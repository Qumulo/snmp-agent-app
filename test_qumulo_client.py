# System under test
import qumulo_client

# API
import qumulo

from mock import patch, Mock
from unittest import TestCase

PS_GOOD="""
PS2 Status       | 50h | ok  | 10.1 | Presence detected
PS1 Status       | 51h | ok  | 10.2 | Presence detected
"""

PS1_BAD="""
PS2 Status       | 50h | ok  | 10.1 | Presence detected
PS1 Status       | 51h | ok  | 10.2 | Presence detected, Power Supply AC lost
"""


class TestIpmi(TestCase):
    @patch('qumulo_client.QumuloClient.login')
    def test_get_power_state(self, MockQClogin):
        MockQClogin.return_value = None
        dummy_cfg = DummyConfig()
        QC = qumulo_client.QumuloClient(dummy_cfg)
        target = {'GOOD': {'PS2', 'PS1'}, 'FAIL': set()}
        result = QC.get_power_state('192.168.203.227')
        print result
        self.assertEqual(target, result)

    @patch('qumulo_client.QumuloClient.login')
    def test_get_ipmi_response(self, MockQClogin):
        MockQClogin.return_value = None
        dummy_cfg = DummyConfig()
        ipmi_query = ('sdr', 'type', 'Power Supply')
        QC = qumulo_client.QumuloClient(dummy_cfg)
        result = QC.get_ipmi_response("192.168.203.227", ipmi_query)
        print result
        self.assertIn("PS1 Status", result)
        self.assertIn("Presence detected", result)

    def test_parse_sdr_ps_good(self):
        target = {'GOOD': {'PS1', 'PS2'}, 'FAIL': set()}
        result = qumulo_client.parse_sdr_ps(PS_GOOD)
        self.assertEqual(target, result)

    def test_parse_sdr_ps1_bad(self):
        target = {'GOOD': {'PS2'}, 'FAIL': {'PS1'}}
        result = qumulo_client.parse_sdr_ps(PS1_BAD)
        self.assertEqual(target, result)


class DummyConfig(object):
    def __init__(self):
        self.name = "qumulo"
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

    @patch('qumulo_client.QumuloClient.get_api_response')
    def test_get_cluster_state_response_none(self, MockGetAPIResponse):
        """don't throw a TypeError when get_cluster_state() receives None"""
        MockGetAPIResponse.return_value = None
        dummy_cfg = DummyConfig()
        QC = qumulo_client.QumuloClient(dummy_cfg)
        result = QC.get_cluster_state()
        self.assertIsNone(result)

    @patch('qumulo_client.QumuloClient.get_api_response')
    def test_get_drive_states_response_none(self, MockGetAPIResponse):
        """don't throw a TypeError when get_cluster_state() receives None"""
        MockGetAPIResponse.return_value = None
        dummy_cfg = DummyConfig()
        QC = qumulo_client.QumuloClient(dummy_cfg)
        result = QC.get_drive_states()
        self.assertIsNone(result)

    def test_get_api_response_credentials_timeout(self):
        """instantiate client, blow away credentials, assert api call works"""
        dummy_cfg = DummyConfig()
        QC = qumulo_client.QumuloClient(dummy_cfg)
        # no credentials behave the same way as expired credentials
        QC.credentials = None
        response = QC.get_api_response(qumulo.rest.cluster.list_nodes)
        self.assertIsNotNone(response)
