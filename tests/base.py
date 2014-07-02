#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of gandalf-client.
# https://github.com/rfloriano/gandalf-client

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com

from unittest import TestCase as PythonTestCase


class TestCase(PythonTestCase):

    def get_config(self):
        return dict(
            GANDALF_HOST='localhost',
            GANDALF_PORT=8001,
        )
