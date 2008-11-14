# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
import sys
from zExceptions import Redirect
from ZPublisher.mapply import mapply
from ZPublisher.Publish import (call_object, missing_name, dont_publish_class,
                                get_module_info, Retry)
from zope.publisher.browser import setDefaultSkin
from zope.security.management import newInteraction, endInteraction
from z3c.soap.interfaces import ISOAPRequest
from z3c.soap.soap import SOAPResponse


def publish(request, module_name, after_list, debug=0,
            call_object=call_object,
            missing_name=missing_name,
            dont_publish_class=dont_publish_class,
            mapply=mapply,
            ):

    (bobo_before, bobo_after, object, realm, debug_mode, err_hook,
     validated_hook, transactions_manager)= get_module_info(module_name)

    parents=None
    response=None

    try:
        # TODO pass request here once BaseRequest implements IParticipation
        newInteraction()

        request.processInputs()

        request_get=request.get
        response=request.response

        # First check for "cancel" redirect:
        if request_get('SUBMIT', '').strip().lower()=='cancel':
            cancel=request_get('CANCEL_ACTION', '')
            if cancel:
                raise Redirect(cancel)

        after_list[0]=bobo_after
        if debug_mode:
            response.debug_mode=debug_mode
        if realm and not request.get('REMOTE_USER', None):
            response.realm=realm

        if bobo_before is not None:
            bobo_before()

        # Get the path list.
        # According to RFC1738 a trailing space in the path is valid.
        path=request_get('PATH_INFO')

        request['PARENTS']=parents=[object]

        if transactions_manager:
            transactions_manager.begin()

        object=request.traverse(path, validated_hook=validated_hook)

        if transactions_manager:
            transactions_manager.recordMetaData(object, request)

        result=mapply(object, request.args, request,
                      call_object, 1,
                      missing_name,
                      dont_publish_class,
                      request, bind=1)

        if result is not response:
            response.setBody(result)

        if transactions_manager:
            transactions_manager.commit()
        endInteraction()

        return response
    except:
        # DM: provide nicer error message for FTP
        sm = None
        if response is not None:
            sm = getattr(response, "setMessage", None)
        if sm is not None:
            from asyncore import compact_traceback
            cl, val= sys.exc_info()[:2]
            sm('%s: %s %s' % (
                getattr(cl, '__name__', cl), val,
                debug_mode and compact_traceback()[-1] or ''))
        if ISOAPRequest.providedBy(request):
            if transactions_manager:
                transactions_manager.abort()
            endInteraction()
            if response is None:
                response = SOAPResponse(request.response)
            response.exception()
            return response
        if err_hook is not None:
            if parents:
                parents=parents[0]
            try:
                try:
                    return err_hook(parents, request,
                                    sys.exc_info()[0],
                                    sys.exc_info()[1],
                                    sys.exc_info()[2],
                                    )
                except Retry:
                    if not request.supports_retry():
                        return err_hook(parents, request,
                                        sys.exc_info()[0],
                                        sys.exc_info()[1],
                                        sys.exc_info()[2],
                                        )
            finally:
                if transactions_manager:
                    transactions_manager.abort()
                endInteraction()

            # Only reachable if Retry is raised and request supports retry.
            newrequest=request.retry()
            request.close()  # Free resources held by the request.
            # Set the default layer/skin on the newly generated request
            setDefaultSkin(newrequest)
            try:
                return publish(newrequest, module_name, after_list, debug)
            finally:
                newrequest.close()

        else:
            if transactions_manager:
                transactions_manager.abort()
            endInteraction()
            raise

import ZPublisher.Publish
ZPublisher.Publish.publish = publish

from Products.PluggableAuthService.plugins.CookieAuthHelper import CookieAuthHelper
from urllib import quote


def unauthorized(self):
        req = self.REQUEST
        resp = req['RESPONSE']

        # If we set the auth cookie before, delete it now.
        if self.cookie_name in resp.cookies:
            del resp.cookies[self.cookie_name]

        # Redirect if desired.
        url = self.getLoginURL()
        if ISOAPRequest.providedBy(req):
            #no need to redirect if it's a soap request
            return 0

        if url is not None:
            came_from = req.get('came_from', None)

            if came_from is None:
                came_from = req.get('URL', '')
                query = req.get('QUERY_STRING')
                if query:
                    if not query.startswith('?'):
                        query = '?' + query
                    came_from = came_from + query
            else:
                # If came_from contains a value it means the user
                # must be coming through here a second time
                # Reasons could be typos when providing credentials
                # or a redirect loop (see below)
                req_url = req.get('URL', '')

                if req_url and req_url == url:
                    # Oops... The login_form cannot be reached by the user -
                    # it might be protected itself due to misconfiguration -
                    # the only sane thing to do is to give up because we are
                    # in an endless redirect loop.
                    return 0

            url = url + '?came_from=%s' % quote(came_from)
            resp.redirect(url, lock=1)
            return 1

        # Could not challenge.
        return 0

CookieAuthHelper.unauthorized = unauthorized
