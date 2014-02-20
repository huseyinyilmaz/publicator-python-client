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

    def _send_msg(self, msg):
        url = '{0}{1}/http/'.format(self.base_url,
                                    self.session_id)
        logger.debug('Send a message to %s message %s', url, msg)

        response = requests.post(url,
                                 data=json.dumps(msg),
                                 headers=self.HEADERS)
        logger.debug('message successfully sent to %s message=%s', url, msg)
        response.raise_for_status()
        result = response.json()
        if result['type'] == 'error' \
                and result['data'] == 'consumer_not_found':
            logger.warning('Session is dead. Creating a new session')
            self.session_id = self.get_session()
            result = self._send_msg(msg)
        return result

    def publish(self, channel, msg):
        """
        Publishes a message to given channel
        """

        msg_to_send = {'type': 'publish',
                       'data': {'channel_code': channel,
                                'message': msg}}

        return self._send_msg(msg_to_send)

    def subscribe(self, channel, subscribtion_type=MESSAGE_ONLY):
        """
        Subscribes to given channel
        """
        msg_to_send = {'type': 'subscribe',
                       'data': {'channel_code': channel,
                                'type': subscribtion_type}}

        return self._send_msg(msg_to_send)

    def unsubscribe(self, channel):
        """
        Unsubscribes from given channel
        """
        msg_to_send = {'type': 'subscribe',
                       'data': channel}

        return self._send_msg(msg_to_send)

    def get_subscribtions(self):
        """
        Get list of subscribed channel list for current session.
        """
        msg_to_send = {'type': 'get_subscribtions'}

        return self._send_msg(msg_to_send)

    def get_consumers(self, channel):
        """
        Get list of consumer codes for given channel code.
        """
        msg_to_send = {'type': 'get_subscribtions',
                       'data': {'channel_code': channel}}

        return self._send_msg(msg_to_send)
