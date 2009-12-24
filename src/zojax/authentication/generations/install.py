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
from zope.app.component.interfaces import ISite
from zope.app.zopeappgenerations import getRootFolder
from zope.dublincore.interfaces import ICMFDublinCore
from zope.app.publication.zopepublication import ZopePublication
from zope.app.generations.utility import findObjectsProviding
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import IPluggableAuthentication
from zope.app.component.site import setSite

from zojax.authentication.interfaces import ICredentialsPluginFactory

OLD_CRED_NAME = u'credentials'


def evolve(context):
    root = getRootFolder(context)

    for site in findObjectsProviding(root, ISite):
        sm = site.getSiteManager()

        pau = component.queryUtility(IAuthentication, context = sm)
        if pau is not None and IPluggableAuthentication.providedBy(pau):
            if OLD_CRED_NAME in pau:
                plugins = list(pau.credentialsPlugins)
                if OLD_CRED_NAME in plugins:
                    plugins.remove(OLD_CRED_NAME)
                    pau.credentialsPlugins = tuple(plugins)

                del pau[OLD_CRED_NAME]

            setSite(site)
            factory = component.getUtility(ICredentialsPluginFactory, 'default.credentials')
            factory.install()
            factory.activate()
            setSite(None)
