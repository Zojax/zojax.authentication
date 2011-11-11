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
import time
from zope import component
from zope.component import getUtility
from zope.app.http.httpdate import build_http_date
from zope.session.interfaces import IClientIdManager
from zope.security.management import queryInteraction
from zope.app.security.interfaces import IAuthentication

from interfaces import IPrincipalInfoStorage, IPrincipalRemovingEvent, \
                       IPrincipalLoggedInEvent, IPrincipalLoggingOutEvent

cookie_name = '__ac_zojax'
cookie_path = '/'

@component.adapter(IPrincipalRemovingEvent)
def principalRemovingHandler(event):
    auth = getUtility(IAuthentication)
    storage = IPrincipalInfoStorage(auth, None)

    if storage is not None:
        principal = event.principal
        interaction = queryInteraction()
        if interaction is not None:
            for request in interaction.participations:
                storage.clear(auth, request, principal)

@component.adapter(IPrincipalLoggedInEvent)
def cookieSet(event):
    """"""
    interaction = queryInteraction()
    if interaction is not None and interaction.participations:
        request = interaction.participations[0]
        manager = component.getUtility(IClientIdManager)
        expires = None
        if manager.cookieLifetime is not None:
            if manager.cookieLifetime:
                expires = build_http_date(time.time() + manager.cookieLifetime)
            else:
                expires = 'Tue, 19 Jan 2038 00:00:00 GMT'

        request.response.setCookie(cookie_name, 'authorized', path=cookie_path, expires=expires)

@component.adapter(IPrincipalLoggingOutEvent)
def cookieDel(event):
    """"""
    interaction = queryInteraction()
    if interaction is not None and interaction.participations:
        request = interaction.participations[0]
        request.response.expireCookie(cookie_name, path=cookie_path)

