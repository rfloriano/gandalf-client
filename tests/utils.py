#!/usr/bin/python
# -*- coding: utf-8 -*-

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


def tag_repo(repo, tag):
    repo_name = '%s.git' % repo
    os.system('cd %s/%s && git tag %s > /dev/null' % (
        ROOT, repo_name,
        tag
    ))


def branch_repo(repo, tag):
    repo_name = '%s.git' % repo
    os.system('cd %s/%s && git branch %s > /dev/null' % (
        ROOT, repo_name,
        tag
    ))
