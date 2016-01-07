import os
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
        self.offline_nodes = []

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


    def get_cluster_state(self):
        # TODO: Add timeout handling code if 1st node/ connection goes south...
        self.cluster_state = qumulo.rest.cluster.list_nodes(self.connection, self.credentials).data
        self.offline_nodes = [ s for s in self.cluster_state if s['node_status'] == 'offline' ]


