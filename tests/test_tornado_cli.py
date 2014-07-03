#!/usr/bin/python
# -*- coding: utf-8 -*-
import uuid

import json
from preggy import expect
from tornado.testing import gen_test

import gandalf.tornado_cli as client
from tests.base import AsyncTestCase

RAWKEY = "ssh-dss AAAAB3NzaC1kc3MAAACBAIHfSDLpSCfIIVEJ/Is3RFMQhsCi7WZtFQeeyfi+DzVP0NGX4j/rMoQEHgXgNlOKVCJvPk5e00tukSv6iVzJPFcozArvVaoCc5jCoDi5Ef8k3Jil4Q7qNjcoRDDyqjqLcaviJEz5GrtmqAyXEIzJ447BxeEdw3Z7UrIWYcw2YyArAAAAFQD7wiOGZIoxu4XIOoeEe5aToTxN1QAAAIAZNAbJyOnNceGcgRRgBUPfY5ChX+9A29n2MGnyJ/Cxrhuh8d7B0J8UkvEBlfgQICq1UDZbC9q5NQprwD47cGwTjUZ0Z6hGpRmEEZdzsoj9T6vkLiteKH3qLo7IPVx4mV6TTF6PWQbQMUsuxjuDErwS9nhtTM4nkxYSmUbnWb6wfwAAAIB2qm/1J6Jl8bByBaMQ/ptbm4wQCvJ9Ll9u6qtKy18D4ldoXM0E9a1q49swml5CPFGyU+cgPRhEjN5oUr5psdtaY8CHa2WKuyIVH3B8UhNzqkjpdTFSpHs6tGluNVC+SQg1MVwfG2wsZUdkUGyn+6j8ZZarUfpAmbb5qJJpgMFEKQ== f@xikinbook.local"


def load_json(json_string):
    try:
        return json.loads(json_string)
    except (ValueError, TypeError):
        return json.loads(json_string.decode('utf-8'))


class TestTornadoGandalfClient(AsyncTestCase):

    def setUp(self, *args, **kwargs):
        super(TestTornadoGandalfClient, self).setUp(*args, **kwargs)
        config = self.get_config()
        self.gandalf = client.AsyncTornadoGandalfClient(config['GANDALF_HOST'], config['GANDALF_PORT'], self.server.application.http_client.fetch)

    @gen_test
    def test_can_manage_users(self):
        user = str(uuid.uuid4())
        response = yield self.gandalf.user_new(user, {})
        expect(response.code).to_equal(200)

        response = yield self.gandalf.user_delete(user)
        expect(response.code).to_equal(200)

    @gen_test
    def test_can_manage_user_keys(self):
        user = str(uuid.uuid4())

        yield self.gandalf.user_new(user, {})

        response = yield self.gandalf.user_add_key(user, {'foo': RAWKEY})
        expect(response.code).to_equal(200)

        response = yield self.gandalf.user_get_keys(user)
        expect(response.code).to_equal(200)

        data = load_json(response.body)
        expect(data['foo']).to_equal(RAWKEY)

        response = yield self.gandalf.user_delete_key(user, 'foo')
        expect(response.code).to_equal(200)

        yield self.gandalf.user_delete(user)

    @gen_test
    def test_can_manage_repositories(self):
        user = str(uuid.uuid4())
        user2 = str(uuid.uuid4())
        repo = str(uuid.uuid4())
        repo2 = str(uuid.uuid4())

        yield self.gandalf.user_new(user, {})
        yield self.gandalf.user_new(user2, {})

        response = yield self.gandalf.repository_new(repo, [user])
        expect(response.code).to_equal(200)

        response = yield self.gandalf.repository_get(repo)
        expect(response.code).to_equal(200)

        response = yield self.gandalf.repository_rename(repo, repo2)
        expect(response.code).to_equal(200)

        response = yield self.gandalf.repository_grant([user2], [repo2])
        expect(response.code).to_equal(200)

        # response = yield self.gandalf.repository_revoke([user2], [repo2])
        # expect(response.code).to_equal(200)

        response = yield self.gandalf.repository_delete(repo2)
        expect(response.code).to_equal(200)

        yield self.gandalf.user_delete(user)
        yield self.gandalf.user_delete(user2)
