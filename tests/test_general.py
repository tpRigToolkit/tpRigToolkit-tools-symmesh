#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains general tests for tpRigToolkit
"""

from __future__ import print_function, division, absolute_import

import pytest

from tpDcc.libs.unittests.core import unittestcase

from tpRigToolkit.tools.symmesh import __version__


class VersionTests(unittestcase.UnitTestCase(as_class=True), object):

    def test_version(self):
        assert __version__.get_version()
