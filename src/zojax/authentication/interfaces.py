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
""" zojax.authentication interfaces

$Id$
"""
from zope import schema, interface
from zope.i18nmessageid import MessageFactory
from zope.app.authentication.interfaces import IPlugin
from zope.app.authentication.interfaces import IAuthenticatorPlugin

_ = MessageFactory('zojax.authentication')

SESSION_ID = 'zojax.authentication'


class IActiveAuthenticatorPlugin(IAuthenticatorPlugin):
    """ active authenticator plugin """


# auth events
class IPrincipalLoggedInEvent(interface.Interface):
    """ principal logged in """

    principal = interface.Attribute('Principal')


class IPrincipalLoggingOutEvent(interface.Interface):
    """ principal logging out """

    principal = interface.Attribute('Principal')


class PrincipalLoggedInEvent(object):
    interface.implements(IPrincipalLoggedInEvent)

    def __init__(self, principal):
        self.principal = principal


class PrincipalLoggingOutEvent(object):
    interface.implements(IPrincipalLoggingOutEvent)

    def __init__(self, principal):
        self.principal = principal


# PrincipalInfo storage
class IPrincipalInfoStorage(interface.Interface):
    """ storage for principal info """

    name = interface.Attribute('Name')

    def get(authentication, request):
        """ return authenticated principal info or None """

    def clear(authentication, request, principal=None):
        """ clear authenticated principal info """

    def store(authentication, request, principalInfo, credentials):
        """ store principal info """


# Login service
class ILoginService(interface.Interface):
    """ adapter for (IAuthentication, IRequest) """

    def challenge(nextURL=u''):
        """Possibly issues a challenge.

        This is typically done in a protocol-specific way.

        If a challenge was issued, return True, otherwise return False.
        """

    def nextURL(clear=True):
        """ return next url for request and clear value """

    def isChallenging():
        """ is challenging process active """

    def challengingActions():
        """ return list of challenging actions """

    def success():
        """ challenging processed successfully """


class ISuccessLoginAction(interface.Interface):
    """ success login action for (principal, request) """

    order = interface.Attribute('Action order')

    def __call__(nextURL=u''):
        """ call action,
        should return non empty value to stop actions processing """


# Credentials Interfaces
class ICredentialsPlugin(IPlugin):
    """ credentials plugin, plugin should not store credential information """

    def extractCredentials(request):
        """Ties to extract credentials from a request.

        A return value of None indicates that no credentials could be found.
        Any other return value is treated as valid credentials.
        """


class ICredentialsUpdater(interface.Interface):
    """ credention information updater interface """

    def updateCredentials(request, creds, temp=False):
        """ update current credentials, return status """


class ISimpleCredentials(interface.Interface):
    """ default credentials """

    login = interface.Attribute('login')

    password = interface.Attribute('password')

    principalinfo = interface.Attribute('principal info')


class IDefaultCredentialsPlugin(ICredentialsPlugin, ICredentialsUpdater):
    """ default plugin """

    loginfield = interface.Attribute('Request field for login')

    passwordfield = interface.Attribute('Request field for password')


class ICredentialAction(interface.Interface):
    """ credential action """

    id = schema.TextLine(
        title = u'Action unique id',
        required = True)

    order = schema.Int(
        title = u'Order',
        required = True)

    def update():
        """ update action """

    def render():
        """ return rendered action """

    def isProcessed():
        """ login action processed status """


class ILoginAction(ICredentialAction):
    """ login action """


class ILogoutAction(ICredentialAction):
    """ logout action """


# Authentication
class IPluggableAuthentication(interface.Interface):
    """ zojax pluggable authentication """

    loginMessage = interface.Attribute('Last login message')


class IAuthenticationSettings(interface.Interface):

    age = schema.Int(
        title = _(u'Age'),
        description = _(u'Maximum age for logged in principal.'),
        default = 3600,
        required = True)

    pinfoStorage = schema.Choice(
        title = _('PrincipalInfo storage'),
        vocabulary = 'zojax.authentication.principalInfoStorages',
        default = u'ram',
        required = True)


class IPrincipalInitializedEvent(interface.Interface):
    """ principal created, event before AuthenticatedPrincipalCreated event """

    principal = interface.Attribute('Principal object')

    authentication = interface.Attribute('IAuthentication object')


class PrincipalInitializedEvent(object):
    interface.implements(IPrincipalInitializedEvent)

    def __init__(self, principal, auth):
        self.principal = principal
        self.authentication = auth


class PrincipalInitializationFailed(Exception):
    """ initialization failed exception,
    IPrincipalInitializedEvent handler can throw this exception """

    def __init__(self, message):
        self.message = message


# Authenticator Plugins Management
class IAuthenticationConfiglet(interface.Interface):
    """ configlet """

    def isInstalled():
        """ is authentication utility installed """

    def installUtility():
        """ install authentication utility """

    def installPrincipalRegistry():
        """ install principal registry authenticator plugin """

    def uninstallUtility(remove=False):
        """ install authentication utility """


class IPluginFactory(interface.Interface):
    """ plugin factory """

    name = interface.Attribute('Plugin name')

    title = schema.TextLine(
        title = u'Title',
        required=True)

    description = schema.TextLine(
        title = u'Description',
        required=False)

    plugin = interface.Attribute("Authenticator plugin")

    def install():
        """ install plugin """

    def uninstall():
        """ uninstall plugin """

    def activate():
        """ activate plugin """

    def deactivate():
        """ de-activate plugin """

    def isActive():
        """ is plugin active """

    def isAvailable():
        """ is plugin available """


class IAuthenticatorPluginFactory(IPluginFactory):
    """ auth plugin factory """


class ICredentialsPluginFactory(IPluginFactory):
    """ credentials plugin factory """


# Principal removing events
class IPrincipalRemovingEvent(interface.Interface):

    principal = schema.TextLine(
        title = u'Principal',
        required = True)


class PrincipalRemovingEvent(object):
    interface.implements(IPrincipalRemovingEvent)

    def __init__(self, principal):
        self.principal = principal


# principal <-> login mapping
class IPrincipalByLogin(interface.Interface):
    """ search principal by login name """

    def getPrincipalByLogin(login):
        """ get principal """


class IPrincipalLogin(interface.Interface):
    """ get login for principal """

    login = interface.Attribute('Principal login')

    def __init__(principal):
        """ adapter constructor """
