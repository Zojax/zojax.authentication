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
from urllib import unquote

from zope import interface
from zope.component import getUtility, queryUtility, queryMultiAdapter
from zope.app.component.hooks import getSite
from zope.traversing.browser import absoluteURL
from zope.app.security.browser.auth import HTTPBasicAuthenticationLogin
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.authentication.interfaces import IPluggableAuthentication

from zojax.statusmessage.interfaces import IStatusMessage

from zojax.authentication.interfaces import _, ILoginAction
from zojax.authentication.interfaces import ILoginService, ISuccessLoginAction

try:
    hasRegistration = True
    from zojax.principal.registration.interfaces import IPortalRegistration
except ImportError:
    hasRegistration = False


class LoginForm(HTTPBasicAuthenticationLogin):

    title = _('Login')

    logins = ()
    processed = False
    join = False

    def update(self):
        request = self.request

        self.portal = getSite()
        self.portalURL = absoluteURL(self.portal, request)
        self.loginURL = '%s/@@login.html'%self.portalURL

        self.isAnonymous = IUnauthenticatedPrincipal.providedBy(
            request.principal)

        if hasRegistration:
            if self.isAnonymous:
                configlet = queryUtility(IPortalRegistration)
                try:
                    if configlet.getActions().next():
                        self.join = True
                except:
                    pass

        auth = getUtility(IAuthentication)
        loginService = queryMultiAdapter((auth, request), ILoginService)
        if loginService is None:
            if self.isAnonymous:
                request.unauthorized('basic realm="Zope"')
                return self.failed()
            else:
                return self.redirect(self.portalURL)

        self.logins = loginService.challengingActions()

        for action in self.logins:
            if action.isProcessed():
                self.processed = True
                break

        if self.processed:
            if not self.isAnonymous:
                loginService.success()
                return
            else:
                msg = auth.loginMessage
                if not msg:
                    msg = _('Login failed.')

                IStatusMessage(request).add(msg, 'warning')
                return
        else:
            try:
                auth.getAuthenticatorPlugins().next()
            except StopIteration:
                return self.login()
