import json
import logging

import requests

logger = logging.getLogger(__name__)

# if there is no handler run this code
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)


class PublicatorClientException(Exception):
    """
    Base Exception that publicator client raises
    """
    pass


class PublicatorClient(object):
    """
    Client objects that communicates with publicator server.
    """

    ALL = 'all'
    MESSAGE_ONLY = 'message_only'
    HEADERS = {'Content-type': 'application/json'}

    SESSION_URI = 'session/'

    def __init__(self, base_url, session_id=None, auth_info=None):
        self.base_url = '{0}{1}'.format(
            base_url,
            ('' if base_url[-1] == '/' else '/'))
        self.auth_info = auth_info
        if not session_id:
            session_id = self.get_session(auth_info)
        self.session_id = session_id

    def get_session(self, auth_info):
        """
        Creates a new session on publicator server
        """
        url = '{0}{1}'.format(self.base_url, self.SESSION_URI)
        data = {'auth_info': auth_info}
        logger.debug('Going to server %s to create a session with data %s',
                     url, data)
        response = requests.post(url,
                                 headers=self.HEADERS,
                                 data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        logger.debug('Session has response %s', result)
        return result['data']

    def _send_msg(self, msg, expected_return_type):
        url = '{0}{1}/http/'.format(self.base_url,
                                    self.session_id)
        logger.debug('Send a message to %s message %s', url, msg)

        response = requests.post(url,
                                 data=json.dumps(msg),
                                 headers=self.HEADERS)
        logger.debug('message successfully sent')
        response.raise_for_status()
        result = response.json()
        logger.debug('response_text = %s' % (result,))
        if result.get('type') == 'error' \
                and result.get('data') == 'consumer_not_found':
            logger.warning('Session is dead. Creating a new session')
            self.session_id = self.get_session(self.auth_info)
            result = self._send_msg(msg)

        if result.get('type') != expected_return_type:
            raise PublicatorClientException(
                'Return type %s does not match with expected type %s' %
                (result.get('type'), expected_return_type))
        return result

    def publish(self, channel, msg):
        """
        Publishes a message to given channel
        """

        msg_to_send = {'type': 'publish',
                       'data': {'channel_code': channel,
                                'message': msg}}

        return self._send_msg(msg_to_send, 'response')

    def subscribe(self, channel, subscribtion_type=MESSAGE_ONLY):
        """
        Subscribes to given channel
        """
        msg_to_send = {'type': 'subscribe',
                       'data': {'channel_code': channel,
                                'type': subscribtion_type}}
        result = self._send_msg(msg_to_send, 'subscribed')

        return {u'data': channel, u'type': u'subscribed'} == result

    def unsubscribe(self, channel):
        """
        Unsubscribes from given channel
        """
        msg_to_send = {'type': 'unsubscribe',
                       'data': channel}

        result = self._send_msg(msg_to_send, 'unsubscribed')
        return True

    def get_subscribtions(self):
        """
        Get list of subscribed channel list for current session.
        """
        msg_to_send = {'type': 'get_subscribtions'}
        result = self._send_msg(msg_to_send, 'subscribtions')
        return result['data']

    def get_consumers(self, channel):
        """
        Get list of consumer codes for given channel code.
        """
        msg_to_send = {'type': 'get_consumers',
                       'data': {'channel_code': channel}}
        result = self._send_msg(msg_to_send, 'consumers')
        return result['data']
