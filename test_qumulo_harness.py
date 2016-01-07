import time

from config import Config
from qumulo_client import QumuloClient

if __name__ == '__main__':

    # see if we can read config
    f = file('snmp_agent.cfg')
    cfg = Config(f)
    client = QumuloClient(cfg.clusters[0]) # only one cluster for now
    notified_offline = False

    while True:
        time.sleep(3)
        client.get_cluster_state()
        if len(client.offline_nodes) > 0:
            notified_offline = True
            print "There are currently " + str(len(client.offline_nodes)) + " nodes offline:"
            for n in client.offline_nodes:
                print "\tNode " + n["node_name"] + " is currently offline."
        else:
            if notified_offline == True:
                notified_offline = False
                print "All nodes back online."
