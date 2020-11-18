.. caution:: 

    This repository has been archived. If you want to work on it please open a ticket in https://github.com/zopefoundation/meta/issues requesting its unarchival.

SOAP Support
============

This SOAP implementation allows you provide SOAP views for objects. The
SOAP layer is based on `ZSI <http://pywebsvcs.sourceforge.net/>`__.

The package requires ZSI 2.0 or better.

SOAP support is implemented in a way very similar to the standard Zope
XML-RPC support.  To call methods via SOAP, you need to create and
register SOAP views.

Version >= 0.5.4 are intended to be used with Zope 2.13 and higher.
Older versions (0.5.3 and under) should work correctly with Zope < 2.13

This package is largely inspired from Zope 3 SOAP (http://svn.zope.org/soap).
