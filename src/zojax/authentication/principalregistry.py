##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

$Id$
"""
from zope import interface
from zope.app.security.principalregistry import principalRegistry
from zope.app.authentication.interfaces import IAuthenticatorPlugin

from interfaces import ISimpleCredentials


class PrincipalInfo(object):

    def __init__(self, principal):
        self.id = principal.id
        self.login = principal.getLogin()
        self.title = principal.title
        self.description = principal.description

    def __repr__(self):
        return 'PrincipalInfo(%r)' % self.id


class PrincipalRegistry(object):
    """ authenticator plugin for PrincipalRegistry """
    interface.implements(IAuthenticatorPlugin)

    prefix = u''

    def authenticateCredentials(self, credentials):
        if not ISimpleCredentials.providedBy(credentials):
            return None

        principal = principalRegistry._PrincipalRegistry__principalsByLogin.get(
            credentials.login)
        if principal is not None:
            if principal.validate(credentials.password):
                return PrincipalInfo(principal)

    def principalInfo(self, id):
        pass
