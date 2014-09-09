#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of gandalf-client.
# https://github.com/rfloriano/gandalf-client

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com


class GandalfException(Exception):
    def __init__(self, response=None, obj=None):
        self.response = response
        self.obj = obj
        if obj:
            self.status_code = obj.get_code(response)
            self.content = obj.get_content(response)
        else:
            self.status_code = obj.status_code
            self.content = obj.content
        super(GandalfException, self).__init__(
            '{0} (Gandalf server response HTTP {1})'
            .format(self.content.strip("\n "), self.status_code)
        )
