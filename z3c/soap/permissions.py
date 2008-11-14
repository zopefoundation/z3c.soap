# -*- coding: utf-8 -*-
"""
z3c.soap

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id$
"""
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles


security = ModuleSecurityInfo('z3c.soap.permissions')

security.declarePublic('SOAP Access')
SoapAccess = 'SOAP Access'
setDefaultRoles(SoapAccess, ('Authenticated', ))
