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

    HEADERS = {'Content-type': 'application/json'}

    SESSION_URI = 'session/'

    def __init__(self, base_url, session_id=None):
        self.base_url = '{0}{1}'.format(
            base_url,
            ('' if base_url[-1] == '/' else '/'))

        if not session_id:
            session_id = self.get_session()
        self.session_id = session_id

    def get_session(self):
        """
        Creates a new session on publicator server
        """
        url = '{0}{1}'.format(self.base_url, self.SESSION_URI)
        logger.debug('Going to server %s to create a session', url)
        response = requests.get(url, headers=self.HEADERS)
        response.raise_for_status()
        result = response.json()
        logger.debug('Session has response %s', result)
        return result['session']

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
