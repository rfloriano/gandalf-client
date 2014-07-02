#!/usr/bin/python
# -*- coding: utf-8 -*-
from preggy import expect

from tests.base import TestCase

import gandalf.client as client

RAWKEY = "ssh-dss AAAAB3NzaC1kc3MAAACBAIHfSDLpSCfIIVEJ/Is3RFMQhsCi7WZtFQeeyfi+DzVP0NGX4j/rMoQEHgXgNlOKVCJvPk5e00tukSv6iVzJPFcozArvVaoCc5jCoDi5Ef8k3Jil4Q7qNjcoRDDyqjqLcaviJEz5GrtmqAyXEIzJ447BxeEdw3Z7UrIWYcw2YyArAAAAFQD7wiOGZIoxu4XIOoeEe5aToTxN1QAAAIAZNAbJyOnNceGcgRRgBUPfY5ChX+9A29n2MGnyJ/Cxrhuh8d7B0J8UkvEBlfgQICq1UDZbC9q5NQprwD47cGwTjUZ0Z6hGpRmEEZdzsoj9T6vkLiteKH3qLo7IPVx4mV6TTF6PWQbQMUsuxjuDErwS9nhtTM4nkxYSmUbnWb6wfwAAAIB2qm/1J6Jl8bByBaMQ/ptbm4wQCvJ9Ll9u6qtKy18D4ldoXM0E9a1q49swml5CPFGyU+cgPRhEjN5oUr5psdtaY8CHa2WKuyIVH3B8UhNzqkjpdTFSpHs6tGluNVC+SQg1MVwfG2wsZUdkUGyn+6j8ZZarUfpAmbb5qJJpgMFEKQ== f@xikinbook.local"


class TestGandalfClient(TestCase):

    def setUp(self, *args, **kwargs):
        config = self.get_config()
        self.gandalf = client.GandalfClient(config['GANDALF_HOST'], config['GANDALF_PORT'])

    def test_can_manage_users(self):
        response = self.gandalf.user_new('user-tests', {})
        expect(response.status_code).to_equal(200)

        response = self.gandalf.user_delete('user-tests')
        expect(response.status_code).to_equal(200)

    def test_can_manage_user_keys(self):
        # TODO: add user direct by gandalf
        self.gandalf.user_new('u-key-tests', {})

        response = self.gandalf.user_add_key('u-key-tests', {'foo': RAWKEY})
        expect(response.status_code).to_equal(200)

        response = self.gandalf.user_get_keys('u-key-tests')
        expect(response.status_code).to_equal(200)
        json = response.json()
        expect(json['foo']).to_equal(RAWKEY)

        response = self.gandalf.user_delete_key('u-key-tests', 'foo')
        expect(response.status_code).to_equal(200)

        self.gandalf.user_delete('u-key-tests')

    def test_can_manage_repositories(self):
        # TODO: add user direct by gandalf
        self.gandalf.user_new('u-repositories-test', {})
        self.gandalf.user_new('u-repositories-test2', {})

        response = self.gandalf.repository_new('repository-test', ['u-repositories-test'])
        expect(response.status_code).to_equal(200)

        # response = self.gandalf.repository_get('repository-test')
        # expect(response.status_code).to_equal(200)

        response = self.gandalf.repository_rename('repository-test', 'repo-test')
        expect(response.status_code).to_equal(200)

        response = self.gandalf.repository_grant(['u-repositories-test2'], ['repo-test'])
        expect(response.status_code).to_equal(200)

        response = self.gandalf.repository_revoke(['u-repositories-test2'], ['repo-test'])
        expect(response.status_code).to_equal(200)

        response = self.gandalf.repository_delete('repo-test')
        expect(response.status_code).to_equal(200)

        self.gandalf.user_delete('u-repositories-test')
        self.gandalf.user_delete('u-repositories-test2')
