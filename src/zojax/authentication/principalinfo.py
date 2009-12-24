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
from zope.traversing.api import getPath
from zope.component import queryUtility, getUtilitiesFor
from zope.session.interfaces import IClientId
from zope.app.authentication.interfaces import IPluggableAuthentication
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

try:
    from zope.ramcache.ram import Storage, caches, writelock
except ImportError:
    from zope.app.cache.ram import Storage, caches, writelock


from interfaces import _, IPrincipalInfoStorage, IAuthenticationSettings

cacheId = 'zojax.authentication.principalinfostorage'


class IRAMCachePrincipalInfoStorage(interface.Interface):
    """ """


class RAMCachePrincipalInfoStorage(object):
    interface.implements(IPrincipalInfoStorage)

    name = _('RAM PrincipalInfo storage')

    def _getStorage(self, age):
        writelock.acquire()
        try:
            if cacheId not in caches:
                caches[cacheId] = Storage(999999999, age+100, 3000)
            return caches[cacheId]
        finally:
            writelock.release()

    def get(self, auth, request):
        storage = self._getStorage(auth.age)

        try:
            clientId = IClientId(request, None)
        except:
            clientId = None
        if clientId is None:
            return None

        clientId = str(clientId)
        try:
            principal = storage.getEntry(clientId, None)
            pid = auth.prefix + principal.id
            try:
                storage.getEntry(pid, None)
            except:
                pass
            return principal
        except KeyError:
            return None

    def clear(self, auth, request, principal=None):
        storage = self._getStorage(auth.age)

        if principal is not None:
            pid = principal.id
            try:
                ids = storage.getEntry(pid, None)
            except:
                return

            for clientId in ids:
                storage.invalidate(clientId)

            storage.invalidate(pid)
            return

        clientId = IClientId(request, None)
        if clientId is None:
            return

        clientId = str(clientId)
        try:
            principal = storage.getEntry(clientId, None)

            pid = auth.prefix + principal.id
            try:
                ids = storage.getEntry(pid, None)
            except:
                ids = []

            if clientId in ids:
                ids.remove(clientId)
                if ids:
                    storage.setEntry(pid, None, ids)
                else:
                    storage.invalidate(pid)
        except:
            pass

        storage.invalidate(clientId)

    def store(self, auth, request, principal, credentials):
        clientId = IClientId(request, None)
        if clientId is None:
            return

        clientId = str(clientId)
        storage = self._getStorage(auth.age)

        storage.setEntry(clientId, None, principal)

        pid = auth.prefix + principal.id
        try:
            ids = storage.getEntry(pid, None)
        except:
            ids = []

        ids.append(clientId)
        storage.setEntry(pid, None, ids)

    def getStatistics(self, auth):
        return self._getStorage(auth.age).getStatistics()


def principalInfoStorages(context):
    terms = []
    for name, storage in getUtilitiesFor(IPrincipalInfoStorage):
        terms.append((storage.name, SimpleTerm(name, name, storage.name)))

    terms.sort()
    return SimpleVocabulary([term for n, term in terms])


@component.adapter(IAuthenticationSettings)
@interface.implementer(IPrincipalInfoStorage)
def getPrincipalInfoStorage(auth):
    storage = queryUtility(IPrincipalInfoStorage, auth.pinfoStorage)
    if storage is not None:
        return storage

    return getUtility(IPrincipalInfoStorage, 'ram')


def isInstalled(configlet):
    return configlet.__parent__.isInstalled()
