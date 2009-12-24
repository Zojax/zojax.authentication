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
""" zojax.authentication.browser interfaces

$Id$
"""
from zope import schema, interface
from zojax.authentication.interfaces import _


class ILoginLayer(interface.Interface):
    """ login layer """


class ILoginForm(interface.Interface):
    """ login form view """


class ILogoutForm(interface.Interface):
    """ logout form view """
