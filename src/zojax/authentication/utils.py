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
from zope.component import getUtility, getUtilitiesFor
from zope.security.management import queryInteraction
from zope.security.interfaces import IMemberGetterGroup
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError
from zope.app.authentication.interfaces import IPluggableAuthentication

from interfaces import IPrincipalByLogin, ICredentialsUpdater
from interfaces import IPluggableAuthentication as extIPluggableAuthentication
from credentials import SimpleCredentials


def updateCredentials(request, login, password):
    auth = getUtility(IAuthentication)
    if IPluggableAuthentication.providedBy(auth):

        updated = False
        for name, creds in auth.getCredentialsPlugins():
            if ICredentialsUpdater.providedBy(creds):
                if extIPluggableAuthentication.providedBy(auth):
                    auth.logout(request)

                creds.updateCredentials(
                    request, SimpleCredentials(login, password))

                auth.authenticate(request)
                updated = True

        if updated:
            return True
    return False


def getPrincipalByLogin(login):
    for name, adapter in getUtilitiesFor(IPrincipalByLogin):
        principal = adapter.getPrincipalByLogin(login)
        if principal is not None:
            return principal


def getPrincipal(id=None):
    """ get current interaction principal """
    if id is None:
        interaction = queryInteraction()

        if interaction is not None:
            for participation in interaction.participations:
                if participation.principal is not None:
                    return participation.principal
    else:
        try:
            return getUtility(IAuthentication).getPrincipal(id)
        except PrincipalLookupError:
            return None


def getPrincipals(ids, filter=None):
    auth = getUtility(IAuthentication)

    principals = []
    for pid in ids:
        try:
            principal = auth.getPrincipal(pid)
        except PrincipalLookupError:
            continue

        if filter is not None:
            if not filter.providedBy(principal):
                continue

        principals.append(principal)

    return principals


def getGroupPrincipals(group, auth=None):
    if auth is None:
        auth = getUtility(IAuthentication)

    if not IMemberGetterGroup.providedBy(group):
        return ()

    seen = set()
    stack = [iter(group.getMembers())]

    while stack:
        try:
            p_id = stack[-1].next()
        except StopIteration:
            stack.pop()
            continue

        if p_id not in seen:
            try:
                principal = auth.getPrincipal(p_id)
            except PrincipalLookupError:
                continue

            seen.add(p_id)

            if IMemberGetterGroup.providedBy(principal):
                stack.append(iter(principal.getMembers()))

    return seen
