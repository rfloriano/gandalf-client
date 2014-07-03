.. gandalf-client documentation master file, created by
   sphinx-quickstart on Tue Jul  1 11:11:08 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

gandalf-client - a client for gandalf
========================================

gandalf-client is a client for gandalf (https://github.com/tsuru/gandalf).

.. image:: https://travis-ci.org/rfloriano/gandalf-client.svg?branch=master
    :target: https://travis-ci.org/rfloriano/gandalf-client

.. image:: https://coveralls.io/repos/rfloriano/gandalf-client/badge.png
  :target: https://coveralls.io/r/rfloriano/gandalf-client


Getting Started
---------------

Installing gandalf-client is as simple as::

   $ pip install gandalf-client

After you have it installed, let's use the gandalf, then:

.. testcode:: getting_started

   import requests
   from gandalf.client import GandalfClient

   gandalf = GandalfClient("localhost", 8001, requests.request)
   gandalf.user_new('rfloriano', {'my-ssh-key': 'content-of-my-ssh-public-key'})

.. toctree::
   :maxdepth: 2

   methods

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

