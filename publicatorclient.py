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
    MESSAGE_URI = 'messages/'

    def __init__(self, base_url):
        self.base_url = '{0}{1}'.format(base_url,
                                        ('' if base_url[-1] == '/' else '/'))
        self.session_id = self.get_session()

    def get_session(self):
        """
        Creates a new session on publicator server
        """
        url = '{0}{1}'.format(self.base_url, self.SESSION_URI)
        logger.debug('Going to server %s to create a session', url)
        response = requests.get(url, headers=self.HEADERS)
        response.raise_for_status()
        result = response.json()
        logger.debug('Session is response=%s', result)
        return result['session']

    def publish(self, channel, msg):
        """
        Publishes a message to given channel
        """
        url = '{0}{1}/{2}{3}/'.format(self.base_url,
                                      self.session_id,
                                      self.MESSAGE_URI,
                                      channel)
        logger.debug('Going to server %s to publish a message', url)

        response = requests.post(url,
                                 data={'message': msg},
                                 headers=self.HEADERS)
        # if response.status_code == 422:
        #     self.session_id = self.get_session()
        # If an error occured create a new session.
        if not response.ok:
            self.session_id = self.get_session()

        response.raise_for_status()
        logger.debug('Message successfully published on channel "%s". '
                     'Response status code is %s (%s)',
                     channel,
                     response.status_code,
                     response.reason)
