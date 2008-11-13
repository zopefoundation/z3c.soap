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
Test SOAP requests.

$Id$
"""

import unittest
from StringIO import StringIO
from zope.publisher.base import DefaultPublication
from zope.publisher.http import HTTPCharsets
from z3c.soap.publisher import SOAPRequest


class Publication(DefaultPublication):

    require_docstrings = 0

    def getDefaultTraversal(self, request, ob):
        if hasattr(ob, 'browserDefault'):
            return ob.browserDefault(request)
        return ob, ()


class TestSOAPRequest(SOAPRequest, HTTPCharsets):
    """Make sure that our request also implements IHTTPCharsets, so that we do
    not need to register any adapters."""

    def __init__(self, *args, **kw):
        self.request = self
        SOAPRequest.__init__(self, *args, **kw)


rpc_call = u'''<?xml version="1.0"?>
<SOAP-ENV:Envelope
 SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
 xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:xsd="http://www.w3.org/1999/XMLSchema"
 xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance">
 <SOAP-ENV:Body>
   <m:action xmlns:m="http://www.soapware.org/">
     <arg1 xsi:type="xsd:int">42</arg1>
   </m:action>
 </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
'''


class SOAPTests(unittest.TestCase):
    """ """

    _testEnv = {
        'PATH_INFO': '/folder/item2/view/',
        'QUERY_STRING': '',
        'SERVER_URL': 'http://foobar.com',
        'HTTP_HOST': 'foobar.com',
        'CONTENT_LENGTH': '0',
        'REQUEST_METHOD': 'POST',
        'HTTP_AUTHORIZATION': 'Should be in accessible',
        'GATEWAY_INTERFACE': 'TestFooInterface/1.0',
        'HTTP_OFF_THE_WALL': "Spam 'n eggs",
        'HTTP_ACCEPT_CHARSET': 'ISO-8859-1, UTF-8;q=0.66, UTF-16;q=0.33'}

    def setUp(self):
        super(SOAPTests, self).setUp()

        class AppRoot(object):
            pass

        class Folder(object):
            pass

        class Item(object):

            def __call__(self, a, b):
                return "%s, %s" % (`a`, `b`)

            def doit(self, a, b):
                return 'do something %s %s' % (a, b)

        class View(object):

            def action(self, a):
                return "Parameter[type: %s; value: %s" %(
                    type(a).__name__, `a`)

        class Item2(object):
            view = View()


        self.app = AppRoot()
        self.app.folder = Folder()
        self.app.folder.item = Item()
        self.app.folder.item2 = Item2()

    def _createRequest(self, extra_env={}, body=""):
        env = self._testEnv.copy()
        env.update(extra_env)
        if len(body):
            env['CONTENT_LENGTH'] = str(len(body))

        publication = Publication(self.app)
        instream = StringIO(body)
        request = TestSOAPRequest(instream, env)
        request.setPublication(publication)
        return request

    def testProcessInput(self):
        req = self._createRequest({}, rpc_call)
        req.processInputs()
        self.failUnlessEqual(req._args, (42, ))
        self.failUnlessEqual(tuple(req._path_suffix), ('action', ))

    def testTraversal(self):
        req = self._createRequest({}, rpc_call)
        req.processInputs()
        action = req.traverse(self.app)
        self.failUnlessEqual(action(*req._args),
                             "Parameter[type: int; value: 42")


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(SOAPTests)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
