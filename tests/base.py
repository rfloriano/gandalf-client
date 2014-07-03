#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of gandalf-client.
# https://github.com/rfloriano/gandalf-client

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com
import unittest

import tornado.httpclient as http

import derpconf.config as config
import cow.testing as testing
import cow.server as server


class TestServer(server.Server):
    def after_start(self, io_loop):
        self.application.http_client = http.AsyncHTTPClient(io_loop)


class TestCase(unittest.TestCase):

    def get_config(self):
        return dict(
            GANDALF_HOST='localhost',
            GANDALF_PORT=8001,
        )


class AsyncTestCase(testing.CowTestCase, TestCase):

    def get_server(self):
        cfg = config.Config(**self.get_config())
        self.server = TestServer(config=cfg)
        return self.server
