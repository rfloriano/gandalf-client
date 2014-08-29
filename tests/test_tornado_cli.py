#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import uuid

import json
from preggy import expect
from tornado.testing import gen_test
from Crypto.PublicKey import RSA

import gandalf.tornado_cli as client
from tests.base import AsyncTestCase
from tests.utils import create_repository, add_file_to_repo, tag_repo

get_key = lambda: RSA.generate(2048, os.urandom).exportKey('OpenSSH')


def load_json(json_string):
    try:
        return json.loads(json_string)
    except (ValueError, TypeError):
        return json.loads(json_string.decode('utf-8'))


class TestTornadoGandalfClient(AsyncTestCase):

    def setUp(self, *args, **kwargs):
        super(TestTornadoGandalfClient, self).setUp(*args, **kwargs)
        config = self.get_config()
        self.gandalf = client.AsyncTornadoGandalfClient(
            config['GANDALF_HOST'], config['GANDALF_PORT'],
            self.server.application.http_client.fetch
        )

    @gen_test
    def test_can_manage_users(self):
        user = str(uuid.uuid4())
        created = yield self.gandalf.user_new(user, {})
        expect(created).to_be_true()

        removed = yield self.gandalf.user_delete(user)
        expect(removed).to_be_true()

    @gen_test
    def test_can_manage_user_keys(self):
        user = str(uuid.uuid4())
        key = get_key().decode('utf-8')

        yield self.gandalf.user_new(user, {})

        added = yield self.gandalf.user_add_key(user, {'foo': key})
        expect(added).to_be_true()

        json = yield self.gandalf.user_get_keys(user)
        expect(json['foo']).to_equal(key)

        removed = yield self.gandalf.user_delete_key(user, 'foo')
        expect(removed).to_be_true()

        yield self.gandalf.user_delete(user)

    @gen_test
    def test_can_manage_repositories(self):
        user = str(uuid.uuid4())
        user2 = str(uuid.uuid4())
        repo = str(uuid.uuid4())
        repo2 = str(uuid.uuid4())

        yield self.gandalf.user_new(user, {})
        yield self.gandalf.user_new(user2, {})

        created = yield self.gandalf.repository_new(repo, [user])
        expect(created).to_be_true()

        response = yield self.gandalf.repository_get(repo)
        expect(response).to_include('git_url')
        expect(response).to_include('ssh_url')
        expect(response).to_include('name')
        expect(response).to_include('public')

        renamed = yield self.gandalf.repository_rename(repo, repo2)
        expect(renamed).to_be_true()

        granted = yield self.gandalf.repository_grant([user2], [repo2])
        expect(granted).to_be_true()

        # TODO: gandalf server needs to accept delete without body
        # response = yield self.gandalf.repository_revoke([user2], [repo2])
        # expect(response.code).to_equal(200)

        removed = yield self.gandalf.repository_delete(repo2)
        expect(removed).to_be_true()

        yield self.gandalf.user_delete(user)
        yield self.gandalf.user_delete(user2)

    @gen_test
    def test_can_get_healthcheck(self):
        response = yield self.gandalf.healthcheck()
        expect(response).to_be_true()

    @gen_test
    def test_can_get_tree(self):
        create_repository('test1')
        add_file_to_repo('test1', 'some/path/doge.txt', 'VERY COMMIT')
        add_file_to_repo('test1', 'some/path/to/add.txt', 'MUCH WOW')

        tree = yield self.gandalf.repository_tree('test1')

        expect(tree[0]).to_be_like({
            u'rawPath': u'README',
            u'path': u'README',
            u'filetype': u'blob',
            u'hash': u'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391',
            u'permission': u'100644'
        })

        expect(tree[1]).to_be_like({
            u'rawPath': u'some/path/doge.txt',
            u'path': u'some/path/doge.txt',
            u'filetype': u'blob',
            u'hash': u'cb508ee85be1e116233ae7c18e2d9bcc9553d209',
            u'permission': u'100644'
        })

        expect(tree[2]).to_be_like({
            u'rawPath': u'some/path/to/add.txt',
            u'path': u'some/path/to/add.txt',
            u'filetype': u'blob',
            u'hash': u'c5545f629c01a7597c9d4f9d5b68626062551622',
            u'permission': u'100644'
        })

    @gen_test
    def test_can_get_tree_with_path(self):
        create_repository('test2')
        add_file_to_repo('test2', 'some/path/doge.txt', 'VERY COMMIT')
        add_file_to_repo('test2', 'some/path/to/add.txt', 'MUCH WOW')

        tree = yield self.gandalf.repository_tree('test2', '/some/path/')

        expect(tree[0]).to_be_like({
            u'rawPath': u'some/path/doge.txt',
            u'path': u'some/path/doge.txt',
            u'filetype': u'blob',
            u'hash': u'cb508ee85be1e116233ae7c18e2d9bcc9553d209',
            u'permission': u'100644'
        })

        expect(tree[1]).to_be_like({
            u'rawPath': u'some/path/to/add.txt',
            u'path': u'some/path/to/add.txt',
            u'filetype': u'blob',
            u'hash': u'c5545f629c01a7597c9d4f9d5b68626062551622',
            u'permission': u'100644'
        })

    @gen_test
    def test_can_get_tree_with_path_for_ref(self):
        create_repository('test3')
        add_file_to_repo('test3', 'some/path/doge.txt', 'VERY COMMIT')
        tag_repo('test3', '0.1.0')
        add_file_to_repo('test3', 'some/path/to/add.txt', 'MUCH WOW')

        tree = yield self.gandalf.repository_tree('test3', '/some/path/', '0.1.0')

        expect(tree).to_length(1)
        expect(tree[0]).to_be_like({
            u'rawPath': u'some/path/doge.txt',
            u'path': u'some/path/doge.txt',
            u'filetype': u'blob',
            u'hash': u'cb508ee85be1e116233ae7c18e2d9bcc9553d209',
            u'permission': u'100644'
        })
