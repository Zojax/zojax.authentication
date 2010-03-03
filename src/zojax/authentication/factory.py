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
from zope import interface, event
from zope.component import getUtility, queryUtility, getSiteManager
from zope.lifecycleevent import ObjectCreatedEvent
from zope.security.proxy import removeSecurityProxy
from zope.component.interfaces import IComponentLookup
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import ICredentialsPlugin
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.authentication.interfaces import IPluggableAuthentication

from interfaces import _, IPluginFactory
from interfaces import IAuthenticatorPluginFactory, ICredentialsPluginFactory


class PluginFactory(object):
    interface.implements(IPluginFactory)

    pluginNames = None
    pluginInterface = None

    def __init__(self, name, factory, interfaces, title, description=''):
        self.name = name
        self.factory = factory
        self.title = title
        self.description = description
        self.interfaces = interfaces

    @property
    def plugin(self):
        return queryUtility(self.pluginInterface, self.name)

    @property
    def auth(self):
        return getUtility(IAuthentication)

    def install(self):
        auth = self.auth
        if not IPluggableAuthentication.providedBy(auth):
            raise ValueError(_("Can't create authenticator plugin."))

        plugin = self.factory()
        event.notify(ObjectCreatedEvent(plugin))

        auth = removeSecurityProxy(auth)
        if self.name in auth:
            del auth[self.name]

        auth[self.name] = plugin

        sm = getSiteManager()
        for iface, name in (self.interfaces +
                            ((self.pluginInterface, self.name),)):
            sm.registerUtility(plugin, iface, name)

    def uninstall(self):
        self.deactivate()

        auth = self.auth

        if not IPluggableAuthentication.providedBy(auth):
            return

        if self.name not in auth:
            return

        plugin = auth[self.name]

        sm = getSiteManager()
        for iface, name in (self.interfaces +
                            ((self.pluginInterface, self.name),)):
            sm.unregisterUtility(plugin, iface, name=name)

        del auth[self.name]

    def isActive(self):
        auth = self.auth

        if IPluggableAuthentication.providedBy(auth):
            return self.name in getattr(auth, self.pluginNames)

        return False

    def activate(self):
        plugin = self.plugin

        if plugin is None:
            return

        auth = self.auth

        if IPluggableAuthentication.providedBy(auth):
            setattr(auth, self.pluginNames,
                    tuple(set(getattr(auth, self.pluginNames) + (self.name,))))

    def deactivate(self):
        plugin = self.plugin

        if plugin is None:
            return

        auth = self.auth

        if IPluggableAuthentication.providedBy(auth):
            plugins = set(getattr(auth, self.pluginNames))
            if self.name in plugins:
                plugins.remove(self.name)
                setattr(auth, self.pluginNames, tuple(plugins))

    def isAvailable(self):
        return True


class AuthenticatorPluginFactory(PluginFactory):
    interface.implementsOnly(IAuthenticatorPluginFactory)

    pluginNames = 'authenticatorPlugins'
    pluginInterface = IAuthenticatorPlugin


class CredentialsPluginFactory(PluginFactory):
    interface.implementsOnly(ICredentialsPluginFactory)

    pluginNames = 'credentialsPlugins'
    pluginInterface = ICredentialsPlugin
