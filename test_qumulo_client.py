# System under test
import qumulo_client

# API
import qumulo

from mock import patch, Mock
from unittest import TestCase


SEL_AC_GOOD = \
"""   1 | 02/28/2018 | 06:25:18 | Event Logging Disabled System Event Log | Log area reset/cleared | Asserted
   2 | 03/01/2018 | 19:23:13 | Power Supply PS1 Status | Power Supply AC lost | Deasserted
   3 | 03/01/2018 | 19:24:21 | Power Supply PS1 Status | Power Supply AC lost | Asserted
   4 | 03/01/2018 | 19:24:56 | Power Supply PS1 Status | Power Supply AC lost | Deasserted"""

SEL_AC_FAILED = \
"""   1 | 02/28/2018 | 06:25:18 | Event Logging Disabled System Event Log | Log area reset/cleared | Asserted
   2 | 03/01/2018 | 19:23:13 | Power Supply PS1 Status | Power Supply AC lost | Deasserted
   3 | 03/01/2018 | 19:24:21 | Power Supply PS1 Status | Power Supply AC lost | Asserted"""

SEL_SUPPLY_FAILED = \
"""   1 | 01/14/2015 | 04:00:23 | Physical Security Chassis Intru | General Chassis intrusion () | Asserted
   2 | 01/14/2015 | 05:49:18 | Physical Security Chassis Intru | General Chassis intrusion () | Asserted
   3 | 01/14/2015 | 09:39:19 | Power Supply PS1 Status | Failure detected () | Asserted
   4 | 01/14/2015 | 09:39:53 | Power Supply PS1 Status | Failure detected () | Deasserted
   5 | 01/14/2015 | 09:44:22 | Power Supply PS2 Status | Failure detected () | Asserted
   6 | 01/14/2015 | 09:45:08 | Power Supply PS2 Status | Failure detected () | Deasserted
   7 | 02/02/2015 | 22:35:13 | Physical Security Chassis Intru | General Chassis intrusion () | Asserted
   8 | 02/12/2015 | 17:57:38 | Physical Security Chassis Intru | General Chassis intrusion () | Asserted
   9 | 02/12/2015 | 17:57:41 | Power Supply PS2 Status | Failure detected () | Asserted
   a | 02/12/2015 | 21:53:46 | Power Supply PS2 Status | Failure detected () | Deasserted
   b | 03/16/2015 | 23:28:06 | Physical Security Chassis Intru | General Chassis intrusion () | Asserted
   c | 03/16/2015 | 23:28:09 | Power Supply PS2 Status | Failure detected () | Asserted
   d | 03/16/2015 | 23:30:18 | Power Supply PS2 Status | Failure detected () | Deasserted
   e | 03/21/2015 | 12:42:39 | Power Supply PS2 Status | Failure detected () | Asserted
   f | 03/21/2015 | 17:37:31 | Physical Security Chassis Intru | General Chassis intrusion () | Asserted
  10 | 05/23/2015 | 00:47:09 | Physical Security Chassis Intru | General Chassis intrusion () | Asserted
  11 | 12/17/2017 | 07:04:29 | Physical Security Chassis Intru | General Chassis intrusion () | Asserted
  12 | 12/17/2017 | 07:04:32 | Power Supply PS1 Status | Failure detected () | Asserted
  13 | 12/17/2017 | 07:08:27 | Power Supply PS1 Status | Failure detected () | Deasserted
  14 | 01/15/2018 | 22:21:39 | Physical Security Chassis Intru | General Chassis intrusion () | Asserted
  15 | 02/01/2018 | 22:21:50 | Session Audit #0xff |  | Asserted"""

