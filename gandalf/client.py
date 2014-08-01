#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging

try:
    import ujson as json
except ImportError:
    import json


class GandalfClient(object):

    def __init__(self, host, port, client):
        self.host = host
        self.port = port
        self.client = client
        self.gandalf_server = self._get_gandalf_server()

    def _get_gandalf_server(self):
        return 'http://{0}:{1}'.format(self.host, self.port)

    def _get_url(self, route):
        return '{0}/{1}'.format(self.gandalf_server, route.lstrip('/'))

    def _request(self, *args, **kwargs):
        return self.client(*args, **kwargs)

    def repository_new(self, name, users, is_public=False):
        '''
        Creates a new repository with the given name.

        :param name: repository name
        :param users: list of usernames that have write access to this repository
        :type users: list of strings
        :param is_public: indicates whether this repository should be readable for everyone or not.
        :type is_public: boolean flag
        :return: True if repository was created, False otherwise

        Usage:

        .. doctest:: repository_new

           >>> gandalf.repository_new(repo_name, users=['rfloriano'], is_public=True)
           True
        '''
        # TODO: needs to validate if repository has some user
        # router.Post("/repository", http.HandlerFunc(api.NewRepository))
        try:
            response = self._request(
                url=self._get_url('/repository'),
                method="POST",
                data=json.dumps({'name': name, 'users': users, 'ispublic': is_public})
            )
            if response.status_code == 200:
                return True

        except Exception:
            err = sys.exc_info()[1]
            logging.exception(err)
            return False

        logging.error("Could not create repository %s." % name)
        return False

    def repository_get(self, name):
        '''
        Gets information on the specified repository.

        :param name: repository name
        :return: Information on the specified repository.

        Usage:

        .. doctest:: repository_get

           >>> result = gandalf.repository_get(repo_name)
           >>> result == {
           ...     u'public': True,
           ...     u'ssh_url': u'git@localhost:8001:%s.git' % repo_name,
           ...     u'git_url': u'git://localhost:8001/%s.git' % repo_name,
           ...     u'name': repo_name
           ... }
           True
        '''

        # router.Get("/repository/:name", http.HandlerFunc(api.GetRepository))
        response = self._request(
            url=self._get_url('/repository/{0}'.format(name)),
            method="GET",
        )

        if response.status_code != 200:
            raise RuntimeError("Could not retrieve repository information. Status: %s. Error: %s" % (
                response.status_code, response.text)
            )

        return json.loads(response.text)

    def repository_tree(self, name, path='', ref='master'):
        '''
        Returns a list of all tracked files in the specified path in the given repository.
        If ref is specified, that revision is used instead of the master branch.

        :param name: repository name
        :param path: optional argument that specifies the root node of the tree
        :param ref: optional argument that specifies the ref you want to retrieve the tree for
        :type ref: tag, branch or commit
        :return: A list of objects found in the given repository
        :raises: RuntimeError if gandalf response status code is not 200

        Usage:

        .. doctest:: repository_tree

           >>> result = gandalf.repository_tree('tree-test', path='/some/path', ref='0.1.0')
           >>> result == [{
           ...     u'rawPath': u'some/path/file.txt',
           ...     u'path': u'some/path/file.txt',
           ...     u'filetype': u'blob',
           ...     u'hash': u'deb02c1a0de2ce994ccc4c88155764aeeb7fc4a6',
           ...     u'permission': u'100644'
           ... }]
           True
        '''
        # router.Get("/repository/:name/tree", http.HandlerFunc(api.GetTree))
        path = path.lstrip('/')
        if path != '':
            path = "&path=%s" % path

        url = self._get_url('/repository/{0}/tree?ref={1}{2}'.format(name, ref, path))
        response = self._request(
            url=url,
            method="GET",
        )

        if response.status_code != 200:
            raise RuntimeError("Could not retrieve tree. Status: %s. Error: %s" % (
                response.status_code, response.text
            ))

        return json.loads(response.text)

    def repository_rename(self, old_name, new_name):
        # router.Put("/repository/:name", http.HandlerFunc(api.RenameRepository))
        return self._request(
            url=self._get_url('/repository/{0}'.format(old_name)),
            method="PUT",
            data=json.dumps({'name': new_name})
        )

    def repository_grant(self, users, repositories):
        # router.Post("/repository/grant", http.HandlerFunc(api.GrantAccess))
        return self._request(
            url=self._get_url('/repository/grant'),
            method="POST",
            data=json.dumps({'users': users, 'repositories': repositories})
        )

    def repository_revoke(self, users, repositories):
        # router.Del("/repository/revoke", http.HandlerFunc(api.RevokeAccess))
        return self._request(
            url=self._get_url('/repository/revoke'),
            method="DELETE",
            data=json.dumps({'users': users, 'repositories': repositories})
        )

    def repository_archive(self, name, ref, format='zip'):
        # router.Get("/repository/:name/archive", http.HandlerFunc(api.GetArchive))
        return self._request(
            url=self._get_url('/repository/{0}/archive?ref={1}&format={2}'.format(name, ref, format)),
            method="GET",
        )

    def repository_contents(self, name, path, ref='master'):
        # router.Get("/repository/:name/contents", http.HandlerFunc(api.GetFileContents))
        request = self._request(
            url=self._get_url('/repository/{0}/contents?path={1}&ref={2}'.format(name, path, ref)),
            method="GET",
        )

        if request.status_code != 200:
            raise RuntimeError(request.text)

        return request.text

    def repository_delete(self, name):
        # router.Del("/repository/:name", http.HandlerFunc(api.RemoveRepository))
        return self._request(
            url=self._get_url('/repository/{0}'.format(name.strip('/'))),
            method="DELETE",
        )

    def repository_branches(self, name):
        # router.Get("/repository/:name/branches", http.HandlerFunc(api.GetBranches))
        return self._request(
            url=self._get_url('/repository/{0}/branches'.format(name)),
            method="GET",
        )

    def repository_tags(self, name):
        # router.Get("/repository/:name/tags", http.HandlerFunc(api.GetTags))
        return self._request(
            url=self._get_url('/repository/{0}/tags'.format(name)),
            method="GET",
        )

    def repository_hook(self, name, repositories, content):
        # router.Post("/repository/hook/:name", http.HandlerFunc(api.AddRepositoryHook))
        if isinstance(repositories, basestring):
            repositories = [repositories]

        return self._request(
            url=self._get_url('/repository/hook/{0}'.format(name)),
            method="POST",
            data=json.dumps({
                "repositories": repositories,
                "content": content
            })
        )

    def repository_diff_commits(self, name, previous_commit, last_commit):
        # router.Get("/repository/:name/diff/commits", http.HandlerFunc(api.GetDiff))
        return self._request(
            url=self._get_url('/repository/{0}/diff/commits?previous_commit={1}&last_commit={2}'\
                    .format(name, previous_commit, last_commit)),
            method="GET"
        )

    def user_add_key(self, name, keys):
        # router.Post("/user/:name/key", http.HandlerFunc(api.AddKey))
        return self._request(
            url=self._get_url('/user/{0}/key'.format(name)),
            method="POST",
            data=json.dumps(keys)
        )

    def user_get_keys(self, name):
        # router.Get("/user/:name/keys", http.HandlerFunc(api.ListKeys))
        return self._request(
            url=self._get_url('/user/{0}/keys'.format(name)),
            method="GET",
        )

    def user_delete_key(self, name, keyname):
        # router.Del("/user/:name/key/:keyname", http.HandlerFunc(api.RemoveKey))
        return self._request(
            url=self._get_url('/user/{0}/key/{1}'.format(name, keyname)),
            method="DELETE",
        )

    def user_new(self, name, keys):
        '''
        Creates a new user. SSH Keys for this user may be specified.

        :param name: user name
        :param keys: Named ssh keys that will be bound to this user
        :type keys: dict where key is SSH Key name and value is the SSH Public Key
        :return: True if user was created, False otherwise

        Usage:

        .. doctest:: user_new

           >>> gandalf.user_new(user_name, keys={
           ...    'default': my_ssh_public_key
           ... })
           True
        '''

        # router.Post("/user", http.HandlerFunc(api.NewUser))
        try:
            response = self._request(
                url=self._get_url('/user'),
                method="POST",
                data=json.dumps({'name': name, 'keys': keys})
            )

            if response.status_code != 200:
                return False

        except Exception:
            err = sys.exc_info()[1]
            logging.exception(err)
            return False

        return True

    def user_delete(self, name):
        # router.Del("/user/:name", http.HandlerFunc(api.RemoveUser))
        return self._request(
            url=self._get_url('/user/{0}'.format(name)),
            method="DELETE",
        )

    def hook_add(self, name, content):
        # router.Post("/hook/:name", http.HandlerFunc(api.AddHook))
        return self._request(
            url=self._get_url('/hook/{0}'.format(name)),
            method="POST",
            data=content
        )

    def healthcheck(self):
        # router.Get("/healthcheck/", http.HandlerFunc(api.HealthCheck))
        response = self._request(
            url=self._get_url('/healthcheck'),
            method="GET",
        )

        if response.status_code != 200:
            return False

        if hasattr(response, 'body'):
            return response.body.decode('utf-8') == 'WORKING'

        if hasattr(response, 'text'):
            return response.text == 'WORKING'

        return False
