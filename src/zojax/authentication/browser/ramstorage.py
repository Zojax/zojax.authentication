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
from zope.component import getUtility
from zope.security.proxy import removeSecurityProxy
from zope.app.security.interfaces import IAuthentication
from zojax.authentication.interfaces import IPrincipalInfoStorage

class RAMStorage(object):

    def getStatistics(self):
        storage = removeSecurityProxy(getUtility(IPrincipalInfoStorage, 'ram'))
        return storage.getStatistics(getUtility(IAuthentication))
