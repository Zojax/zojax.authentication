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
from zope import event
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.security.interfaces import IAuthentication

from zojax.authentication.credentials import DefaultCredentialsPlugin
from zojax.authentication.authentication import PluggableAuthentication


def installAuthentication(portal):
    sm = portal.getSiteManager()

    if 'auth' in sm:
        return

    if portal.__name__ is None:
        # maybe IRootFolder
        prefix = ''
    else:
        prefix = '%s.'%portal.__name__

    # PluggableAuthentication
    pau = PluggableAuthentication(prefix)
    event.notify(ObjectCreatedEvent(pau))
    sm[u'auth'] = pau
    sm.registerUtility(pau, IAuthentication)

    # Credentials Plugin
    creds = DefaultCredentialsPlugin()
    event.notify(ObjectCreatedEvent(creds))
    pau[u'credentials'] = creds

    # set plugins
    pau.credentialsPlugins = [u'credentials']


def uninstallAuthentication(portal):
    sm = portal.getSiteManager()

    if 'auth' not in sm:
        return

    pau = sm[u'auth']
    sm.unregisterUtility(pau, IAuthentication)

    del sm[u'auth']
