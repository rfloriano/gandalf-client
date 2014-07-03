#!/usr/bin/python
# -*- coding: utf-8 -*-
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

    def repository_new(self, name, users, ispublic=False):
        # router.Post("/repository", http.HandlerFunc(api.NewRepository))
        return self._request(
            url=self._get_url('/repository'),
            method="POST",
            data=json.dumps({'name': name, 'users': users, 'ispublic': ispublic})
        )

    def repository_get(self, name):
        # router.Get("/repository/:name", http.HandlerFunc(api.GetRepository))
        return self._request(
            url=self._get_url('/repository/{0}'.format(name)),
            method="GET",
        )

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

    def repository_archive(self, name, ref, format):
        # router.Get("/repository/:name/archive/:ref.:format", http.HandlerFunc(api.GetArchive))
        return self._request(
            url=self._get_url('/repository/{0}/archive/{1}.{2}'.format(name, ref, format)),
            method="GET",
        )

    def repository_contents(self, name, path):
        # router.Get("/repository/:name/contents/:path", http.HandlerFunc(api.GetFileContents))
        return self._request(
            url=self._get_url('/repository/{0}/contents/{1}'.format(name, path)),
            method="GET",
        )

    def repository_delete(self, name):
        # router.Del("/repository/:name", http.HandlerFunc(api.RemoveRepository))
        return self._request(
            url=self._get_url('/repository/{0}'.format(name.strip('/'))),
            method="DELETE",
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
        # router.Post("/user", http.HandlerFunc(api.NewUser))
        return self._request(
            url=self._get_url('/user'),
            method="POST",
            data=json.dumps({'name': name, 'keys': keys})
        )

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
