import sys
import random
import unittest
import publicatorclient
# global variable that will be used in tests
HOST = []


class TestClient(unittest.TestCase):

    def get_channel_name(self):
        return self.channel_name + str(random.randint(1, 10000000))

    def setUp(self):
        self.host = HOST[0]
        # client = publicatorclient.PublicatorClient(HOST[0])
        # self.channel_name = 'channel_%s' % (random.randint(1, 10000000),)
        self.channel_name = 'integration_test_channel_'

    def test_subscribe(self):
        channel_name = self.get_channel_name()
        client = publicatorclient.PublicatorClient(self.host)
        self.assertTrue(client.subscribe(channel_name))
        self.assertEqual(client.get_subscribtions(),
                         [channel_name])
        self.assertEqual(client.get_consumers(channel_name),
                         [client.session_id])

    def test_publish(self):
        test_msg = 'test_message'
        channel_name = self.get_channel_name()
        client = publicatorclient.PublicatorClient(self.host)
        self.assertTrue(client.subscribe(channel_name))
        self.assertTrue(client.publish(channel_name, test_msg))
        expected_result = [{u'data': test_msg,
                            u'type': u'message',
                            u'channel_code': channel_name}]
        result = client.get_messages()
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    # sys.argv ==  ['integration_tests.py','arg1','arg2', ...]
    HOST.append(sys.argv[1])
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClient)
    unittest.TextTestRunner().run(suite)
