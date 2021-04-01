# DEPRECATED: Qumulo SNMP Agent Readme
This repository has been deprecated as it is not well-maintained, tested, and will not be converted to support Python 3.  Since Qumulo will not be supporting Python 2.7 at the end of this quarter, this repository will subsequently be deleted.

[![No Maintenance Intended](http://unmaintained.tech/badge.svg)](http://unmaintained.tech/)

The Qumulo SNMP Agent is an SNMP agent for Qumulo clusters built using [PySNMP](http://pysnmp.sourceforge.net/).

At present the agent does two things:

1. **Push**: Sends SNMP traps to a Network Management Station (NMS) such as Nagios upon cluster or drive failure (and when cluster returns to normal)
2. **Pull**: Serves up Qumulo-specific MIB to NMSes

To get started we've defined a simple, flat SNMP MIB for exposing Qumulo cluster information. We plan on adding 
more information over time. Of course, you can fork the project to add more if desired! 

**NOTE**: Qumulo SNMP Agent requires **Python Version 2.7**

## Requirements

* Qumulo cluster and API credentials for the cluster
* Linux or Mac with continuous access to the Qumulo cluster
* python and pip
* ipmitool (Homebrew can provide this on Mac OS X)


## Installation Steps

### 1. Install the snmp_agent

    git clone https://github.com/Qumulo/snmp-agent-app.git

Or, download the zip file (https://github.com/Qumulo/snmp-agent-app/archive/master.zip) and unzip it to your machine where you will be running this tool.

### 2. Install Prequisites

We currently support Linux or MacOSX for running the Qumulo SNMP Agent. In some cases, the following commands may show warnings when run, however, the required libraries should still be correctly installed.

#### On Linux (Ubuntu)
    sudo apt-get install python-pip

#### On Mac OSX
    sudo easy_install pip

### 3. Install the prerequisite python libraries

Just run

    pip install -r requirements.txt

from the snmp_agent install folder to install the Python prerequisites including the Qumulo REST API
wrapper.  *NOTE* that the snmp_agent sample requires Qumulo REST API version 2.7.5 or later.

### 4. Install ipmitool

`ipmitool` is used to get power supply states and communicate with nodes that are powered off.

#### On Linux (Ubuntu)
    sudo apt-get install ipmitool

#### On Mac OSX
    brew install ipmitool

*NOTE* that [Homebrew](https://brew.sh) must be installed to install `ipmitool` on Mac OS X. There are other methods but this agent is tested against the Homebrew-provided
version of `ipmitool`.


### 5. Copy the configuration template and edit the configuration file
Copy **snmp_agent.cfg.template** to **snmp_agent.cfg**
    `cp snmp_agent.cfg.template snmp_agent.cfg`

Edit **snmp_agent.cfg**

In the config file you specify:

1. IP addresses of your cluster nodes:
```python
clusters:
[
    {
      name: "qumulo"
      port:8000
      # use persistent IP addresses instead of floating here
      # listing them in node order is helpful
      nodes: [ "10.220.200.1",
               "10.220.200.2",
               "10.220.200.3",
               "10.220.200.4",
               "10.220.200.5",
               "10.220.200.6",
               ]
```

2. IP addresses of the IPMI addresses on your cluster nodes. Please note that these should be in the same order as the node list above,
or snmp_agent might report the wrong node numbers when sending alerts about power supplies!
```python
      # If your cluster has IPMI enabled and you have
      # ipmitool installed on the box running this agent,
      # set this flag to true
      ipmi: {
        enabled: True
        # IPMI address order should match the order of the nodes above
        ipmi_servers: [ "192.168.203.227",
                        "192.168.203.223",
                        "192.168.203.226",
                        "192.168.203.222",
                        "192.168.203.220",
                        "192.168.203.219",
                        ]
      }

    }
]
```

3. IP address of an SNMP trap receiver
```python
    # Specify IP address of SNMP trap receiver
    snmp: {
        enabled: True
        snmp_trap_receiver: '10.20.217.205'
    }
```

4. SMTP information
```python
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
        address_from: "your_account_on@gmail.com"
        address_to: "other_account_on@gmail.com"
    }
```

** NOTE ** that credentials used for accessing the Qumulo cluster via API are determined by two environment variables
that snmp_agent expects to find on start:

    SNMP_AGENT_REST_USER
    SNMP_AGENT_REST_PWD

If these environment variables are not defined/found at startup, snmp_agent will use 'admin'/'admin' for credentials.

In addition, if your configuration has email enabled for notifications, you will need to define
environment vars for the email account and password to use to send mail:

    SNMP_AGENT_EMAIL_ACCT
    SNMP_AGENT_EMAIL_PWD
    
** NOTE that if you are using Gmail (and potentially other services) you will need to
allow less secure apps (credential as well as token-based) to access your email server
as described here: http://goo.gl/RXkKGU

### 6. Testing the Agent

After configuring `snmp_agent` per above against a running Qumulo cluster, one can test the agent in the following way:

1. In lieu of a NMS such as Nagios, one can configure and run [snmptrapd](http://www.net-snmp.org/wiki/index.php/TUT:Configuring_snmptrapd)
to listen for SNMP traps from the agent.  Start it using sudo in the folder where snmp_agent is installed, as follows:

    ```bash
    sudo snmptrapd -f -Lo -c snmptrapd.conf
    ```

2. I then start then agent (also using sudo, making sure I'm in a python 2.7 environment with all supporting packages
installed via pip):

    ```bash
    sudo -E python agent.py
    ```
    
** NOTE that the -E is important so that the python app picks up your env vars for
SNMP_AGENT_REST_USER and the others.

3. To test the agent, I fail a node in a cluster and bring it back, and then fail a drive in a node and bring it back, 
verifying that the appropriate traps are sent on node and drive failure and when they are restored.

### 7. Modifying the MIB / adding values etc.
PySNMP needs a "pythonized" MIB.  To generate:


    ```bash
    mibdump.py  --destination-directory=. ./QUMULO-MIB
    ```

