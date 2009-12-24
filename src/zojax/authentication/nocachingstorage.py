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
from zope import interface, component
from zope.traversing.api import getPath
from zope.session.interfaces import ISession
from zope.component import queryUtility, getUtilitiesFor
from zope.app.authentication.interfaces import IPluggableAuthentication

from interfaces import _, SESSION_ID, IPrincipalInfoStorage, ICredentialsUpdater


class NoCachingStorage(object):
    interface.implements(IPrincipalInfoStorage)

    name = _('No Caching storage')

    def get(self, authentication, request):
        session = ISession(request)

        if 'credentials' in session[SESSION_ID]:
            creds = session[SESSION_ID]['credentials']

            for name, authplugin in authentication.getAuthenticatorPlugins():
                info = authplugin.authenticateCredentials(creds)
                if info is not None:
                    return info

            del session[SESSION_ID]['credentials']

    def clear(self, authentication, request, principal=None):
        if principal is not None and request.principal.id != principal.id:
            return

        session = ISession(request)

        if 'credentials' in session[SESSION_ID]:
            del session[SESSION_ID]['credentials']

    def store(self, authentication, request, principalInfo, credentials):
        ISession(request)[SESSION_ID]['credentials'] = credentials
