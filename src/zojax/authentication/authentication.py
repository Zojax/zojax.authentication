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
import re
from threading import local

from ZODB.interfaces import IDatabase

from zope import interface, component
from zope.event import notify
from zope.component import getUtility, getUtilitiesFor, queryMultiAdapter #, getMultiAdapter
from zope.app.component import queryNextUtility
from zope.app.component.interfaces import ISite
from zope.app.security.interfaces import IAuthentication
from zope.app.publication.interfaces import IBeforeTraverseEvent

from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.authentication.interfaces import AuthenticatedPrincipalCreated
from zope.app.authentication.principalfolder import Principal
from zope.app.authentication.authentication import PluggableAuthentication

from interfaces import ILoginService
from interfaces import ICredentialsPlugin
from interfaces import IPrincipalInfoStorage
from interfaces import IActiveAuthenticatorPlugin
from interfaces import IPluggableAuthentication, IAuthenticationSettings
from interfaces import PrincipalLoggedInEvent, PrincipalLoggingOutEvent
from interfaces import PrincipalInitializedEvent, PrincipalInitializationFailed


class PluggableAuthentication(PluggableAuthentication):
    interface.implements(IPluggableAuthentication, IAuthenticationSettings)

    age = 3600
    pinfoStorage = 'ram'

    def getCredentialsPlugins(self):
        return self._plugins(self.credentialsPlugins, ICredentialsPlugin)

    def getAuthenticatorPlugins(self):
        for name in self.authenticatorPlugins:
            plugin = self.get(name)
            if not IAuthenticatorPlugin.providedBy(plugin):
                plugin = component.queryUtility(IAuthenticatorPlugin, name)
            if plugin is not None:
                yield name, plugin

        for name, plugin in getUtilitiesFor(IActiveAuthenticatorPlugin):
            yield name, plugin

    def authenticate(self, request):
        if isReadonly():
            storage = getUtility(IPrincipalInfoStorage, 'ram')
        else:
            storage = IPrincipalInfoStorage(self)

        # use cached PrincipalInfo
        try:
            info = storage.get(self, request)
            if info is not None:
                principal = Principal(
                    self.prefix + info.id, info.title, info.description)
                notify(AuthenticatedPrincipalCreated(
                        self, principal, info, request))
                return principal
        except PrincipalInitializationFailed, err:
            storage.clear(self, request)
            cache.loginMessage = err.message

        authenticatorPlugins = None
        for credname, credplugin in self.getCredentialsPlugins():
            # extract credentials
            credentials = credplugin.extractCredentials(request)
            if credentials is None:
                continue

            # authenticate credentials
            if authenticatorPlugins is None:
                authenticatorPlugins = list(self.getAuthenticatorPlugins())

            for authname, authplugin in authenticatorPlugins:
                try:
                    info = authplugin.authenticateCredentials(credentials)
                    if info is None:
                        continue

                    principal = Principal(
                        self.prefix + info.id, info.title, info.description)

                    notify(PrincipalInitializedEvent(principal, self))
                except PrincipalInitializationFailed, err:
                    cache.loginMessage = err.message
                    return

                notify(AuthenticatedPrincipalCreated(
                        self, principal, info, request))

                storage.store(self, request, info, credentials)

                notify(PrincipalLoggedInEvent(principal))
                return principal

    def unauthorized(self, id, request):
        # see #415 - workaround for MS Office products opening links
        # without a session in a browser, preventing logged users to see them
        ua = request.get('HTTP_USER_AGENT')
        uri = request.get('REQUEST_URI')

        if re.search('[^\w](Word|Excel|PowerPoint|ms-office)([^\w]|\z)', ua, re.I):
            return request.response.redirect(uri)

        login = queryMultiAdapter((self, request), ILoginService)
        if login is not None:
            if login.challenge():
                return

        next = queryNextUtility(self, IAuthentication)
        if next is not None:
            next.unauthorized(id, request)

    def logout(self, request):
        notify(PrincipalLoggingOutEvent(request.principal))

        if isReadonly():
            storage = getUtility(IPrincipalInfoStorage, 'ram')
        else:
            storage = IPrincipalInfoStorage(self)

        storage.clear(self, request)

    _caching = True

    def getPrincipal(self, id):
        if not self._caching:
            return super(PluggableAuthentication, self).getPrincipal(id)

        principals = cache.principals

        if id in principals:
            return principals[id]

        principal = super(PluggableAuthentication, self).getPrincipal(id)

        principals[id] = principal
        return principal

    @property
    def loginMessage(self):
        return cache.loginMessage


def isReadonly():
    readonly = False

    db = getUtility(IDatabase)
    conn = db.open()

    if conn.isReadOnly():
        readonly = True

    conn.close()

    return readonly


class Cache(local):
    principals = {}
    defaultcreds = None
    loginMessage = u''


cache = Cache()

@component.adapter(ISite, IBeforeTraverseEvent)
def beforeTraverseHandler(site, event):
    cache.principals = {}
    cache.defaultcreds = None
    cache.loginMessage = u''
