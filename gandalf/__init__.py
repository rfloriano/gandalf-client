#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of gandalf-client.
# https://github.com/rfloriano/gandalf-client

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com

class GandalfException(Exception):
    def __init__(self, response=None):
        self.response = response
        return super(GandalfException, self).__init__('{0} (Gandalf server response HTTP {1})'\
            .format(response.body.strip(), response.code))
