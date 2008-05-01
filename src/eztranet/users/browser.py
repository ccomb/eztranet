from zope.app.securitypolicy.browser.granting import Granting
from zope.component import getUtility, getAllUtilitiesRegisteredFor
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.securitypolicy.interfaces import IRole, IPrincipalRoleManager
from zope.formlib.form import EditForm, Fields, AddForm, applyChanges, DisplayForm
from zope.app.container.interfaces import INameChooser
from zope.app.container.browser.contents import Contents
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')

from users import EztranetUser
from interfaces import IEztranetUser


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
        """
        This method is called at the beginning of the template. So do the job and return the status
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

class EztranetUserAdd(AddForm):
    """
    The view class for adding a user
    """
    form_fields = Fields(IEztranetUser).select('login','password','IsAdmin')
    label = _(u'New user')
    def createAndAdd(self, data):
        user=EztranetUser("","","")
        applyChanges(user, self.form_fields, data)
        contentName = INameChooser(user).chooseName(user.login, user)
        user.title = user.login
        self.context[contentName] = user
        self.request.response.redirect(AbsoluteURL(self.context,
                                                   self.request)()+'/contents.html')

class EztranetUserView(DisplayForm):
    """
    The view class for viewing a user
    """
    form_fields = Fields(IEztranetUser).select('login','IsAdmin')
    label = _(u'User')
    def __init__(self, context, request):
        self.context, self.request = context, request
        self.label = self.context.login

class EztranetUserEdit(EditForm):
    """
    The view class for editing a user
    """
    form_fields=Fields(IEztranetUser).select('password','IsAdmin')
    label = _(u'Modifying a user')
    def __init__(self, context, request):
        self.context, self.request = context, request
        self.label = self.context.login

class EztranetUsers(Contents):
    """
    The list of users
    """
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
