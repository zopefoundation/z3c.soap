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
SOAP interfaces.

$Id$
"""

from zope.publisher.interfaces.http import IHTTPRequest, IHTTPResponse
from zope.component.interfaces import IView, IPresentation
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import IPublication
from zope.interface import Interface


class ISOAPPublisher(IPublishTraverse):
    """SOAP Publisher"""


class ISOAPPublication(IPublication):
    """Object publication framework."""

    def getDefaultTraversal(request, ob):
        """Get the default published object for the request."""


class ISOAPRequest(IHTTPRequest):
    """SOAP Request"""


class ISOAPResponse(IHTTPResponse):
    """SOAP Response"""


class ISOAPPresentation(IPresentation):
    """SOAP presentation"""


class ISOAPView(ISOAPPresentation, IView):
    """SOAP View"""


class IZSIRequestType(Interface):
    """Resolver for complex request"""


class IZSIResponseType(Interface):
    """Resolver for complex response"""
