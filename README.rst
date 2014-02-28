publicator-python-client
========================

Python client for publicator.


Running integration test
------------------------

To run integration tests. run 'python manage.py integration_test.py PUBLICATOR_HOST'.
This will try every operation available on python client to make sure that your client is runnging properly with the server. For instance to run integration test with your local server. You could run the following

::

   python manage.py integration_test.py http://localhost:8766
