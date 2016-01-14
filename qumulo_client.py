import errno
import os
from socket import error as socket_error
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
        self.password = os.getenv('SNMP_AGENT_REST_PWD', 'admin')
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
                    self.connection, None, self.user, self.password)

            self.credentials = qumulo.lib.auth.Credentials.\
                    from_login_response(login_results)
        except Exception, excpt:
            print "Error connecting to the REST server: %s" % excpt
            print __doc__
            sys.exit(1)


    def get_api_response(self, api_call):

        attempt = 0
        resp_obj = None
        retry = True
        max_attempts = 10
        response = None

        while retry and (attempt <= max_attempts):
            try:
                response_object = api_call(self.connection, self.credentials)
                if len(response_object) == 0:
                    retry = True
                else:
                    retry = False
            except socket_error as serr:
                if serr.errno != errno.ECONNREFUSED:
                    raise serr
                else:
                    retry = True

            if retry:
                attempt += 1
                time.sleep(5)

        return response_object.data


    def get_cluster_state(self):
        self.cluster_state = self.get_api_response(qumulo.rest.cluster.list_nodes)
        self.offline_nodes = [ s for s in self.cluster_state if s['node_status'] == 'offline' ]

    def get_drive_states(self):
        self.drive_states = self.get_api_response(qumulo.rest.cluster.get_cluster_slots_status)
        self.dead_drives = [ d for d in self.drive_states if d['state'] == 'dead' ]


