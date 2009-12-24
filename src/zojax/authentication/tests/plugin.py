##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
from zope.app.container.contained import Contained
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zojax.authentication.factory import AuthenticatorPluginFactory


class IAuthPlugin(interface.Interface):
    """ auth plugin """


class PrincipalInfo(object):
    interface.implements(IPrincipalInfo)

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description


class AuthPlugin(Contained):
    interface.implements(IAuthenticatorPlugin, IAuthPlugin)

    def __init__(self, title='Test Auth Plugin', prefix='zojax.test'):
        self.prefix = unicode(prefix)
        self.title = title

    def authenticateCredentials(self, credentials):
        if credentials.login == 'bob' and \
               credentials.password == 'secretcode':
            return PrincipalInfo('bob', 'Bob', '')


factory = AuthenticatorPluginFactory(
    'auth.plugin', AuthPlugin, ((IAuthPlugin, ''),), u'Test Auth Plugin', u'')
