from pysnmp.entity import engine, config
from pysnmp import debug
from pysnmp.entity.rfc3413 import cmdrsp, context, ntforg
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.smi import builder

import collections
from config import Config
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import os
import re
import smtplib
import threading
import time

from qumulo_client import QumuloClient

#can be useful
# debug.setLogger(debug.Debug('all'))

MibObject = collections.namedtuple('MibObject', ['mibName',
                                   'objectType', 'valueFunc'])

class Mib(object):
    """Stores the data we want to serve.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._test_count = 0
        self._nodes = []
        self._drives = []

    def getTestDescription(self):
        return "My Description"

    def getTestCount(self):
        with self._lock:
            return self._test_count

    def setTestCount(self, value):
        with self._lock:
            self._test_count = value

    def getNodes(self):
        with self._lock:
            return self._nodes

    def setNodes(self, value):
        with self._lock:
            self._nodes = value

    def getDrives(self):
        with self._lock:
            return self._drives

    def setDrives(self, value):
        with self._lock:
            self._drives = value


def createVariable(SuperClass, getValue, *args):
    """This is going to create a instance variable that we can export.
    getValue is a function to call to retreive the value of the scalar
    """
    class Var(SuperClass):
        def readGet(self, name, *args):
            return name, self.syntax.clone(getValue())
    return Var(*args)


class SNMPAgent(object):
    """Implements an Agent that serves the custom MIB and
    can send a trap.
    """

    def __init__(self, mibObjects):
        """
        mibObjects - a list of MibObject tuples that this agent
        will serve
        """

        #each SNMP-based application has an engine
        self._snmpEngine = engine.SnmpEngine()

        #open a UDP socket to listen for snmp requests
        config.addSocketTransport(self._snmpEngine, udp.domainName,
                                  udp.UdpTransport().openServerMode(('', 161)))

        #add a v2 user with the community string public
        config.addV1System(self._snmpEngine, "agent", "public")
        #let anyone accessing 'public' read anything in the subtree below,
        #which is the enterprises subtree that we defined our MIB to be in
        config.addVacmUser(self._snmpEngine, 2, "agent", "noAuthNoPriv",
                           readSubTree=(1,3,6,1,4,1))

        #each app has one or more contexts
        self._snmpContext = context.SnmpContext(self._snmpEngine)

        #the builder is used to load mibs. tell it to look in the
        #current directory for our new MIB. We'll also use it to
        #export our symbols later
        mibBuilder = self._snmpContext.getMibInstrum().getMibBuilder()
        mibSources = mibBuilder.getMibSources() + (builder.DirMibSource('.'),)
        mibBuilder.setMibSources(*mibSources)

        #our variables will subclass this since we only have scalar types
        #can't load this type directly, need to import it
        MibScalarInstance, = mibBuilder.importSymbols('SNMPv2-SMI',
                                                      'MibScalarInstance')
        #export our custom mib
        for mibObject in mibObjects:
            nextVar, = mibBuilder.importSymbols(mibObject.mibName,
                                                mibObject.objectType)
            instance = createVariable(MibScalarInstance,
                                      mibObject.valueFunc,
                                      nextVar.name, (0,),
                                      nextVar.syntax)
            #need to export as <var name>Instance
            instanceDict = {str(nextVar.name)+"Instance":instance}
            mibBuilder.exportSymbols(mibObject.mibName,
                                     **instanceDict)

        # tell pysnmp to respond to get, getnext, and getbulk
        cmdrsp.GetCommandResponder(self._snmpEngine, self._snmpContext)
        cmdrsp.NextCommandResponder(self._snmpEngine, self._snmpContext)
        cmdrsp.BulkCommandResponder(self._snmpEngine, self._snmpContext)


    def setTrapReceiver(self, host, community):
        """Send traps to the host using community string community
        """
        config.addV1System(self._snmpEngine, 'nms-area', community)
        config.addVacmUser(self._snmpEngine, 2, 'nms-area', 'noAuthNoPriv',
                           notifySubTree=(1,3,6,1,4,1))
        config.addTargetParams(self._snmpEngine,
                               'nms-creds', 'nms-area', 'noAuthNoPriv', 1)
        config.addTargetAddr(self._snmpEngine, 'my-nms', udp.domainName,
                             (host, 162), 'nms-creds',
                             tagList='all-my-managers')
        #set last parameter to 'notification' to have it send
        #informs rather than unacknowledged traps
        config.addNotificationTarget(
            self._snmpEngine, 'test-notification', 'my-filter',
            'all-my-managers', 'trap')


    def sendTrap(self, notification, trap_name, var_binds):
        ntfOrg = ntforg.NotificationOriginator(self._snmpContext)

        errorIndication = ntfOrg.sendNotification(
            self._snmpEngine,
            'test-notification',
            ( 'QUMULO-MIB', trap_name ), var_binds)


    def serve_forever(self):
        print "Starting agent"
        self._snmpEngine.transportDispatcher.jobStarted(1)
        try:
           self._snmpEngine.transportDispatcher.runDispatcher()
        except:
            self._snmpEngine.transportDispatcher.closeDispatcher()
            raise

class Worker(threading.Thread):
    """Just to demonstrate updating the MIB
    and sending traps
    """

    def __init__(self, agent, mib, cfg):
        threading.Thread.__init__(self)
        self._agent = agent
        self._mib = mib
        self._cfg = cfg
        self.setDaemon(True)

        self.client = QumuloClient(cfg.clusters[0])  # only one cluster for now
        self.notified_offline = False
        self.notified_dead_drives = False
        # Use an array of dictionaries to track per-node power supply states
        self.notified_power_supply_failure = [{'PS1':False, 'PS2':False} for node in cfg.clusters[0].ipmi.ipmi_servers]
        print self.notified_power_supply_failure

        self.snmp_enabled = cfg.snmp.enabled
        self.email_enabled = cfg.email.enabled
        self.ipmi_enabled = cfg.clusters[0].ipmi.enabled

        if self.email_enabled:
           self.email_acct = os.getenv('SNMP_AGENT_EMAIL_ACCT')
           self.email_pwd = os.getenv('SNMP_AGENT_EMAIL_PWD')

    def check_nodes(self):
        self.client.get_cluster_state()
        if len(self.client.offline_nodes) > 0:

            if self.notified_offline == False:
               msg = "There are currently " + str(len(self.client.offline_nodes)) + \
                  " nodes offline:"

               for n in self.client.offline_nodes:
                   msg = msg +  "\tNode " + n["node_name"] + " is currently offline."

               self.notify("Qumulo Nodes Offline", msg, "nodeDownTrap")
               self.notified_offline = True
        else:
            if self.notified_offline == True:
                self.notified_offline = False
                self.notify("Qumulo Nodes Back Online", "All nodes back online", "nodesClearTrap")

    def check_drives(self):
        self.client.get_drive_states()
        if len(self.client.dead_drives) > 0:

            if self.notified_dead_drives == False:
                msg = "There are currently " + str(len(self.client.dead_drives)) + " drives offline:"

                for d in self.client.dead_drives:
                    msg = msg + "\t" + d["disk_type"] + " Drive" + d["id"] + " is offline."

                self.notify("Qumulo Drives Offline", msg, "driveFailureTrap")
                self.notified_dead_drives = True

        else:
            if self.notified_dead_drives == True:
                self.notified_dead_drives = False
                self.notify("Qumulo Drives Back Online", "All nodes back online", "nodesClearTrap")

    def check_power(self, ipmi_server, node_id):
        power_states = self.client.get_power_state(ipmi_server)

        # notify on every failed supply we find and set appropriate notified states to True
        for PS in power_states['FAIL']:
            if not self.notified_power_supply_failure[node_id][PS]:
                message = PS + " in node " + str(node_id + 1) + " failed"
                self.notify("Qumulo Power Supply Failure", message, "powerSupplyFailureTrap")
                self.notified_power_supply_failure[node_id][PS] = True

        # notify on every good supply we find and set those notified states to False
        for PS in power_states['GOOD']:
            if self.notified_power_supply_failure[node_id][PS]:
                message = PS + " in node " + node_id + " power back to normal"
                self.notify("Qumulo Power Supply Normal", message, "nodesClearTrap")
                self.notified_power_supply_failure[node_id][PS] = False

        # m = re.search("Failure", power_state[0])
        # if m:
        #     if not self.notified_power_supply_failure:
        #         self.notify("Qumulo Power Supply Failure", power_state[0], "powerSupplyFailureTrap")
        #         self.notified_power_supply_failure = True
        # else:
        #     if self.notified_power_supply_failure: # we're back to normal
        #         self.notified_power_supply_failure = False
        #         self.notify("Qumulo Cluster Back Online", "Qumulo Cluster power back to normal", "nodesClearTrap")

    def notify(self, subject, message, snmp_trap_name = None):

        print(message)

        if self.snmp_enabled:
            print("Sending trap")
            self._agent.sendTrap(message, snmp_trap_name, ())

        if self.email_enabled:
            print("Sending email")
            self.send_email(subject, message)


    def check_cluster_status(self):

        # Check IPMI
        if self._cfg.clusters[0].ipmi.enabled:
            ipmi_servers = self._cfg.clusters[0].ipmi.ipmi_servers
            print ipmi_servers
            for ipmi_server in ipmi_servers:
                self.check_power(ipmi_server, node_id=list(ipmi_servers).index(ipmi_server))

        if self.client.credentials != None:
            self.check_nodes()
            self.check_drives()
        else: # we're offline
            if not self.notified_offline:
                print "Error connecting to Qumulo Cluster REST Server"
                self.notify("Qumulo Cluster offline", "Error connecting to Qumulo Cluster REST Server", "nodeDownTrap")
                self.notified_offline = True
            else: # retry login
                self.client.login()


    def send_email(self, subject, body):
        '''Send an email message to a list of recipients'''
        try:
            # Create a text/plain message
            msg = MIMEMultipart()
            msg['From'] = self._cfg.email.address_from
            msg['To'] = self._cfg.email.address_to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self._cfg.email.server, self._cfg.email.tls_port)
            server.starttls()
            server.login(self.email_acct, self.email_pwd)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            server.quit()


        except Exception, excpt:
            print("Failed to send email (Subject: %s) (%s)" %
                    (subject, excpt))


    def run(self):
        while True:
            time.sleep(5)
            self._mib.setTestCount(mib.getTestCount()+1)
            self.check_cluster_status()

if __name__ == '__main__':

    # see if we can read config
    f = file('snmp_agent.cfg')
    cfg = Config(f)

    mib = Mib()
    objects = [MibObject('QUMULO-MIB', 'testDescription', mib.getTestDescription),
                MibObject('QUMULO-MIB', 'testCount', mib.getTestCount)]
    agent = SNMPAgent(objects)

    if cfg.snmp.enabled:
        agent.setTrapReceiver(cfg.snmp.snmp_trap_receiver, 'traps')

    Worker(agent, mib, cfg).start()
    try:
        agent.serve_forever()
    except KeyboardInterrupt:
         print "Shutting down"