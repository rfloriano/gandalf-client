#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid
import os
import tempfile
import shutil

try:
    from StringIO import StringIO
    IO = StringIO
except ImportError:
    from io import BytesIO
    IO = BytesIO

from preggy import expect
import requests
from Crypto.PublicKey import RSA

import gandalf.client as client
from tests.base import TestCase
from tests.utils import create_repository, create_bare_repository, add_file_to_repo, tag_repo, branch_repo

TMP_DIR = tempfile.gettempdir()
HOOKS_DIR = '/tmp/git/bare-template/hooks'
REPOS_DIR = '/tmp/repositories-test'

get_key = lambda: RSA.generate(2048, os.urandom).exportKey('OpenSSH')


class TestGandalfClient(TestCase):

    def setUp(self, *args, **kwargs):
        config = self.get_config()
        self.gandalf = client.GandalfClient(config['GANDALF_HOST'], config['GANDALF_PORT'], requests.request)

    def test_can_create_user(self):
        user = str(uuid.uuid4())
        result = self.gandalf.user_new(user, {
            'default': '{0} rfloriano@localmachine'.format(get_key().decode('utf-8'))
        })

        expect(result).to_be_true()

    def test_can_create_user_with_invalid_data(self):
        user = str(uuid.uuid4())
        not_created = self.gandalf.user_new(user, {
            'default': 'invalidkey'
        })

        expect(not_created).to_be_false()

    def test_can_create_user_with_no_keys(self):
        user = str(uuid.uuid4())
        result = self.gandalf.user_new(user, {})

        expect(result).to_be_true()

    def test_can_manage_users(self):
        user = str(uuid.uuid4())
        created = self.gandalf.user_new(user, {})
        expect(created).to_be_true()

        not_created = self.gandalf.user_new(user, {})
        expect(not_created).to_be_false()

        removed = self.gandalf.user_delete(user)
        expect(removed).to_be_true()

        not_removed = self.gandalf.user_delete(user)
        expect(not_removed).to_be_false()

        not_removed = self.gandalf.user_delete('user-that-does-not-exists')
        expect(not_removed).to_be_false()

    def test_can_manage_user_keys(self):
        user = str(uuid.uuid4())
        key = get_key().decode('utf-8')
        self.gandalf.user_new(user, {})

        added = self.gandalf.user_add_key(user, {'foo': key})
        expect(added).to_be_true()

        json = self.gandalf.user_get_keys(user)
        expect(json['foo']).to_equal(key)

        deleted = self.gandalf.user_delete_key(user, 'foo')
        expect(deleted).to_be_true()

        self.gandalf.user_delete(user)

    def test_can_manage_repositories(self):
        user = str(uuid.uuid4())
        user2 = str(uuid.uuid4())
        repo = str(uuid.uuid4())
        repo2 = str(uuid.uuid4())

        self.gandalf.user_new(user, {})
        self.gandalf.user_new(user2, {})

        created = self.gandalf.repository_new(repo, [user])
        expect(created).to_be_true()

        response = self.gandalf.repository_get(repo)
        expect(response).to_include('git_url')
        expect(response).to_include('ssh_url')
        expect(response).to_include('name')
        expect(response).to_include('public')

        renamed = self.gandalf.repository_rename(repo, repo2)
        expect(renamed).to_be_true()

        granted = self.gandalf.repository_grant([user2], [repo2])
        expect(granted).to_be_true()

        revoked = self.gandalf.repository_revoke([user2], [repo2])
        expect(revoked).to_be_true()

        removed = self.gandalf.repository_delete(repo2)
        expect(removed).to_be_true()

        self.gandalf.user_delete(user)
        self.gandalf.user_delete(user2)

    def test_can_get_repository(self):
        repo = str(uuid.uuid4())
        user = str(uuid.uuid4())
        user2 = str(uuid.uuid4())

        self.gandalf.user_new(user, {})
        self.gandalf.user_new(user2, {})

        created = self.gandalf.repository_new(repo, [user])
        expect(created).to_be_true()

        response = self.gandalf.repository_get(repo)
        expect(response).to_include('git_url')
        expect(response).to_include('ssh_url')
        expect(response).to_include('name')
        expect(response).to_include('public')
        expect(response['git_url']).to_equal('git://localhost:8001/%s.git' % repo)
        expect(response['ssh_url']).to_equal('git@localhost:8001:%s.git' % repo)
        expect(response['name']).to_equal(repo)
        expect(response['public']).to_be_false()

    def test_can_get_repository_branches(self):
        repo = str(uuid.uuid4())
        create_repository(repo)
        branch_repo(repo, 'branch-test')

        result = self.gandalf.repository_branches(repo)
        expect(result[0]).to_include('name')
        expect(result[0]['name']).to_equal('branch-test')
        expect(result[1]).to_include('name')
        expect(result[1]['name']).to_equal('master')

    def test_can_get_repository_tags(self):
        repo = str(uuid.uuid4())
        create_repository(repo)
        tag_repo(repo, 'my-tag')

        result = self.gandalf.repository_tags(repo)
        expect(result[0]).to_include('name')
        expect(result[0]['name']).to_equal('my-tag')

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

        tar = self.gandalf.repository_archive(repo, 'master', 'tar')
        tar.extract('{0}-master/some/path/doge.txt'.format(repo), TMP_DIR)
        archive = open(os.path.join(TMP_DIR, '{0}-master/some/path/doge.txt'.format(repo)), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal('OTHER TEST\n')

        zip_ = self.gandalf.repository_archive(repo, '0.1.0')
        zip_.extract('{0}-0.1.0/some/path/doge.txt'.format(repo), TMP_DIR)
        archive = open(os.path.join(TMP_DIR, '{0}-0.1.0/some/path/doge.txt'.format(repo)), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal('FOO BAR\n')

    def test_can_add_hook(self):
        repo = str(uuid.uuid4())
        if os.path.exists(HOOKS_DIR):
            shutil.rmtree(HOOKS_DIR)
        os.makedirs(HOOKS_DIR)

        created = self.gandalf.hook_add('post-receive', repo)
        expect(created).to_be_true()
        archive = open(os.path.join(HOOKS_DIR, 'post-receive'), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal(repo)

        created = self.gandalf.hook_add('pre-receive', repo)
        expect(created).to_be_true()
        archive = open(os.path.join(HOOKS_DIR, 'pre-receive'), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal(repo)

        created = self.gandalf.hook_add('update', repo)
        expect(created).to_be_true()
        archive = open(os.path.join(HOOKS_DIR, 'update'), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal(repo)

    def test_can_add_repository_hook(self):
        repo = str(uuid.uuid4())
        create_bare_repository(repo)

        created = self.gandalf.hook_add('post-receive', repo, repo)
        expect(created).to_be_true()
        archive = open(os.path.join(REPOS_DIR, repo + '.git', 'hooks', 'post-receive'), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal(repo)

        created = self.gandalf.hook_add('pre-receive', repo, repo)
        expect(created).to_be_true()
        archive = open(os.path.join(REPOS_DIR, repo + '.git', 'hooks', 'pre-receive'), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal(repo)

        created = self.gandalf.hook_add('update', repo, repo)
        expect(created).to_be_true()
        archive = open(os.path.join(REPOS_DIR, repo + '.git', 'hooks', 'update'), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal(repo)

        created = self.gandalf.hook_add('update', repo + ' another', [repo])
        expect(created).to_be_true()
        archive = open(os.path.join(REPOS_DIR, repo + '.git', 'hooks', 'update'), 'r')
        content = archive.read()
        archive.close()
        expect(content).to_equal(repo + ' another')

        not_created = self.gandalf.hook_add('invalid', repo, repo)
        expect(not_created).to_be_false()

    def test_can_diff_commits(self):
        repo = str(uuid.uuid4())
        create_repository(repo)
        add_file_to_repo(repo, 'some/path/doge.txt', 'FOO BAR')
        tag_repo(repo, '0.1.0')
        add_file_to_repo(repo, 'some/path/doge.txt', 'OTHER TEST')

        diff = self.gandalf.repository_diff_commits(repo, '0.1.0', 'master')
        expected = """diff --git a/some/path/doge.txt b/some/path/doge.txt
index 404727f..bd82f1d 100644
--- a/some/path/doge.txt
+++ b/some/path/doge.txt
@@ -1 +1 @@
-FOO BAR
+OTHER TEST
"""
        expect(expected).to_equal(diff)

    def test_can_commit_into_repo(self):
        repo = str(uuid.uuid4())
        create_bare_repository(repo)

        json = self.gandalf.repository_commit(
            repo,
            'Repository scaffold',
            'Author Name',
            'author@name.com',
            'Committer Name',
            'committer@email.com',
            'master',
            open('./tests/fixtures/scaffold.zip', 'rb')
        )

        expect(json).to_include('committer')
        expect(json).to_include('author')
        expect(json).to_include('name')
        expect(json).to_include('ref')
        expect(json).to_include('createdAt')
        expect(json).to_include('subject')
        expect(json).to_include('_links')

        expect(json['committer']).to_include('date')
        expect(json['committer']).to_include('name')
        expect(json['committer']).to_include('email')

        expect(json['author']).to_include('date')
        expect(json['author']).to_include('name')
        expect(json['author']).to_include('email')

        expect(json['name']).to_equal(u'master')
        expect(json['subject']).to_equal(u'Repository scaffold')

        expect(json['_links']).to_include('zipArchive')
        expect(json['_links']).to_include('tarArchive')
