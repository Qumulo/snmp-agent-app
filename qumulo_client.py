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
        self.retries = cluster_cfg.retries
        self.retry_delay = cluster_cfg.retry_delay
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
            self.get_credentials()
        except Exception, excpt:
            print "Problem connecting to the REST server: %s" % excpt
            if 'certificate verify failed' not in str(excpt):
                print "Fatal error, exiting..."
                sys.exit(1)
            else:
                # Create an unverified ssl context, warn that we're doing it
                print "Warning: Creating unverified HTTPS Context!"
                import ssl
                try:
                    _create_unverified_https_context = ssl._create_unverified_context
                except AttributeError:
                    # Legacy Python that doesn't verify by default
                    pass
                else:
                    # Handle envs that don't support HTTPS verification
                    ssl._create_default_https_context = _create_unverified_https_context

                self.get_credentials()

    def get_credentials(self):
        self.connection = qumulo.lib.request.Connection(
            self.nodes[0], int(self.port))
        login_results, _ = qumulo.rest.auth.login(
            self.connection, None, self.user, self.pwd)

        self.credentials = qumulo.lib.auth.Credentials.from_login_response(login_results)

    def get_api_response(self, api_call):

        attempt = 0
        response_object = None
        retry = True

        while retry and (attempt <= self.retries):
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
                time.sleep(self.retry_delay)

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
        # TODO: Say something useful if ipmi doesn't work

        try:
            ipmi_cmd = "ipmitool -H " + ipmi_server + " -U " + self.ipmi_user + " -P " + \
                       self.ipmi_pwd + " sel elist"
            ipmi_output = subprocess.check_output(ipmi_cmd.split(" "),
                                                  stderr=subprocess.STDOUT)
            results = parse_sel(ipmi_output)

        except Exception, e:
            results = ["get_power_state: IPMI command exception: " + str(e)]

        sys.stdout.flush()
        return results


def parse_sel(text):
    lines = text.split('\n')
    PS = {'PS1', 'PS2'}
    GOOD = set()
    FAIL = set()
    # use sets for comparison because order can change based on SEL order
    # assume both power supplies are good unless we find otherwise
    results = {'GOOD': {'PS1', 'PS2'}, 'FAIL': set()}
    for line in reversed(lines):
        m = re.search(
            r'Power Supply (.+?) Status \| (?:Failure detected \(\)|Power Supply AC lost) \| (Asserted|Deasserted)',
            line
        )
        if m and m.group(1) in PS:
            if m.group(2) == "Asserted":
                FAIL.add(m.group(1))
            elif m.group(2) == "Deasserted":
                GOOD.add(m.group(1))
            else:
                raise Exception(
                    "Received abnormal PS status from ipmitool"
                )
            PS.remove(m.group(1))
            if not PS:  # we've found states for all power supplies, bail
                break
    # if we didn't find anything in the SEL dont mess with results dict
    GOOD.update(PS)
    if GOOD:
        results['GOOD'] = GOOD
    if FAIL:
        results['FAIL'] = FAIL
    return results
