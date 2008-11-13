##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Functional tests for SOAP.

$Id$
"""

import sys
import os
import zope.interface
from zope.testing import doctest
from zope.app.folder.folder import IFolder
from zope.app.testing.functional import ZCMLLayer
from zope.app.testing import ztapi
from z3c.soap.interfaces import ISOAPRequest


# Evil hack to make pickling work with classes defined in doc tests


class NoCopyDict(dict):

    def copy(self):
        return self


class FakeModule:

    def __init__(self, dict):
        self.__dict = dict

    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError(name)


globs = NoCopyDict()
name = 'z3c.soap.README'


def setUp(test):
    globs['__name__'] = name
    sys.modules[name] = FakeModule(globs)


def tearDown(test):
    # clean up the views we registered:

    # we use the fact that registering None unregisters whatever is
    # registered. We can't use an unregistration call because that
    # requires the object that was registered and we don't have that handy.
    # (OK, we could get it if we want. Maybe later.)

    ztapi.provideView(IFolder,
                        ISOAPRequest,
                        zope.interface,
                        'contents',
                        None,
                        )
    ztapi.provideView(IFolder,
                        ISOAPRequest,
                        zope.interface,
                        'contents',
                        None,
                        )

    globs.clear()
    del sys.modules[name]


dir = os.path.abspath(os.path.dirname(__file__))
filename = os.path.join(dir, 'ftesting.zcml')

z3c_soap_functional_layer = ZCMLLayer(filename,
                                          __name__,
                                          'z3c.soap_functional_layer')


def test_suite():
    #from zope.app.testing.functional import FunctionalDocFileSuite
    from Testing.ZopeTestCase import FunctionalDocFileSuite
    ftest = FunctionalDocFileSuite(
        'README.txt',
        optionflags=doctest.ELLIPSIS|
                    doctest.REPORT_NDIFF|
                    doctest.REPORT_ONLY_FIRST_FAILURE|
                    doctest.NORMALIZE_WHITESPACE,
        setUp=setUp, tearDown=tearDown, globs=globs)
    ftest.layer = z3c_soap_functional_layer
    return ftest

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite')