SEL_SUPPLY_GOOD = \
"""   1 | 10/28/2014 | 08:28:21 | Power Supply PS1 Status | Failure detected () | Asserted
   2 | 10/28/2014 | 08:28:21 | Power Supply PS2 Status | Failure detected () | Asserted
   3 | 10/28/2014 | 08:29:22 | Unknown #0xc4 |  | Asserted
   4 | 10/29/2014 | 02:17:49 | Power Supply PS1 Status | Failure detected () | Asserted
   5 | 10/29/2014 | 02:18:31 | Power Supply PS1 Status | Failure detected () | Deasserted
   6 | 10/29/2014 | 02:20:52 | Power Supply PS2 Status | Failure detected () | Asserted
   7 | 10/29/2014 | 02:21:43 | Power Supply PS2 Status | Failure detected () | Deasserted
   8 | 12/03/2014 | 17:08:42 | Power Supply PS1 Status | Failure detected () | Asserted
   9 | 12/04/2014 | 15:15:11 | Power Supply PS1 Status | Failure detected () | Asserted
   a | 12/05/2014 | 18:18:54 | Power Supply PS1 Status | Failure detected () | Asserted
   b | 12/11/2014 | 18:41:19 | Power Supply PS1 Status | Failure detected () | Asserted
   c | 01/09/2015 | 18:30:32 | Power Supply PS1 Status | Failure detected () | Asserted
   d | 01/20/2015 | 22:14:29 | Power Supply PS1 Status | Failure detected () | Asserted
   e | 01/21/2015 | 18:41:57 | Power Supply PS1 Status | Failure detected () | Asserted
   f | 01/23/2015 | 23:07:16 | Power Supply PS1 Status | Failure detected () | Asserted
  10 | 02/02/2015 | 22:32:29 | Power Supply PS1 Status | Failure detected () | Asserted
  11 | 02/16/2015 | 19:08:47 | Power Supply PS1 Status | Failure detected () | Deasserted
  12 | 03/16/2015 | 23:25:20 | Power Supply PS2 Status | Failure detected () | Asserted
  13 | 03/16/2015 | 23:27:42 | Power Supply PS2 Status | Failure detected () | Deasserted
  14 | 04/21/2015 | 00:52:46 | Power Supply PS1 Status | Failure detected () | Asserted
  15 | 05/12/2015 | 03:01:53 | Power Supply PS1 Status | Failure detected () | Deasserted
  16 | 05/12/2015 | 03:02:09 | Power Supply PS2 Status | Failure detected () | Asserted
  17 | 05/12/2015 | 03:02:24 | Power Supply PS2 Status | Failure detected () | Deasserted
  18 | 04/16/2016 | 00:31:40 | Power Supply PS1 Status | Failure detected () | Asserted
  19 | 12/17/2017 | 07:01:53 | Power Supply PS1 Status | Failure detected () | Asserted
  1a | 12/17/2017 | 20:49:35 | Power Supply PS1 Status | Failure detected () | Deasserted"""


class TestSelParsing(TestCase):
    def test_parse_sel_elist_ac_healthy(self):
        result = qumulo_client.parse_sel(SEL_AC_GOOD)
        target = {'GOOD': {'PS1','PS2'}, 'FAIL': set()}
        self.assertEqual(result, target)

    def test_parse_sel_elist_ac_failed(self):
        result = qumulo_client.parse_sel(SEL_AC_FAILED)
        target = {'GOOD': {'PS2'}, 'FAIL': {'PS1'}}
        self.assertEqual(result, target)

    def test_parse_sel_elist_ps_healthy(self):
        result = qumulo_client.parse_sel(SEL_SUPPLY_GOOD)
        target = {'GOOD': {'PS1','PS2'}, 'FAIL': set()}
        self.assertEqual(result, target)

    def test_parse_sel_elist_ps_failed(self):
        result = qumulo_client.parse_sel(SEL_SUPPLY_FAILED)
        target = {'GOOD': {'PS1'}, 'FAIL': {'PS2'}}
        self.assertEqual(result, target)


class DummyConfig(object):
    def __init__(self):
        self.port = 8000
        self.nodes = ["10.220.200.1", "10.220.200.2", ]
        self.retries = 10
        self.retry_delay = 0.1


class TestRestClient(TestCase):
    @patch('qumulo_client.QumuloClient.login')
    @patch('qumulo.rest.cluster.get_cluster_slots_status')
    @patch('qumulo.rest.cluster.list_nodes')
    def test_get_api_response_none(self, MockListNodes, MockGetClusterSlotsStatus, MockQClogin):
        MockListNodes.return_value = None
        MockGetClusterSlotsStatus.return_value = None
        MockQClogin.return_value = None
        dummy_cfg = DummyConfig()
        QC = qumulo_client.QumuloClient(dummy_cfg)
        result = QC.get_api_response(qumulo.rest.cluster.list_nodes)
        self.assertIsNone(result)
