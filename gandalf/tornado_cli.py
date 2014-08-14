#!/usr/bin/python
# -*- coding: utf-8 -*-
import tornado.gen as gen
import tornado.httpclient as httpclient

import gandalf
import gandalf.client as client


class AsyncTornadoGandalfClient(client.GandalfClient):
    @gen.coroutine
    def _request(self, *args, **kwargs):
        url = kwargs.pop('url')
        data = kwargs.pop('data', None)
        if data:
            kwargs['body'] = data

        try:
            response = yield self.client(url, *args, **kwargs)
        except httpclient.HTTPError as e:
            raise gandalf.GandalfException(e.response)
        raise gen.Return(response)

    def get_code(self, response):
        return response.code

    def get_body(self, response):
        return response.body.decode('utf-8')
