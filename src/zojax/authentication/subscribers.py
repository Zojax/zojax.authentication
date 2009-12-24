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
from zope import component
from zope.component import getUtility
from zope.security.management import queryInteraction
from zope.app.security.interfaces import IAuthentication

from interfaces import IPrincipalInfoStorage, IPrincipalRemovingEvent


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
