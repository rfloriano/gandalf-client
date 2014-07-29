#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid
import os
import StringIO
import tarfile
import zipfile
import tempfile

from preggy import expect
import requests
from Crypto.PublicKey import RSA

import gandalf.client as client
from tests.base import TestCase
from tests.utils import create_repository, add_file_to_repo, tag_repo


TMP_DIR = tempfile.gettempdir()

get_key = lambda: RSA.generate(2048, os.urandom).exportKey('OpenSSH')


class TestGandalfClient(TestCase):

    def setUp(self, *args, **kwargs):
        config = self.get_config()
        self.gandalf = client.GandalfClient(config['GANDALF_HOST'], config['GANDALF_PORT'], requests.request)

    def test_can_create_user(self):
        user = str(uuid.uuid4())
        result = self.gandalf.user_new(user, {
            'default': '%s rfloriano@localmachine' % get_key()
        })

        expect(result).to_be_true()

    def test_can_create_user_with_invalid_data(self):
        user = str(uuid.uuid4())
        result = self.gandalf.user_new(user, {
            'default': 'invalidkey'
        })

        expect(result).to_be_false()

    def test_can_create_user_with_no_keys(self):
        user = str(uuid.uuid4())
        result = self.gandalf.user_new(user, {})

        expect(result).to_be_true()

    def test_can_manage_users(self):
        user = str(uuid.uuid4())
        response = self.gandalf.user_new(user, {})
        expect(response).to_be_true()

        response = self.gandalf.user_delete(user)
        expect(response.status_code).to_equal(200)

    def test_can_manage_user_keys(self):
        user = str(uuid.uuid4())
        key = get_key()
        self.gandalf.user_new(user, {})

        response = self.gandalf.user_add_key(user, {'foo': key})
        expect(response.status_code).to_equal(200)

        response = self.gandalf.user_get_keys(user)
        expect(response.status_code).to_equal(200)
        json = response.json()
        expect(json['foo']).to_equal(key)

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

        expect(self.gandalf.repository_new(repo, [user])).to_be_true()

        response = self.gandalf.repository_get(repo)
        expect(response).to_include('git_url')
        expect(response).to_include('ssh_url')
        expect(response).to_include('name')
        expect(response).to_include('public')

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

    def test_can_get_repository(self):
        repo = str(uuid.uuid4())
        user = str(uuid.uuid4())
        user2 = str(uuid.uuid4())

        self.gandalf.user_new(user, {})
        self.gandalf.user_new(user2, {})

        expect(self.gandalf.repository_new(repo, [user])).to_be_true()

        response = self.gandalf.repository_get(repo)
        expect(response).to_include('git_url')
        expect(response).to_include('ssh_url')
        expect(response).to_include('name')
        expect(response).to_include('public')
        expect(response['git_url']).to_equal('git://localhost:8001/%s.git' % repo)
        expect(response['ssh_url']).to_equal('git@localhost:8001:%s.git' % repo)
        expect(response['name']).to_equal(repo)
        expect(response['public']).to_be_false()

    def test_can_get_healthcheck(self):
        response = self.gandalf.healthcheck()
        expect(response).to_be_true()

    def test_can_get_tree(self):
        create_repository('test1')
        add_file_to_repo('test1', 'some/path/doge.txt', 'VERY COMMIT')
        add_file_to_repo('test1', 'some/path/to/add.txt', 'MUCH WOW')

        tree = self.gandalf.repository_tree('test1')

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

    def test_can_get_tree_with_path(self):
        create_repository('test2')
        add_file_to_repo('test2', 'some/path/doge.txt', 'VERY COMMIT')
        add_file_to_repo('test2', 'some/path/to/add.txt', 'MUCH WOW')

        tree = self.gandalf.repository_tree('test2', '/some/path/')

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

    def test_can_get_tree_with_path_for_ref(self):
        create_repository('test3')
        add_file_to_repo('test3', 'some/path/doge.txt', 'VERY COMMIT')
        tag_repo('test3', '0.1.0')
        add_file_to_repo('test3', 'some/path/to/add.txt', 'MUCH WOW')

        tree = self.gandalf.repository_tree('test3', '/some/path/', '0.1.0')

        expect(tree).to_length(1)
        expect(tree[0]).to_be_like({
            u'rawPath': u'some/path/doge.txt',
            u'path': u'some/path/doge.txt',
            u'filetype': u'blob',
            u'hash': u'cb508ee85be1e116233ae7c18e2d9bcc9553d209',
            u'permission': u'100644'
        })

    def test_can_get_repository_contents(self):
        repo = str(uuid.uuid4())
        create_repository(repo)
        add_file_to_repo(repo, 'some/path/doge.txt', 'FOO BAR')
        tag_repo(repo, '0.1.0')
        add_file_to_repo(repo, 'some/path/doge.txt', 'OTHER TEST')

        content = self.gandalf.repository_contents(repo, 'some/path/doge.txt', '0.1.0')
        expect(content).to_equal('FOO BAR\n')

        content = self.gandalf.repository_contents(repo, 'some/path/doge.txt')
        expect(content).to_equal('OTHER TEST\n')

    def test_can_get_repository_archive(self):
        repo = str(uuid.uuid4())
        create_repository(repo)
        add_file_to_repo(repo, 'some/path/doge.txt', 'FOO BAR')
        tag_repo(repo, '0.1.0')
        add_file_to_repo(repo, 'some/path/doge.txt', 'OTHER TEST')

        file_ = self.gandalf.repository_archive(repo, 'master', 'tar')
        tar = tarfile.TarFile(fileobj=StringIO.StringIO(file_.content))
        tar.extract('{0}-master/some/path/doge.txt'.format(repo), TMP_DIR)
        archive = file(os.path.join(TMP_DIR, '{0}-master/some/path/doge.txt'.format(repo)), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal('OTHER TEST\n')

        file_ = self.gandalf.repository_archive(repo, '0.1.0')
        zip_ = zipfile.ZipFile(StringIO.StringIO(file_.content))
        zip_.extract('{0}-0.1.0/some/path/doge.txt'.format(repo), TMP_DIR)
        archive = file(os.path.join(TMP_DIR, '{0}-0.1.0/some/path/doge.txt'.format(repo)), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal('FOO BAR\n')
