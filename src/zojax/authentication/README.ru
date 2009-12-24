============================
zojax Authenitcation Utility
============================

    >>> from zope import interface, component

Главное отличие от zope.app.authentication, zojax.authentication не хранит
`credentials` данные в течении сессии. `credentials` используются только
один раз для авторизации, дальше хранится промежуточный результат (PrincipalInfo)
Поэтому ICredentialsPlugin интерфейс существенно сокращен.
По сути `credentials` плагин используется только для получания `login` и `password`

Сначало нужно создать IPrincipalInfoStorage, где Authentication
Utility будет хранить данные.

    >>> from zojax.authentication import interfaces
    >>> from zojax.authentication.authentication import PluggableAuthentication

    >>> class PrincipalInfoStorage(object):
    ...     interface.implements(interfaces.IPrincipalInfoStorage)
    ...
    ...     data = {}
    ...
    ...     def get(self, auth, request):
    ...         id = request.get('sessionId', None)
    ...         if id is not None:
    ...             return self.data.get(id, None)
    ...         return None
    ...
    ...     def clear(self, auth, request, principal=None):
    ...         id = request.get('sessionId', None)
    ...         if id is not None:
    ...             if id in self.data:
    ...                 del self.data[id]
    ...
    ...     def store(self, auth, request, info, credentials):
    ...         id = request.get('sessionId', None)
    ...         if id is not None:
    ...             self.data[id] = info

    >>> component.provideUtility(PrincipalInfoStorage(), name="myStorage")

Создадим простой плагин

    >>> from zojax.authentication.credentials import DefaultCredentialsPlugin

Зарегестрируем плагин

    >>> myCredentialsPlugin = DefaultCredentialsPlugin()
    >>> component.provideUtility(myCredentialsPlugin, interfaces.IDefaultCredentialsPlugin , name='My Credentials Plugin')


Simple Authenticator Plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next we'll create a simple authenticator plugin. For our plugin, we'll need
an implementation of IPrincipalInfo::

    >>> from zope.app.authentication.interfaces import IPrincipalInfo
    >>> from zope.app.authentication.interfaces import IAuthenticatorPlugin

    >>> class PrincipalInfo(object):
    ...
    ...     interface.implements(IPrincipalInfo)
    ...
    ...     def __init__(self, id, title, description):
    ...         self.id = id
    ...         self.title = title
    ...         self.description = description
    ...
    ...     def __repr__(self):
    ...         return 'PrincipalInfo(%r)' % self.id

Our authenticator uses this type when it creates a principal info::

    >>> class MyAuthenticatorPlugin(object):
    ...     interface.implements(IAuthenticatorPlugin)
    ...
    ...     def authenticateCredentials(self, credentials):
    ...         if credentials.login == 'bob' and \
    ...                credentials.password == 'secretcode':
    ...             return PrincipalInfo('bob', 'Bob', '')
    ...
    ...     def principalInfo(self, id):
    ...         if id == 'bob':
    ...             return PrincipalInfo('bob', 'Bob', '')


Так же как и для `credentials plugin`, `authenticator plugin` должен
быть зарегестрирован как именованная утилита::

    >>> myAuthenticatorPlugin = MyAuthenticatorPlugin()
    >>> component.provideUtility(
    ...     myAuthenticatorPlugin, name='My Authenticator Plugin')


Principal Factories
~~~~~~~~~~~~~~~~~~~

While authenticator plugins provide principal info, they are not responsible
for creating principals. This function is performed by factory adapters. For
these tests we'll borrow some factories from the principal folder::

    >>> from zope.app.authentication import principalfolder
    >>> component.provideAdapter(principalfolder.AuthenticatedPrincipalFactory)
    >>> component.provideAdapter(principalfolder.FoundPrincipalFactory)


Configure PAU
~~~~~~~~~~~~~

    >>> pau = PluggableAuthentication('xyz_')

    >>> pau.credentialsPlugins = ('My Credentials Plugin', )
    >>> pau.authenticatorPlugins = ('My Authenticator Plugin', )
    >>> pau.pinfoStorage = u'myStorage'

Using the PAU to Authenticate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Теперь мы можем использовать PAU для авторизации простого `request`::

  >>> from zope.publisher.browser import TestRequest
  >>> print pau.authenticate(TestRequest(sessionId='1'))
  None

В данном случае мы не можем авторизовать пустой `request`. Так же не
возможно авторизовать request с неправильными `credentials` данными::

  >>> print pau.authenticate(
  ...     TestRequest(**{'zojax-login': 'bob',
  ...                    'zojax-password': 'let me in!',
  ...                    myCredentialsPlugin.submitfield: '1',
  ...                    'sessionId': '1'}))
  None

Теперь передадим правильные данные::

  >>> request = TestRequest(
  ...     **{'zojax-login': 'bob', 'zojax-password': 'secretcode',
  ...        myCredentialsPlugin.submitfield: '1', 'sessionId': '1'})
  >>> principal = pau.authenticate(request)
  >>> principal
  Principal('xyz_bob')

we get an authenticated principal. При этом создается сообщение IPrincipalLoggedInEvent

  >>> from zope.component.eventtesting import getEvents, clearEvents
  >>> event = getEvents()[-1]
  >>> event, event.principal
  (<zojax.authentication.interfaces.PrincipalLoggedInEvent ...>, Principal('xyz_bob'))

  >>> clearEvents()

Для повторной авторизации нам не нужно передовать `credentials` данные снова.

  >>> principal = pau.authenticate(TestRequest(sessionId='1'))
  >>> print principal
  Principal('xyz_bob')

При повторной авторизации IPrincipalLoggedInEvent сообщение не создается.

  >>> interfaces.IPrincipalLoggedInEvent.providedBy(getEvents()[-1])
  False


Logout
~~~~~~

Нужно просто вызвать метод `logout`

  >>> request = TestRequest(sessionId='1')
  >>> pau.logout(request)
  >>> principal = pau.authenticate(request)
  >>> print principal
  None

При этом создается сообщение IPrincipalLoggingOutEvent

  >>> event = getEvents()[-1]
  >>> event
  <zojax.authentication.interfaces.PrincipalLoggingOutEvent ...>


getPrincipal
~~~~~~~~~~~~

getPrincipal кеширует полученные данные, но только для текущего `interaction`

  >>> from zojax.authentication import authentication

  >>> authentication.cache.principals
  {}

  >>> pau.getPrincipal('xyz_bob')
  Principal('xyz_bob')

  >>> pau.getPrincipal('xyz_bob')
  Principal('xyz_bob')

  >>> authentication.cache.principals
  {'xyz_bob': Principal('xyz_bob')}
