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
"""Login and Logout screens

$Id$
"""
import urllib
from zope import interface, component
from zope.component import getAdapters, getMultiAdapter, queryMultiAdapter
from zope.session.interfaces import ISession
from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import IPluggableAuthentication

from interfaces import \
    SESSION_ID, ILoginAction, ILoginService, ISuccessLoginAction


class LoginService(object):
    interface.implements(ILoginService)
    component.adapts(IPluggableAuthentication, interface.Interface)

    def __init__(self, auth, request):
        self.context = auth
        self.request = request

    def challenge(self, nextURL=u''):
        context = self.context
        request = self.request

        actions = {}
        for name, creds in context.getCredentialsPlugins():
            action = queryMultiAdapter((creds, request), ILoginAction)
            if action is not None and action.id not in actions:
                action.update()
                actions[action.id] = action

        if not actions:
            return False

        if not nextURL:
            nextURL = self._generateNextURL()

        if not request.getHeader('X-Requested-With', ''):
            ISession(request)[SESSION_ID]['nextURL'] = nextURL
        request.response.redirect(
            '%s/login.html'%absoluteURL(getSite(), request))
        return True

    def nextURL(self, clear=False):
        request = self.request

        nextURL = request.get('nextURL', u'')
        if not (nextURL.endswith('logout.html') or \
                    nextURL.endswith('login.html')) and nextURL:
            return nextURL

        session = ISession(request)[SESSION_ID]
        if 'nextURL' in session:
            nextURL = session['nextURL']
            if clear:
                del session['nextURL']

            if nextURL:
                return nextURL

        return self._generateNextURL()

    def _generateNextURL(self):
        if self.request.getHeader('X-Requested-With', ''):
            return u''
        stack = self.request.getTraversalStack()
        stack.reverse()
        nextURL = u'/'.join([self.request.getURL(path_only=True)] + stack)

        if nextURL.endswith('logout.html') or nextURL.endswith('login.html'):
            return u''
        else:
            return nextURL

    def isChallenging(self):
        return 'login.html' in self.request.get('PATH_INFO', '')

    def challengingActions(self):
        actions = []
        request = self.request

        seen = set()
        for name, creds in self.context.getCredentialsPlugins():
            action = queryMultiAdapter((creds, request), ILoginAction)
            if action is not None and action.id not in seen:
                seen.add(action.id)
                action.update()
                actions.append((action.order, action.id, action))

        actions.sort()
        return [action for _w, _n, action in actions]

    def success(self):
        actions = [(action.order, action) for name, action in
                   getAdapters((self.request.principal, self.request),
                               ISuccessLoginAction)]
        actions.sort()

        nextURL = self.nextURL(True)
        for order, action in actions:
            result = action(nextURL)
            if result:
                return result
