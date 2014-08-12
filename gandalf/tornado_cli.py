#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging

try:
    import ujson as json
except ImportError:
    import json


import tornado.gen as gen
import tornado.httpclient

import gandalf.client as client


class AsyncTornadoGandalfClient(client.GandalfClient):
    @gen.coroutine
    def _request(self, *args, **kwargs):
        url = kwargs.pop('url')
        data = kwargs.pop('data', None)
        if data:
            kwargs['body'] = data

        response = yield self.client(url, *args, **kwargs)
        code = self.get_code(response)
        if code != 200:
            body = self.get_body(response).strip()
            raise RuntimeError("Could not retrieve tree. Status: %s. Error: %s" % (code, body))
        raise gen.Return(response)

    def get_code(self, response):
        return response.code

    def get_body(self, response):
        return response.body.decode('utf-8')
