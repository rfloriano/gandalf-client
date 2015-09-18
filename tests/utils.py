#!/usr/bin/python
# -*- coding: utf-8 -*-

import functools
import os
from os.path import join, exists, dirname
import shutil

ROOT = '/tmp/repositories-test'


def create_repository(name):
    repo_name = '%s.git' % name
    repo_path = join(ROOT, repo_name)
    if exists(repo_path):
        shutil.rmtree(repo_path)

    os.system('cd %s && mkdir %s && cd %s && git init > /dev/null && touch README && git add . > /dev/null && git commit -am "Initial commit" > /dev/null' % (
        ROOT, repo_name, repo_name
    ))


def create_bare_repository(name):
    repo_name = '%s.git' % name
    repo_path = join(ROOT, repo_name)
    if exists(repo_path):
        shutil.rmtree(repo_path)

    os.system('cd %s && mkdir %s && cd %s && git init --bare > /dev/null' % (
        ROOT, repo_name, repo_name
    ))


def add_file_to_repo(repo, path, contents):
    repo_name = '%s.git' % repo
    os.system('cd %s/%s && mkdir -p %s && echo "%s" > %s && git add . > /dev/null && git commit -am "%s" > /dev/null' % (
        ROOT, repo_name,
        dirname(path),
        contents,
        path,
        path
    ))


def add_img_to_repo(repo, path, file_path):
    repo_name = '%s.git' % repo
    cmd = 'cd %s/%s && mkdir -p %s && cp "%s" %s && git add . > /dev/null && git commit -am "%s" > /dev/null' % (
        ROOT, repo_name,
        dirname(path),
        file_path,
        dirname(path),
        path
    )
    os.system(cmd)


def tag_repo(repo, tag, annotation=None):
    if annotation is not None:
        annotation = u' -m "%s"' % annotation
    else:
        annotation = ''
    repo_name = '%s.git' % repo
    os.system(u'cd %s/%s && git tag %s%s > /dev/null' % (
        ROOT, repo_name,
        tag,
        annotation
    ))


def branch_repo(repo, tag):
    repo_name = '%s.git' % repo
    os.system('cd %s/%s && git branch %s > /dev/null' % (
        ROOT, repo_name,
        tag
    ))


class GitEnvironVarsInjector(object):

    def __init__(self, which, name, email):
        self.which = which.upper()
        self.name = name
        self.email = email

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            os.putenv('GIT_%s_NAME' % self.which, self.name)
            os.putenv('GIT_%s_EMAIL' % self.which, self.email)
            return func(*args, **kwargs)
        return wrapped

with_git_author = functools.partial(GitEnvironVarsInjector, 'author')
with_git_committer = functools.partial(GitEnvironVarsInjector, 'committer')
