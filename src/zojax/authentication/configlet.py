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
from zope import event, interface
from zope.component import getSiteManager, getUtility
from zope.component.interfaces import IComponentLookup
from zope.proxy import sameProxiedObjects, removeAllProxies
from zope.lifecycleevent import ObjectCreatedEvent
from zope.traversing.interfaces import IContainmentRoot
from zope.app.intid.interfaces import IIntIds
from zope.app.component.hooks import getSite
from zope.app.security.interfaces import IAuthentication

from credentials import DefaultCredentialsPlugin
from authentication import PluggableAuthentication

from interfaces import IAuthenticationConfiglet, \
    IPluggableAuthentication, ICredentialsPluginFactory


class AuthenticationConfiglet(object):
    interface.implements(IAuthenticationConfiglet)

    def isInstalled(self):
        sm = getSiteManager()

        auth = sm.getUtility(IAuthentication)
        if not IPluggableAuthentication.providedBy(auth):
            return False

        return sameProxiedObjects(IComponentLookup(auth), sm)

    def installUtility(self):
        sm = getSiteManager()

        if 'auth' in sm:
            pau = sm[u'auth']
            sm.registerUtility(pau, IAuthentication)
            return

        portal = getSite()
        if IContainmentRoot.providedBy(portal):
            prefix = u''
        else:
            id = getUtility(IIntIds).queryId(removeAllProxies(portal))
            if not id:
                id = u''
            prefix = u'%s.'%id

        # PluggableAuthentication
        pau = PluggableAuthentication(prefix)
        event.notify(ObjectCreatedEvent(pau))
        sm[u'auth'] = pau
        sm.registerUtility(pau, IAuthentication)

        # Credentials Plugin
        factory = getUtility(ICredentialsPluginFactory, 'default.credentials')
        factory.install()
        factory.activate()

    def installPrincipalRegistry(self):
        pau = getSiteManager()['auth']
        if 'principalRegistry' not in pau.authenticatorPlugins:
            pau.authenticatorPlugins = pau.authenticatorPlugins + \
                ('principalRegistry',)

    def uninstallUtility(self, remove=False):
        sm = getSiteManager()

        if 'auth' in sm:
            pau = sm[u'auth']
            sm.unregisterUtility(pau, IAuthentication)

            if remove:
                del sm[u'auth']
