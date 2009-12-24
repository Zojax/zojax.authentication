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
from zope.component import getUtility, queryMultiAdapter
from zope.viewlet.viewlet import ViewletBase
from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zojax.authentication.interfaces import ILoginService


class LoginMenuItem(ViewletBase):

    weight = 9999

    def isAvailable(self):
        return self.manager.isAnonymous


class LoginPagelet(object):

    def __call__(self):
        request = self.request

        if not IUnauthenticatedPrincipal.providedBy(request.principal):
            request.response.redirect(u'%s/'%absoluteURL(getSite(), request))
            return u''

        auth = getUtility(IAuthentication)

        loginService = queryMultiAdapter((auth, request), ILoginService)

        if loginService is not None:
            loginService.challenge(u'%s/'%absoluteURL(self.context, request))
        else:
            request.response.redirect(
                u'%s/login.html'%absoluteURL(getSite(), request))

        return u''
