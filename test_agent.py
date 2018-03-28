# System under test
import agent as testagent

from StringIO import StringIO

from config import Config
from unittest import TestCase
from mock import patch

test_config = """# we only support one cluster for now
clusters:
[
    {
      name: "clustername"
      port:8000
      retries:10
      retry_delay:10
      # use persistent IP addresses instead of floating here
      # listing them in node order is helpful
      nodes: [ "10.220.200.1",
               "10.220.200.2",
               ]
      # If your cluster has IPMI enabled and you have
      # ipmitool installed on the box running this agent,
      # set this flag to true
      ipmi: {
        enabled: True
        # IPMI address order should match the order of the nodes above
        ipmi_servers: [ "10.10.10.1",
                        "10.10.10.2",
                        ]
      }

    }
]

# Specify IP address of SNMP trap receiver
snmp: {
    enabled: True
    snmp_trap_receiver: '192.168.11.1'
}

# If email is enabled, you will need to set
# environment variables where you are running the
# agent to specify the account and password to
# authorize email access:
#
#    SNMP_AGENT_EMAIL_ACCT
#    SNMP_AGENT_EMAIL_PWD
#
email: {
    enabled: True
    server: "smtp.gmail.com"
    tls_port:587
    ssl_port:465
    address_from: "some.user@gmail.com"
    address_to: "some_nms@yourcompany.com"
}
"""


class TestAgent(TestCase):
    @patch('qumulo_client.QumuloClient.login')
    @patch('pysnmp.carrier.asynsock.dgram.udp.UdpTransport.openServerMode')
    @patch('pysnmp.entity.config.addSocketTransport')
    def test_check_power_no_ipmi(self, MockAddSocketTransport, MockOpenServerMode, MockQClogin):
        """Test that lack of ipmi connectivity warns, but does not break"""
        test_cfg_file = StringIO(test_config)

        MockAddSocketTransport.return_value = None
        MockOpenServerMode.return_value = None
        MockQClogin.return_value = None
        cfg = Config(test_cfg_file)

        mib = testagent.Mib()
        objects = [
            testagent.MibObject('QUMULO-MIB', 'testDescription', mib.getTestDescription),
            testagent.MibObject('QUMULO-MIB', 'testCount', mib.getTestCount)]
        agent = testagent.SNMPAgent(objects)

        if cfg.snmp.enabled:
            agent.setTrapReceiver(cfg.snmp.snmp_trap_receiver, 'traps')

        W = testagent.Worker(agent, mib, cfg)
        W.check_power('127.0.0.1', 1)

    @patch('agent.SNMPAgent.sendTrap')
    @patch('qumulo_client.QumuloClient.get_power_state')
    @patch('qumulo_client.QumuloClient.login')
    @patch('pysnmp.carrier.asynsock.dgram.udp.UdpTransport.openServerMode')
    @patch('pysnmp.entity.config.addSocketTransport')
    def test_check_power_good(self, MockAddSocketTransport, MockOpenServerMode, MockQClogin, MockGetPowerState, MockSendTrap):
        """Test that notification of PS recovery does not throw exception"""
        test_cfg_file = StringIO(test_config)

        MockAddSocketTransport.return_value = None
        MockOpenServerMode.return_value = None
        MockQClogin.return_value = None
        MockGetPowerState.return_value = {'GOOD': {'PS1', 'PS2'}, 'FAIL': set()}
        MockSendTrap.return_value = None
        cfg = Config(test_cfg_file)

        mib = testagent.Mib()
        objects = [
            testagent.MibObject('QUMULO-MIB', 'testDescription', mib.getTestDescription),
            testagent.MibObject('QUMULO-MIB', 'testCount', mib.getTestCount)]
        agent = testagent.SNMPAgent(objects)

        if cfg.snmp.enabled:
            agent.setTrapReceiver(cfg.snmp.snmp_trap_receiver, 'traps')

        W = testagent.Worker(agent, mib, cfg)
        W.notified_power_supply_failure[0]['PS1'] = True
        print W.notified_power_supply_failure
        W.check_power('127.0.0.1', 0)
