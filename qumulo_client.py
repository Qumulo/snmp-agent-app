import time
import os
# subprocess is for shelling out to run ipmi commands
import re
import subprocess
import sys

import qumulo.lib.auth
import qumulo.lib.request
import qumulo.rest.fs as fs

class QumuloClient(object):
    ''' class wrapper for REST API cmd so that we can new them up in tests '''
    def __init__(self, cluster_cfg):

        self.port = cluster_cfg.port
        self.nodes = cluster_cfg.nodes
        self.user = os.getenv('SNMP_AGENT_REST_USER', 'admin')
        self.pwd = os.getenv('SNMP_AGENT_REST_PWD', 'admin')
        self.ipmi_user = os.getenv('SNMP_AGENT_IPMI_USER', 'ADMIN')
        self.ipmi_pwd = os.getenv('SNMP_AGENT_IPMI_PWD', 'ADMIN')

        self.connection = None
        self.credentials = None
        self.cluster_state = None
        self.drive_states = None
        self.offline_nodes = []
        self.dead_drives = []

        self.login()

    def login(self):
        try:
            self.connection = qumulo.lib.request.Connection(\
                                self.nodes[0], int(self.port))
            login_results, _ = qumulo.rest.auth.login(\
                    self.connection, None, self.user, self.pwd)

            self.credentials = qumulo.lib.auth.Credentials.\
                    from_login_response(login_results)
        except Exception, excpt:
            # print "Error connecting to the REST server: %s" % excpt
            # sys.exit(1)
            pass


    def get_api_response(self, api_call):

        attempt = 0
        response_object = None
        retry = True

        while retry and (attempt <= 10):
            try:
                response_object = api_call(self.connection, self.credentials)
                if len(response_object) == 0:
                    retry = True
                else:
                    retry = False
            except Exception, excpt:
                retry = True

            if retry:
                attempt += 1
                time.sleep(10)

        return response_object.data


    def get_cluster_state(self):
        self.cluster_state = self.get_api_response(qumulo.rest.cluster.list_nodes)
        self.offline_nodes = [ s for s in self.cluster_state if s['node_status'] == 'offline' ]

    def get_drive_states(self):
        self.drive_states = self.get_api_response(qumulo.rest.cluster.get_cluster_slots_status)
        self.dead_drives = [ d for d in self.drive_states if d['state'] == 'dead' ]

    def get_power_state(self, ipmi_server):
        '''
        use ipmi to determine if any power supplies have failed.
        @return:  TBD data structure
        '''
        ipmi_success = False
        results = []

        try:
            ipmi_cmd = "ipmitool -H " + ipmi_server + " -U " + self.ipmi_user + " -P " + \
                       self.ipmi_pwd + " sel elist"
            ipmi_output = subprocess.check_output(ipmi_cmd.split(" "))
            lines = ipmi_output.split("\n")

            for line in lines:

                m = re.search('Power Supply(.+?)Failure', line)
                if m:
                    results.append(m.group())

        except:
            results = [ "get_power_state: IPMI command exception." ]

        sys.stdout.flush()
        return results



    def get_memory_state(self, ipmi_server):
        '''
        use ipmi to determine if any DIMMs have failed.
        @return:  TBD data structure
        '''
        return []




