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
SOAP Publisher.

$Id$
"""

import ZSI
from zope.app.publication.interfaces import ISOAPRequestFactory
from zope.publisher.http import HTTPRequest, HTTPResponse
from z3c.soap.interfaces import ISOAPRequest, ISOAPResponse
from ZSI import TC, ParsedSoap, ParseException
from ZSI import SoapWriter, Fault
from zope.security.proxy import isinstance
from zope.security.interfaces import IUnauthorized
from zope.publisher.xmlrpc import premarshal
from zope.interface import implements
from StringIO import StringIO
import traceback


class SOAPRequestFactory(object):
    """
    This class implements a SOAP request factory that is registered
    for zope.app.publication.interfaces.ISOAPRequestFactory as a
    utility. This lets the hook in the z3 publisher delegate to us
    for SOAP requests.
    """
    implements(ISOAPRequestFactory)

    def __call__(self, input, env):
        return SOAPRequest(input, env)

factory = SOAPRequestFactory()


class SOAPRequest(HTTPRequest):

    implements(ISOAPRequest)

##     __slots__ = (
##         '_target',
##         '_root',
##         )

    _target = ''
    _root = None
    _args = ()

    def _getPositionalArguments(self):
        return self._args

    def _createResponse(self):
        """Create a specific SOAP response object."""
        return SOAPResponse()

    def _setError(self, error):
        self._getResponse()._error = error

    def processInputs(self):
        try:
            input = self._body_instream.read()
            parsed = ParsedSoap(input)

            # We do not currently handle actors or mustUnderstand elements.
            actors = parsed.WhatActorsArePresent()
            if len(actors):
                self._setError(ZSI.FaultFromActor(actors[0]))
                return

            must = parsed.WhatMustIUnderstand()
            if len(must):
                uri, localname = must[0]
                self._setError(ZSI.FaultFromNotUnderstood(uri, localname))
                return

        except ParseException, e:
            self._setError(ZSI.FaultFromZSIException(e))
            return

        except Exception, e:
            self._setError(ZSI.FaultFromException(e, 1))
            return

        # Parse the SOAP input.
        try:
            docstyle = 0 # cant really tell...
            resolver = None # XXX
            root = self._root = parsed.body_root
            target = self._target = root.localName

            self.setPathSuffix(target.split('.'))

            if docstyle:
                self._args = (root)
            else:
                data = ZSI._child_elements(root)
                if len(data) == 0:
                    self._args = ()
                else:
                    try:
                        try:
                            type = data[0].localName
                            tc = getattr(resolver, type).typecode
                        except Exception, e:
                            tc = TC.Any()
                        self._args = [tc.parse(e, parsed) for e in data]
                        self._args = tuple(self._args)
                    except ZSI.EvaluateException, e:
                        self._error = ZSI.FaultFromZSIException(e)
                    return

        except Exception, e:
            self._setError(ZSI.FaultFromException(e, 0))


class SOAPResponse(HTTPResponse):

    implements(ISOAPResponse)

    _error = None

    def setBody(self, body):
        """Sets the body of the response"""
        # A SOAP view can return a Fault directly to indicate an error.
        if isinstance(body, Fault):
            self._error = body

        if not self._error:
            try:
                target = self._request._target
                body = premarshal(body)
                output = StringIO()
                result = body

                if hasattr(result, 'typecode'):
                    tc = result.typecode
                else:
                    tc = TC.Any(aslist=1, pname=target + 'Response')
                    result = [result]

                SoapWriter(output).serialize(result, tc)
                output.seek(0)

                if not self._status_set:
                    self.setStatus(200)
                self.setHeader('content-type', 'text/xml')
                self._body = output.read()
                self._updateContentLength()
                return

            except Exception, e:
                self._error = ZSI.FaultFromException(e, 0)

        # Error occurred in input, during parsing or during processing.
        self.setStatus(500)
        self.setHeader('content-type', 'text/xml')
        self.setResult(self._error.AsSOAP())
        #self._updateContentLength()

    def handleException(self, exc_info):
        """Handle exceptions that occur during processing."""
        type, value = exc_info[:2]
        content = "".join(traceback.format_tb(exc_info[-1]))
        if IUnauthorized.providedBy(value):
            self.setStatus(401)
            self.setBody("")
            #XXXself._body = ""
            #self._updateContentLength()
            return
        if not isinstance(value, Fault):
            value = ZSI.FaultFromException(u"%s : %s" % (value, content), 0)
        self.setStatus(500)
        self.setBody(value)
