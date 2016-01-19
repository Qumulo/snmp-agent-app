# Qumulo SNMP Agent Readme

The Qumulo SNMP Agent is an SNMP agent for Qumulo clusters built using [**PySNMP**] (http://pysnmp.sourceforge.net/).  
At present the agent does two things:

1. **Push**: Sends SNMP traps to a Network Management Station (NMS) such as Nagios upon cluster or drive failure (and when cluster returns to normal)
2. **Pull**: Serves up Qumulo-specific MIB to NMSes

To get started we've defined a simplistic SNMP MIB for exposing Qumulo cluster information but we plan on adding 
more information over time (and you can fork the project to add more if desired). 

**NOTE** Qumulo SNMP Agent requires **Python Version 2.7**

## Requirements

* Qumulo cluster and API credentials for the cluster
* Linux or Mac with continuous access to the Qumulo cluster
* python and pip


## Installation Steps

### 1. Install the snmp_agent

    git clone https://github.com/Qumulo/snmp_agent.git

Or, download the zip file (https://github.com/Qumulo/snmp_agent/archive/master.zip) and unzip it to your machine where you will be running this tool.

### 2. Install Prequisites

We currently support Linux or MacOSX for running the Qumulo SNMP Agent. In some cases, the following commands may show warnings when run, however, the required libraries should still be correctly installed.

#### On Linux (Ubuntu)
    sudo apt-get install python-pip

#### On Mac OSX
    sudo easy_install pip

### 3. Install the prerequisite python libraries

Just run

    pip install -r requirements.txt

from the snmp_agent install folder to install the python prerequisites including the Qumulo REST API
wrapper.  *NOTE* that the snmp_agent sample requires Qumulo REST API version 1.2.19 or later.

### 4. Edit the configuration file
Edit **snmp_agent.config**

In the config file you specify the IP addresses of your cluster nodes and the IP address of the NMS server for traps, like this

    clusters:

    [
        # qumulo-snmp
        { port:8000,
        
          nodes: [ '10.0.0.181',
          
                   '10.0.0.182',
                   
                   '10.0.0.183',
                   
                   '10.0.0.184']}
                   
    ]
    # Specify IP address of SNMP trap receiver

    snmp_trap_receiver: '10.0.0.11'

** NOTE ** that credentials used for accessing the Qumulo cluster via API are determined by two environment variables
that snmp_agent expects to find on start:

SNMP_AGENT_REST_USER
SNMP_AGENT_REST_PWD

If these environment variables are not defined/found at startup, snmp_agent will use 'admin'/'admin' for credentials.


### 5. Testing the Agent

After configuring snmp_agent per above, I test the agent in the following way (there are certainly other ways, but 
this is what I used to test):

1. I start a four node Qumulo cluster (using VMs for testing -- I create four VMs from Qumulo 1.2.19 core ova) with IP addrs corresonding to snmp_agent.cfg

2. In lieu of a NMS such as Nagios, I run [**snmptrapd**] (http://www.net-snmp.org/wiki/index.php/TUT:Configuring_snmptrapd)
to listen for SNMP traps from my agent.  I start it using sudo (in order to have network privileges for my app which
is using UDP for SNMP traffic) in the folder where snmp_agent is installed, as follows:

    sudo snmptrapd -f -Lo -c snmptrapd.conf

3. I then start then agent (also using sudo, making sure I'm in a python 2.7 environment with all supporting packages
installed via pip):

    sudo python agent.py

4. To test the agent, I fail a node in a cluster and bring it back, and then fail a drive in a node and bring it back, 
verifying that the appropriate traps are sent on node and drive failure and when they are restored.  For testing, I fail
a cluster by pausing one of the node VMs, ensuring the node failure trap is sent and received by snmptrapd, then I use
an internal Qumulo testing tool to fail a drive on one of the four node VMs and then bring it back.  For the drive
failure there may be other ways besides our internal tool to fail and restore the drive but I will look into alternatives
and sharing them.


