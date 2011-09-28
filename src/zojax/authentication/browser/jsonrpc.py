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
from zope.app.security.interfaces import IAuthentication
from zojax.principal.profile.interfaces import IPersonalProfile
import simplejson
"""

$Id$
"""
from zope.session.interfaces import IClientIdManager
from zope import component

from z3c.jsonrpc import publisher


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
