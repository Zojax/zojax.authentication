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
from zope.security.interfaces import IPrincipal
from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite

from zojax.statusmessage.interfaces import IStatusMessage
from zojax.authentication.interfaces import _, ISuccessLoginAction


class LoginAction(object):

    id = 'default.login'
    order = 1

    def update(self):
        self.loginURL = u'%s/login.html'%absoluteURL(getSite(), self.request)

    def isProcessed(self):
        return 'form.zojax-auth-login' in self.request


class SuccessLoginAction(object):
    interface.implements(ISuccessLoginAction)
    component.adapts(IPrincipal, interface.Interface)

    order = 1

    def __init__(self, principal, request):
        self.principal = principal
        self.request = request

    def __call__(self, nextURL=u''):
        request = self.request
        response = request.response

        IStatusMessage(request).add(_('You successfully logged in.'))

        if nextURL:
            response.redirect(nextURL)
        else:
            response.redirect('%s/'%absoluteURL(getSite(), request))

        return False
