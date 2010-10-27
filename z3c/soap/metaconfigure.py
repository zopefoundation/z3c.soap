##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
SOAP configuration code

$Id$
"""

from zope.interface import Interface
from zope.security.checker import CheckerPublic
from zope.component.interface import provideInterface
from Products.Five.security import protectClass, protectName
from zope.app.publisher.browser.viewmeta import _handle_for

# XXX handler is non-public.  Should call directives instead
try:
	from zope.app.component.metaconfigure import handler
except ImportError:
	from zope.component.zcml import handler

from inspect import ismethod
from interfaces import ISOAPRequest
from Globals import InitializeClass as initializeClass
from Products.Five.security import getSecurityInfo
from Products.Five.metaclass import makeClass

from Products.Five.browser import BrowserView
from Products.Five.browser.metaconfigure import ViewMixinForAttributes
from Products.Five.security import CheckerPrivateId


def view(_context, for_=None, interface=None, methods=None,
         class_=None, permission=None, name=None):

    interface = interface or []
    methods = methods or []

    # If there were special permission settings provided, then use them
    if permission == 'zope.Public':
        permission = CheckerPublic

    require = {}
    for attr_name in methods:
        require[attr_name] = permission

    if interface:
        for iface in interface:
            for field_name in iface:
                require[field_name] = permission
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = ('', for_))

    cdict = getSecurityInfo(class_)

    if name:
        cdict['__name__'] = name
        new_class = makeClass(class_.__name__,
                              (class_, BrowserView), cdict)

        _handle_for(_context, for_)
        # Register the new view.
        _context.action(
            discriminator = ('view', (for_, ), name, ISOAPRequest),
            callable = handler,
            args = ('registerAdapter',
                    new_class, (for_, ISOAPRequest),
                    Interface, name,
                    _context.info)
            )
        _context.action(
            discriminator = ('five:protectClass', new_class),
            callable = protectClass,
            args = (new_class, permission))

        for name in require:
            _context.action(
                discriminator = ('five:protectName', new_class, name),
                callable = protectName,
                args = (new_class, name, permission))

        #else its private:
        allowed = require
        private_attrs = [name for name in dir(new_class)
                         if (not name.startswith('_')) and
                            (name not in allowed) and
                            ismethod(getattr(new_class, name))]
        for attr in private_attrs:
            _context.action(
                discriminator = ('five:protectName', new_class, attr),
                callable = protectName,
                args = (new_class, attr, CheckerPrivateId))

    else:
        for name in require:
            cdict.update({'__page_attribute__': name,
                          '__name__': name})
            new_class = makeClass(class_.__name__,
                                  (class_, ViewMixinForAttributes),
                                  cdict)

            func = getattr(new_class, name)
            if not func.__doc__:
                # cannot test for MethodType/UnboundMethod here
                # because of ExtensionClass
                if hasattr(func, 'im_func'):
                    # you can only set a docstring on functions, not
                    # on method objects
                    func = func.im_func
                func.__doc__ = "Stub docstring to make ZPublisher work"

            _context.action(
                discriminator = ('view', (for_, ), name, ISOAPRequest),
                callable = handler,
                args = ('registerAdapter',
                        new_class,
                        (for_, ISOAPRequest), Interface, name,
                        _context.info))

            _context.action(
                discriminator = ('five:protectClass', new_class),
                callable = protectClass,
                args = (new_class, permission))

            _context.action(
                discriminator = ('five:protectName', new_class, name),
                callable = protectName,
                args = (new_class, name, permission))

            _context.action(
                discriminator = ('five:initialize:class', new_class),
                callable = initializeClass,
                args = (new_class, )
                )

    # Register the used interfaces with the interface service
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_))
