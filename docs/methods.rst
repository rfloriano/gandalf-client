Available Methods
=================

.. testsetup:: *

   import requests
   from gandalf.client import GandalfClient
   gandalf = GandalfClient("localhost", 8001, requests.request)

.. testsetup:: repository_tree, repository_log

   import requests
   from uuid import uuid4
   from tests.utils import create_repository, add_file_to_repo, tag_repo
   from gandalf.client import GandalfClient

   repo_name = "repository_test_%s" % uuid4()
   gandalf = GandalfClient("localhost", 8001, requests.request)
   create_repository(repo_name)
   add_file_to_repo(repo_name, 'some/path/file.txt', 'file-content')
   tag_repo(repo_name, '0.1.0')
   add_file_to_repo(repo_name, 'some/path/other.txt', 'other-file-content')

.. testsetup:: repository_new

   import requests
   from uuid import uuid4
   from gandalf.client import GandalfClient
   from tests.utils import create_repository, add_file_to_repo, tag_repo
   gandalf = GandalfClient("localhost", 8001, requests.request)

   repo_name = "newtest_%s" % uuid4()

.. testsetup:: user_new

   import os
   import requests
   from uuid import uuid4
   from gandalf.client import GandalfClient
   from tests.utils import create_repository, add_file_to_repo, tag_repo
   from Crypto.PublicKey import RSA

   gandalf = GandalfClient("localhost", 8001, requests.request)

   user_name = "user_%s" % uuid4()
   my_ssh_public_key = RSA.generate(2048, os.urandom).exportKey('OpenSSH').decode('utf-8')

.. testsetup:: repository_get

   import requests
   from uuid import uuid4
   from gandalf.client import GandalfClient
   from tests.utils import create_repository, add_file_to_repo, tag_repo
   gandalf = GandalfClient("localhost", 8001, requests.request)

   repo_name = "gettest_%s" % uuid4()
   gandalf.repository_new(repo_name, ['rfloriano'], True)

:mod:`client` Module
====================

.. automodule:: gandalf.client
    :members:
    :undoc-members:

repository_grant
----------------

Grant access to users in repositories

Arguments:

* users: List of users to grant accesss
* repositories: List of repositories to grant users acesss

Example:

.. testcode:: repository_grant

   gandalf.repository_grant(['rfloriano'], ['project-repository'])


repository_update
-----------------

Updates repository data

Arguments:

* repository: List of all users to set accesss

Keywork arguments:

* users: List of users to replace if set
* readonlyusers: List of read only users to replace if set
* ispublic: Set if repository is public (boolean)

Example:

.. testcode:: repository_update

   gandalf.repository_update('rfloriano', name='bla-bla', users=['user1@gmail.com'], readonlyusers=[], ispublic=False)

repository_revoke
-----------------

Revoke access to users in repositories

Arguments:

* users: List of users to revoke accesss
* repositories: List of repositories to revoke users acesss

Example:

.. testcode:: repository_grant

   gandalf.repository_grant(['rfloriano'], ['project-repository'])


repository_archive
------------------

Arguments:

* name: The repository's name
* ref: Git reference to file
* format: The file format


repository_contents
-------------------
Arguments:

* name: The repository's name
* path: File's path


repository_delete
-----------------

Delete a repository

Arguments:

* name: The repository's name

Example:

.. testcode:: repository_delete

   gandalf.repository_delete('project-repository')


repository_log
--------------

Returns a list of all commits into repository

Arguments:

* name: The repository's name
* ref: The repository ref (commit, tag or branch)
* total: The maximum number of items to retrieve
* path: Path to file or directory to filter log

Example:

.. testcode:: repository_log

   gandalf.repository_log(repo_name, 'HEAD', 1, 'README.md')


user_add_key
------------

Add ssh public key to an user

Arguments:

* name: The username
* keys: Dictionary of public key to associate with user account (Ie: {'macbook-key': 'ssh-dss my-public-key== f@foo.bar'})

Example:

.. testcode:: user_add_key

   gandalf.user_add_key('rfloriano', {'my-ssh-key-another': 'content-of-my-ssh-public-another-key'})


user_get_keys
-------------

Get keys from an user

Arguments:

* name: The username

Example:

.. testcode:: user_get_keys

   gandalf.user_get_keys('rfloriano')


user_delete_key
---------------

Delete keys from an user

Arguments:

* name: The username
* keyname: The key name to remove (Ie: 'macbook-key')

Example:

.. testcode:: user_delete_key

   gandalf.user_delete_key('rfloriano', 'my-ssh-key-another')

user_delete
-----------

Delete an user

Arguments:

* name: The username

Example:

.. testcode:: user_delete

   gandalf.user_delete('rfloriano')


hook_add
--------

Add git server hook

Arguments:

* name: The hook's name
* content: Content of hook

healthcheck
-----------

Validates if the gandalf server responds to healthcheck.

Example:

.. testcode:: healthcheck

   assert gandalf.healthcheck()
