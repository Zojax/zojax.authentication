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
import os
import unittest, doctest
from zope import interface, component, event
from zope.component import getUtility
from zope.app.testing import setup
from zope.app.testing.functional import ZCMLLayer
from zope.app.rotterdam import Rotterdam
from zope.session import session
from zope.app.component.hooks import getSite, setSite
from zope.app.testing import functional
from zope.app.security.interfaces import IAuthentication
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectCreatedEvent

from zojax.layoutform.interfaces import ILayoutFormLayer

from zojax.authentication import principalinfo
from zojax.authentication.authentication import PluggableAuthentication
from zojax.authentication.interfaces import ICredentialsPluginFactory
from zojax.authentication.credentials import factory as defaultCreds


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


zojaxAuthentication = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxAuthentication', allow_teardown=True)


def setUp(test):
    site = setup.placefulSetUp(True)
    site.__name__ = u'portal'

    setSite(site)
    sm = site.getSiteManager()

    # PluggableAuthentication
    pau = PluggableAuthentication(u'')
    event.notify(ObjectCreatedEvent(pau))
    sm[u'auth'] = pau
    sm.registerUtility(pau, IAuthentication)

    # Credentials Plugin
    defaultCreds.install()
    defaultCreds.activate()

    setup.setUpTestAsModule(test, name='zojax.authentication.TESTS')


def tearDown(test):
    site = getSite()

    sm = site.getSiteManager()

    # Credentials Plugin
    defaultCreds.deactivate()
    defaultCreds.uninstall()

    # PluggableAuthentication
    sm.unregisterUtility(sm['auth'], IAuthentication)
    del sm['auth']

    setup.placefulTearDown()
    setup.tearDownTestAsModule(test)


def setUpAuth(test):
    site = setup.placefulSetUp(True)
    site.__name__ = u'portal'

    component.provideAdapter(session.ClientId)

    component.provideAdapter(principalinfo.getPrincipalInfoStorage)
    component.provideUtility(
        principalinfo.RAMCachePrincipalInfoStorage(), name='ram')

    setup.setUpTestAsModule(test, name='zojax.authentication.TESTS')


def tearDownAuth(test):
    setup.placefulTearDown()
    setup.tearDownTestAsModule(test)


def FunctionalDocFileSuite(*paths, **kw):
    layer = zojaxAuthentication

    globs = kw.setdefault('globs', {})
    globs['http'] = functional.HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kw['package'] = doctest._normalize_module(kw.get('package'))

    kwsetUp = kw.get('setUp')
    def setUp(test):
        functional.FunctionalTestSetup().setUp()

        root = functional.getRootFolder()
        sm = root.getSiteManager()

        # IIntIds
        root['ids'] = IntIds()
        sm.registerUtility(root['ids'], IIntIds)
        root['ids'].register(root)

    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        setSite(None)
        functional.FunctionalTestSetup().tearDown()

    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old|doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite


def test_suite():
    auth = doctest.DocFileSuite(
        '../README.ru',
        setUp=setUpAuth, tearDown=tearDownAuth,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)

    factory = doctest.DocFileSuite(
        'factory.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)

    configlet = FunctionalDocFileSuite("configlet.txt")
    login = FunctionalDocFileSuite("login.txt")

    return unittest.TestSuite((login, auth, factory, configlet))
