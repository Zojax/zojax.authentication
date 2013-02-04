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
import simplejson

from zope import component
from zope.event import notify
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.principalfolder import Principal
from zope.session.interfaces import IClientIdManager, IClientId
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.authentication.interfaces import AuthenticatedPrincipalCreated
from zojax.cache.interfaces import ICacheConfiglet
from zope.app.cache.interfaces import ICache
from zope.component import getUtility

from datetime import datetime
from datetime import timedelta 
from z3c.jsonrpc import publisher

from zojax.cache.tag import ContextTag
from zojax.cache.timekey import TimeKey, each5minutes
from zojax.cache.view import cache as view_cache
from zojax.authentication.credentials import SimpleCredentials
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.authentication.interfaces import IPrincipalInfoStorage,\
    PrincipalInitializedEvent, PrincipalInitializationFailed

OnlineNumTag = ContextTag('online.number')

class Authentication(publisher.MethodPublisher):
    
    def loginStatus(self, secret):
        self.request.response.setCookie(component.getUtility(IClientIdManager).namespace, secret)
        principal = component.getUtility(IAuthentication).authenticate(self.request)
        if principal is not None:
            def safe_dump(ob, schema):
                o = schema(ob, None)
                if o is not None:
                    res = {}
                    for field in schema:
                        try:
                            res[field] = simplejson.loads(simplejson.dumps(getattr(o, field, None)))
                        except TypeError:
                            continue
                    return res
            return dict(profile=safe_dump(principal,IPersonalProfile), title=principal.title,
                        id = principal.id)


    def loginPassAuth(self, login=None, password=None):
        """ authorizes the user with login and password
            and returns authenticated user's sessionId """

        request = self.request

        #if not IUnauthenticatedPrincipal.providedBy(request.principal):
        #    return

        if login is not None and password is not None:
            credentials = SimpleCredentials(login, password)

            auth = component.getUtility(IAuthentication)
            storage = IPrincipalInfoStorage(auth)
            authenticatorPlugins = list(auth.getAuthenticatorPlugins())

            for authname, authplugin in authenticatorPlugins:
                try:
                    info = authplugin.authenticateCredentials(credentials)
                    if info is None:
                        continue
                    principal = Principal(
                        auth.prefix + info.id, info.title, info.description)

                    notify(PrincipalInitializedEvent(principal, auth))
                except PrincipalInitializationFailed, err:
                    #? cache.loginMessage = err.message
                    return "Authentication Error: %s" % err.message

                notify(AuthenticatedPrincipalCreated(
                        auth, principal, info, request))

                storage.store(auth, request, info, credentials)

                if principal is None:
                    return "Authentication Error: principal is None"

                return str(IClientId(request, None))
                
        return "Authentication Error: login or password is empty"

    @property
    def cache(self):
        return getUtility(ICacheConfiglet).cache
    
    @view_cache('zojax.authentication.onlineNumber', OnlineNumTag, TimeKey(minutes=each5minutes))
    def onlineNumber(self):
        id_dict = self.cache.query('zojax.authentication', {'online_users':'id_dict'})
        if id_dict:
            rm_list = []
            for id, time in id_dict.iteritems():
               if datetime.now() > time:
                   rm_list.append(id) 
            for rm_id in rm_list:
                del id_dict[rm_id]
            self.recountOnlineNumber(id_dict)
            self.cache.set(id_dict, 'zojax.authentication', {'online_users':'id_dict'})
            num = self.cache.query('zojax.authentication', {'online_users':'number'})
            if num is not None:
                return str(num)
        return '1'
    
    def incOnline(self):
        id_dict = self.cache.query('zojax.authentication', {'online_users':'id_dict'})    
        new_id = self.request.principal.id
        if id_dict:
            id_dict[new_id] = self.getExpireTime()
        else:
            id_dict = {new_id: self.getExpireTime()}
        self.recountOnlineNumber(id_dict)
        self.cache.set(id_dict, 'zojax.authentication', {'online_users':'id_dict'})
        OnlineNumTag.update(self.context)

    def recountOnlineNumber(self, id_dict):
        self.cache.set(len(id_dict), 'zojax.authentication', {'online_users':'number'})
        
    def getExpireTime(self):
        return datetime.now() + timedelta(minutes=5)
