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
SOAP Publication Tests

$Id$
"""
import unittest

from zope.app.publication.tests.test_zopepublication import \
     BasePublicationTests
from zope.app.publication.traversers import TestTraverser
from zope.app.publication.soap import SOAPPublication
from zope.interface import Interface, implements
from zope.proxy import removeAllProxies
from zope.publisher.interfaces import NotFound
from z3c.soap.interfaces import ISOAPPresentation, ISOAPRequest
from z3c.soap.interfaces import ISOAPPublisher
from z3c.soap.publisher import SOAPRequest
from zope.app.testing import ztapi
from StringIO import StringIO


class TestRequest(SOAPRequest):

    def __init__(self, body_instream=None, environ=None,
                 response=None, **kw):

        _testEnv = {
            'SERVER_URL': 'http://127.0.0.1',
            'HTTP_HOST': '127.0.0.1',
            'CONTENT_LENGTH': '0',
            'GATEWAY_INTERFACE': 'TestFooInterface/1.0'}

        if environ:
            _testEnv.update(environ)
        if kw:
            _testEnv.update(kw)
        if body_instream is None:
            body_instream = StringIO('')

        super(TestRequest, self).__init__(
            body_instream, _testEnv, response)


class SimpleObject(object):

    def __init__(self, v):
        self.v = v


class SOAPPublicationTests(BasePublicationTests):

    klass = SOAPPublication

    def _createRequest(self, path, publication, **kw):
        request = TestRequest(PATH_INFO=path, **kw)
        request.setPublication(publication)
        return request

    def testTraverseName(self):
        pub = self.klass(self.db)

        class C(object):
            x = SimpleObject(1)
        ob = C()
        r = self._createRequest('/x', pub)
        ztapi.provideView(None, ISOAPRequest, ISOAPPublisher,
                          '', TestTraverser)
        ob2 = pub.traverseName(r, ob, 'x')
        self.assertEqual(removeAllProxies(ob2).v, 1)

    def testDenyDirectMethodAccess(self):
        pub = self.klass(self.db)

        class I(Interface):
            pass

        class C(object):
            implements(I)

            def foo(self):
                return 'bar'

        class V(object):

            def __init__(self, context, request):
                pass
            implements(ISOAPPresentation)

        ob = C()
        r = self._createRequest('/foo', pub)

        ztapi.provideView(I, ISOAPPresentation, Interface, 'view', V)
        ztapi.setDefaultViewName(I, 'view', type=ISOAPPresentation)
        self.assertRaises(NotFound, pub.traverseName, r, ob, 'foo')

    def testTraverseNameView(self):
        pub = self.klass(self.db)

        class I(Interface):
            pass

        class C(object):
            implements(I)

        ob = C()

        class V(object):

            def __init__(self, context, request):
                pass
            implements(ISOAPPresentation)


        # Register the simple traverser so we can traverse without @@
        from z3c.soap.interfaces import ISOAPPublisher, ISOAPRequest
        from zope.app.publication.traversers import SimpleComponentTraverser
        ztapi.provideView(Interface, ISOAPRequest, ISOAPPublisher, '',
                          SimpleComponentTraverser)

        r = self._createRequest('/@@spam', pub)
        ztapi.provideView(I, ISOAPRequest, Interface, 'spam', V)
        ob2 = pub.traverseName(r, ob, '@@spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)

        ob2 = pub.traverseName(r, ob, 'spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)

    def testTraverseNameServices(self):
        pub = self.klass(self.db)

        class C(object):

            def getSiteManager(self):
                return SimpleObject(1)
        ob = C()
        r = self._createRequest('/++etc++site', pub)
        ob2 = pub.traverseName(r, ob, '++etc++site')
        self.assertEqual(removeAllProxies(ob2).v, 1)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SOAPPublicationTests),
        ))

if __name__ == '__main__':
    unittest.main()
