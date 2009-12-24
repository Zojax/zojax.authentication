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
from zope import interface
from zope.component import getUtility
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal


class LogoutView(object):

    def update(self):
        request = self.request
        nextURL = request.get('nextURL')

        if not IUnauthenticatedPrincipal.providedBy(request.principal):
            getUtility(IAuthentication).logout(request)

        if nextURL:
            self.redirect(nextURL)
        elif not IUnauthenticatedPrincipal.providedBy(request.principal):
            self.redirect('logout.html')
