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
from zope.proxy import sameProxiedObjects
from zope.component import getUtility, getSiteManager
from zope.component import queryUtility, getUtilitiesFor
from zope.component.interfaces import IComponentLookup

from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import \
    IAuthenticatorPlugin, ICredentialsPlugin, IPluggableAuthentication

from zope.app.component.hooks import getSite

from zojax.layoutform import interfaces, button, Fields, PageletEditForm
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.authentication.interfaces import \
    _, IAuthenticatorPluginFactory, ICredentialsPluginFactory,\
    IAuthenticationSettings


class ConfigletView(PageletEditForm):

    fields = Fields(IAuthenticationSettings)

    buttons = PageletEditForm.buttons.copy()
    handlers = PageletEditForm.handlers.copy()

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__

    def getContent(self):
        return getUtility(IAuthentication)

    @button.buttonAndHandler(
        _(u'Uninstall'), name='uninstall', provides=interfaces.ICancelButton)
    def uninstallHandler(self, action):
        self.context.uninstallUtility(True)
        IStatusMessage(self.request).add(
            _('Authentication service has been uninstalled.'))
        self.redirect(self.request.URL)

    def _installPlugins(self, factoryIds, iface, message):
        installed = False

        for name in factoryIds:
            factory = queryUtility(iface, name)
            if factory is not None:
                factory.install()
                factory.activate()
                installed = True

        if installed:
            IStatusMessage(self.request).add(message)

    def _uninstallPlugins(self, pluginIds, iface, message):
        uninstalled = False

        for name in pluginIds:
            factory = queryUtility(iface, name)
            if factory is not None:
                factory.uninstall()
                uninstalled = True

        if uninstalled:
            IStatusMessage(self.request).add(message)

    def _changeState(self, pluginId, iface, message):
        factory = queryUtility(iface, pluginId)
        if factory is not None:
            if factory.isActive():
                factory.deactivate()
            else:
                factory.activate()

            IStatusMessage(self.request).add(message)

    def _installedPlugins(self, factoryIface, pluginIface):
        sm = getSiteManager()

        installed = []
        for name, factory in getUtilitiesFor(factoryIface):
            plugin = queryUtility(pluginIface, name)
            if plugin is not None and \
                    sameProxiedObjects(IComponentLookup(plugin), sm):
                config = self.context.get(factory.name)
                if config is not None and config.isAvailable():
                    configurable = True
                else:
                    configurable = False

                info = {'name': factory.name,
                        'title': factory.title,
                        'description': factory.description,
                        'active': factory.isActive(),
                        'configurable': configurable}

                installed.append((factory.title, factory.name, info))

        installed.sort()
        return [data for t,n,data in installed], \
            [name for t, name, d in installed]

    def update(self):
        request = self.request

        auth = getUtility(IAuthentication)
        self.isPluggable = self.context.isInstalled()

        self.installed = []
        self.installed_names = []

        self.installedCred = []
        self.installedCred_names = []

        if 'form.authinstall' in request:
            self.context.installUtility()
            IStatusMessage(request).add(
                _('Authentication service has been installed.'))
            self.redirect(request.URL)

        if self.isPluggable:
            super(ConfigletView, self).update()
        else:
            return

        if 'form.install' in request:
            self._installPlugins(
                request.get('factory_ids', ()),
                IAuthenticatorPluginFactory,
                _('Authenticator plugins have been installed.'))

        if 'form.cred_install' in request:
            self._installPlugins(
                request.get('cred_factory_ids', ()),
                ICredentialsPluginFactory,
                _('Credentials plugins have been installed.'))

        elif 'form.uninstall' in request:
            self._uninstallPlugins(
                request.get('plugin_ids', ()),
                IAuthenticatorPluginFactory,
                _('Authenticator plugins have been uninstalled.'))

        elif 'form.cred_uninstall' in request:
            self._uninstallPlugins(
                request.get('cred_plugin_ids', ()),
                ICredentialsPluginFactory,
                _('Credentials plugins have been uninstalled.'))

        elif 'change_state' in request:
            self._changeState(
                request['change_state'],
                IAuthenticatorPluginFactory,
                _("Authenticator plugin's status has been changed."))

        elif 'cred_change_state' in request:
            self._changeState(
                request['cred_change_state'],
                ICredentialsPluginFactory,
                _("Credentials plugin's status has been changed."))

        # prepare plugin info
        if self.isPluggable:
            self.installed, self.installed_names = self._installedPlugins(
                IAuthenticatorPluginFactory, IAuthenticatorPlugin)

            self.installedCred, self.installedCred_names = \
                self._installedPlugins(
                ICredentialsPluginFactory, ICredentialsPlugin)

    def _listFactories(self, iface, names):
        factories = []
        for name, factory in getUtilitiesFor(iface):
            if name not in names and factory.isAvailable():
                factories.append((factory.title, name, factory.description))

        factories.sort()
        return factories

    def listFactories(self):
        return self._listFactories(
            IAuthenticatorPluginFactory, self.installed_names)

    def listCredentialsFactories(self):
        return self._listFactories(
            ICredentialsPluginFactory, self.installedCred_names)
