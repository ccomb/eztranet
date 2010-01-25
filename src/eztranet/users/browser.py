from z3c.contents.browser import Contents
from z3c.form.field import Fields
from z3c.form.form import applyChanges
from z3c.formui.form import EditForm, AddForm, DisplayForm
from z3c.menu.simple.menu import SimpleMenuItem
from z3c.pagelet.browser import BrowserPagelet
from z3c.table.column import Column
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.publisher.interfaces.http import ILogin
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import ILogout, ILogoutSupported
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.securitypolicy.browser.granting import Granting
from zope.component import getUtility, getAllUtilitiesRegisteredFor, adapts
from zope.contentprovider.interfaces import IContentProvider
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements, Interface
from zope.lifecycleevent import ObjectCreatedEvent
from zope.securitypolicy.interfaces import IRole, IPrincipalRoleManager
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.viewlet.viewlet import ViewletBase
import urllib
import zope.event

from eztranet.skin.interfaces import IEztranetSkin
from interfaces import IEztranetUser
from users import EztranetUser

_ = MessageFactory('eztranet')


class LoginForm(BrowserPagelet):
    """view class for the login form"""


class HTTPAuthenticationLogin(BrowserPagelet):
    """view class for the login
    """
    implements(ILogin)
    def login(self, nextURL=None):
        "see ILogin"
        # we don't want to keep challenging if we're authenticated
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            getUtility(IAuthentication).unauthorized(self.request.principal.id,
                                                     self.request)
            return
        else:
            if nextURL is None:
                return
            else:
                self.request.response.redirect(nextURL)

    def update(self):
        "update part of the content provider (the render part is inherited)"
        if 'nextURL' in self.request:
            return self.login(self.request['nextURL'])
        else:
            return self.login()



class HTTPAuthenticationLogout(BrowserPagelet):
    """logout view
    """
    implements(ILogout)

    def update(self):
        "see ILogout"
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = getUtility(IAuthentication)
            ILogout(auth).logout(self.request)


class LoginLogout(ViewletBase):
    """viewlet for the login or logout link

    (same as zope.app.security LoginLogout view
    """
    implements(IContentProvider)
    adapts(Interface, IEztranetSkin, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
    def update(self):
        pass

    def render(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            return u'<a href="@@login.html?nextURL=%s">%s</a>' % (
                urllib.quote(self.request.getURL()),
                translate(_('[Login]'), context=self.request,
                          default='[Login]'))
        elif ILogoutSupported(self.request, None) is not None:
            return u'<b>%s</b><br/><br/><a href="@@logout.html?nextURL=%s">%s</a>' % (
                self.request.principal.id,
                urllib.quote(self.request.getURL()),
                translate(_('[Logout]'), context=self.request,
                          default='[Logout]'))
        else:
            return None


class LogoutHeader(ViewletBase):
    """viewlet offering the part of header used for logout

    inspired from zope.app.security logout.pt
    """

    def render(self):
        output = ''
        if 'nextURL' in self.request:
            output += '''
            <meta http-equiv="refresh" content="0;url=%s" />
            ''' % self.request['nextURL']
        output += """
                  <script type="text/javascript"><!--
                    // clear HTTP Authentication
                    try {
                      if (window.XMLHttpRequest) {
                        var xmlhttp = new XMLHttpRequest();
                        // Send invalid credentials, then abort
                        xmlhttp.open("GET", "@@", true, "logout", "logout");
                        xmlhttp.send("");
                        xmlhttp.abort();
                      } else if (document.execCommand) {
                        // IE specific command
                        document.execCommand("ClearAuthenticationCache");
                      }
                    } catch(e) { }
                    //-->
                  </script>
        """
        return output


class ProjectGranting(Granting):
    def get_all_users(self):
        users = getUtility(IAuthenticatorPlugin, name="EztranetUsers")
        return users.keys()
    def get_eztranet_roles(self):
        roles = getAllUtilitiesRegisteredFor(IRole)
        return [role for role in roles if role.id.rsplit('.',1)[0]=='eztranet.project']
    def assigned(self, role, user):
        rolemanager = IPrincipalRoleManager(self.context)
        if rolemanager.getSetting(role, user).getName()=="Allow":
            return "1"
    def status(self):
        """This method is called at the beginning of the template.
        So do the job and return the status
        """

        if 'GRANT_SUBMIT' in self.request.form:
            rolemanager = IPrincipalRoleManager(self.context)
            for role in self.get_eztranet_roles():
                for user in self.get_all_users():
                    if role.id in self.request.form and user in self.request.form[role.id]:
                        rolemanager.assignRoleToPrincipal(role.id, user)
                    else:
                        rolemanager.unsetRoleForPrincipal(role.id, user)
            return _(u'Permissions modified')
        else:
            return False


class ProjectGrantingMenuItem(SimpleMenuItem):
    title = _(u'Permissions')
    url = 'permissions.html'
    weight = 150


class EztranetUserAdd(AddForm):
    """The view class for adding a user
    """
    fields = Fields(IEztranetUser).select('login','password','IsAdmin')
    label = _(u'New user')

    def createAndAdd(self, data):
        user=EztranetUser("","","")
        applyChanges(self, user, data)
        user.title = user.login
        zope.event.notify(ObjectCreatedEvent(user))
        if user.login in self.context:
            self.status = _(u'This user already exists')
            return
        self.context[user.login] = user
        self.request.response.redirect(AbsoluteURL(self.context,
                                                   self.request)()+'/contents.html')


class EztranetUserAddMenuItem(SimpleMenuItem):
    title = _(u'New user')
    url = 'add_user.html'


class EztranetUserView(DisplayForm):
    """The view class for viewing a user"""

    fields = Fields(IEztranetUser).select('login','IsAdmin')


class EztranetUserViewMenuItem(SimpleMenuItem):
    title = _(u'View user')
    url = 'index.html'


class EztranetUserEdit(EditForm):
    """The view class for editing a user
    """
    fields=Fields(IEztranetUser).select('password','IsAdmin')


class EztranetUserEditMenuItem(SimpleMenuItem):
    title = _(u'Edit user')
    url = 'edit_user.html'


class EztranetUsers(Contents):
    """The list of users
    """
    startBatchingAt = 1000000

    def supportsRename(self):
        return False
    def removeObjects(self):
        # prevent from deleting ourself
        ppal_id = unicode(self.request.principal.id)
        ids_to_remove = []
        if 'ids' in self.request.form:
            ids_to_remove = self.request.form['ids']
        if ppal_id in ids_to_remove:
            ids_to_remove.remove(ppal_id)
        super(EztranetUsers, self).removeObjects()


class EztranetUsersMenuItem(SimpleMenuItem):
    title = _(u'List')
    url = 'contents.html'


class AdminColumn(Column):
    header = _(u'')
    weight = 60
    def renderCell(self, item):
        return item.IsAdmin and u'admin' or u''
