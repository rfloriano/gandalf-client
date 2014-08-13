#!/usr/bin/python
# -*- coding: utf-8 -*-
import tarfile
import zipfile

try:
    import ujson as json
except ImportError:
    import json

try:
    from StringIO import StringIO
    IO = StringIO
except ImportError:
    from io import BytesIO
    IO = BytesIO

try:
    from tornado.gen import coroutine
    from tornado.gen import Return
    from tornado.concurrent import is_future
except ImportError:
    is_future = lambda x: False
    Return = lambda x: x

    def coroutine(f):
        def wrap(*args, **kwargs):
            return f(*args, **kwargs)
        return wrap


@coroutine
def run_future(future, cb=None, **kwargs):
    result = yield future
    if cb:
        raise Return(cb(result, **kwargs))
    raise Return(result)


def process_future_as_bool(response, obj, text=''):
    code = obj.get_code(response)
    body = obj.get_body(response)
    if text:
        return code == 200 and body == text
    return code == 200


def process_future_as_json(response, obj):
    body = obj.get_body(response)
    return json.loads(body)


def process_future_as_text(response, obj):
    return obj.get_body(response)


def process_future_as_archive(response, obj, format):
    if format == 'tar':
        archive = tarfile.TarFile(fileobj=IO(response.content))
    elif format == 'zip':
        archive = zipfile.ZipFile(IO(response.content))
    return archive


def response_bool(func=None, text=''):
    def _response_bool(func):
        def wrap(*args, **kwargs):
            obj = args[0]
            response = func(*args, **kwargs)
            if is_future(response):
                return run_future(response, process_future_as_bool, obj=obj, text=text)
            return process_future_as_bool(response, obj, text=text)
        return wrap

    if func is not None:
        # Used like:
        #     @response_bool
        #     def f(self):
        #         pass
        return _response_bool(func)
    # Used like @response_bool(text="WORKING")
    return _response_bool


def response_json(f):
    def wrap(*args, **kwargs):
        obj = args[0]
        response = f(*args, **kwargs)
        if is_future(response):
            return run_future(response, process_future_as_json, obj=obj)
        return process_future_as_json(response, obj)
    return wrap


def response_text(f):
    def wrap(*args, **kwargs):
        obj = args[0]
        response = f(*args, **kwargs)
        if is_future(response):
            return run_future(response, process_future_as_text, obj=obj)
        return process_future_as_text(response, obj)
    return wrap


def response_archive(f):
    def wrap(*args, **kwargs):
        obj = args[0]
        format = kwargs.get('format')
        if not format and len(args) == 4:
            format = args[3]
        else:
            format = 'zip'
        response = f(*args, **kwargs)
        if is_future(response):
            return run_future(response, process_future_as_archive, obj=obj, format=format)
        return process_future_as_archive(response, obj, format)
    return wrap


def may_async(f):
    def wrap(*args, **kwargs):
        response = f(*args, **kwargs)
        if is_future(response):
            response = run_future(response)
        return response
    return wrap
