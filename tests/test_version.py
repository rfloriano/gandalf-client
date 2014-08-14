#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of gandalf-client.
# https://github.com/rfloriano/gandalf-client

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com

from preggy import expect

from gandalf.version import __version__
from tests.base import TestCase


class VersionTestCase(TestCase):
    def test_has_proper_version(self):
        expect(__version__).to_equal("0.3.0")
