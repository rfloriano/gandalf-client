#!/usr/bin/python
# -*- coding: utf-8 -*-
import uuid

from preggy import expect
from tests.base import TestCase
import gandalf.client as client
import requests

RAWKEY = "ssh-dss AAAAB3NzaC1kc3MAAACBAIHfSDLpSCfIIVEJ/Is3RFMQhsCi7WZtFQeeyfi+DzVP0NGX4j/rMoQEHgXgNlOKVCJvPk5e00tukSv6iVzJPFcozArvVaoCc5jCoDi5Ef8k3Jil4Q7qNjcoRDDyqjqLcaviJEz5GrtmqAyXEIzJ447BxeEdw3Z7UrIWYcw2YyArAAAAFQD7wiOGZIoxu4XIOoeEe5aToTxN1QAAAIAZNAbJyOnNceGcgRRgBUPfY5ChX+9A29n2MGnyJ/Cxrhuh8d7B0J8UkvEBlfgQICq1UDZbC9q5NQprwD47cGwTjUZ0Z6hGpRmEEZdzsoj9T6vkLiteKH3qLo7IPVx4mV6TTF6PWQbQMUsuxjuDErwS9nhtTM4nkxYSmUbnWb6wfwAAAIB2qm/1J6Jl8bByBaMQ/ptbm4wQCvJ9Ll9u6qtKy18D4ldoXM0E9a1q49swml5CPFGyU+cgPRhEjN5oUr5psdtaY8CHa2WKuyIVH3B8UhNzqkjpdTFSpHs6tGluNVC+SQg1MVwfG2wsZUdkUGyn+6j8ZZarUfpAmbb5qJJpgMFEKQ== f@xikinbook.local"


class TestGandalfClient(TestCase):

    def setUp(self, *args, **kwargs):
        config = self.get_config()
        self.gandalf = client.GandalfClient(config['GANDALF_HOST'], config['GANDALF_PORT'], requests.request)

    def test_can_manage_users(self):
        user = str(uuid.uuid4())
        response = self.gandalf.user_new(user, {})
        expect(response.status_code).to_equal(200)

        response = self.gandalf.user_delete(user)
        expect(response.status_code).to_equal(200)

    def test_can_manage_user_keys(self):
        user = str(uuid.uuid4())
        self.gandalf.user_new(user, {})

        response = self.gandalf.user_add_key(user, {'foo': RAWKEY})
        expect(response.status_code).to_equal(200)

        response = self.gandalf.user_get_keys(user)
        expect(response.status_code).to_equal(200)
        json = response.json()
        expect(json['foo']).to_equal(RAWKEY)

        response = self.gandalf.user_delete_key(user, 'foo')
        expect(response.status_code).to_equal(200)

        self.gandalf.user_delete(user)

    def test_can_manage_repositories(self):
        user = str(uuid.uuid4())
        user2 = str(uuid.uuid4())
        repo = str(uuid.uuid4())
        repo2 = str(uuid.uuid4())

        self.gandalf.user_new(user, {})
        self.gandalf.user_new(user2, {})

        response = self.gandalf.repository_new(repo, [user])
        expect(response.status_code).to_equal(200)

        response = self.gandalf.repository_get(repo)
        expect(response.status_code).to_equal(200)

        response = self.gandalf.repository_rename(repo, repo2)
        expect(response.status_code).to_equal(200)

        response = self.gandalf.repository_grant([user2], [repo2])
        expect(response.status_code).to_equal(200)

        response = self.gandalf.repository_revoke([user2], [repo2])
        expect(response.status_code).to_equal(200)

        response = self.gandalf.repository_delete(repo2)
        expect(response.status_code).to_equal(200)

        self.gandalf.user_delete(user)
        self.gandalf.user_delete(user2)
