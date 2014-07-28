#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging

try:
    import ujson as json
except ImportError:
    import json


import tornado.gen as gen

import gandalf.client as client


class AsyncTornadoGandalfClient(client.GandalfClient):

    @gen.coroutine
    def _request(self, *args, **kwargs):
        url = kwargs.pop('url')
        data = kwargs.pop('data', None)
        if data:
            kwargs['body'] = data

        response = yield self.client(url, *args, **kwargs)
        raise gen.Return(response)

    @gen.coroutine
    def healthcheck(self):
        response = yield self._request(
            url=self._get_url('/healthcheck'),
            method="GET",
        )

        if response.code != 200:
            raise gen.Return(False)

        if hasattr(response, 'body'):
            raise gen.Return(response.body.decode('utf-8') == 'WORKING')

        if hasattr(response, 'text'):
            raise gen.Return(response.text == 'WORKING')

        raise gen.Return(False)

    @gen.coroutine
    def repository_new(self, name, users, is_public=False):
        # router.Post("/repository", http.HandlerFunc(api.NewRepository))
        try:
            response = yield self._request(
                url=self._get_url('/repository'),
                method="POST",
                data=json.dumps({'name': name, 'users': users, 'ispublic': is_public})
            )
            if response.code == 200:
                raise gen.Return(True)
        except Exception:
            err = sys.exc_info()[1]
            logging.exception(err)

        logging.error("Could not create repository %s." % name)
        raise gen.Return(False)

    @gen.coroutine
    def repository_get(self, name):
        '''
        Gets information on the specified repository.

        :param name: repository name
        :return: Information on the specified repository.

        Usage:

        .. testcode:: repository_get

           gandalf.repository_get('my-project-repository')
        '''

        # router.Get("/repository/:name", http.HandlerFunc(api.GetRepository))
        response = yield self._request(
            url=self._get_url('/repository/{0}'.format(name)),
            method="GET",
        )

        if response.code != 200:
            raise RuntimeError("Could not retrieve repository information. Status: %s. Error: %s" % (
                response.code, response.body)
            )

        raise gen.Return(json.loads(response.body))

    @gen.coroutine
    def repository_tree(self, name, path='', ref='master'):
        # router.Get("/repository/:name/tree/:path", http.HandlerFunc(api.GetTree))
        path = path.lstrip('/')
        if path != '':
            path = "&path=%s" % path

        url = self._get_url('/repository/{0}/tree?ref={1}{2}'.format(name, ref, path))

        response = yield self._request(
            url=url,
            method="GET",
        )

        if response.code != 200:
            raise RuntimeError("Could not retrieve tree. Status: %s. Error: %s" % (response.code, response.body))

        raise gen.Return(json.loads(response.body))
