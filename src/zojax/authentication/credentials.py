##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

from authentication import cache
from factory import CredentialsPluginFactory
from interfaces import _, ISimpleCredentials, IDefaultCredentialsPlugin


class SimpleCredentials(object):
    interface.implements(ISimpleCredentials)

    principalinfo = None

    def __init__(self, login, password):
        self.login = login
        self.password = password


class DefaultCredentialsPlugin(Contained):
    interface.implements(IDefaultCredentialsPlugin)

    loginfield = 'zojax-login'
    passwordfield = 'zojax-password'
    submitfield = 'form.zojax-auth-login'

    def extractCredentials(self, request):
        global cache

        if cache.defaultcreds is not None:
            creds, temp = cache.defaultcreds
            if temp:
                cache.defaultcreds = None
            return creds
        else:
            if self.submitfield in request:
                login = request.get(self.loginfield, None)
                password = request.get(self.passwordfield, None)
                if login is not None and password is not None:
                    return SimpleCredentials(login, password)

    def updateCredentials(self, request, creds, temp=False):
        if ISimpleCredentials.providedBy(creds):
            global cache
            cache.defaultcreds = (creds, temp)


import array, hmac
def _strxor(s1, s2):
    """Utility method. XOR the two strings s1 and s2 (must have same length).
    """
    a1 = array.array('B')
    a1.fromstring(s1)
    a2 = array.array('B')
    a2.fromstring(s2)
    return array.array('B', [x ^ y for x, y in zip(a1, a2)]).tostring()

hmac._strxor = _strxor

FACTORY_NAME = 'default.credentials'

factory = CredentialsPluginFactory(
    FACTORY_NAME, DefaultCredentialsPlugin, (),
    _('Default credentials plugin'),
    _('Extract credentials after submit form with login and password.'))
