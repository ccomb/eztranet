# -*- coding: utf-8 -*-
from zope.app.securitypolicy.browser.granting import Granting
from zope.component import getUtility, getAllUtilitiesRegisteredFor
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.securitypolicy.interfaces import IRole, IPrincipalRoleManager
from zope.security.proxy import removeSecurityProxy
from zope.formlib.form import EditForm, Fields, AddForm, applyChanges, DisplayForm
from zope.app.authentication.principalfolder import InternalPrincipal, IInternalPrincipal
from zope.app.container.interfaces import INameChooser
from zope.app.container.browser.contents import Contents
from zope.app.file.interfaces import IFile
from zope.app.file.file import File
from zope.publisher.browser import BrowserPage
from zope.app.pagetemplate import ViewPageTemplateFile

from users import EztranetUser
from interfaces import *


class ProjectGranting(Granting):
    def get_all_users(self):
        users = getUtility(IAuthenticatorPlugin, name="users")
        return users.keys()
    def get_eztranet_roles(self):
        roles = getAllUtilitiesRegisteredFor(IRole)
        return [role for role in roles if role.id.rsplit('.',1)[0]=='eztranet.project']
    def assigned(self, role, user):
        rolemanager = IPrincipalRoleManager(self.context)
        if rolemanager.getSetting(role, user).getName()=="Allow":
            return "1"
    def status(self):
        u"This method is called a the beginning of the template. So do the job and return the status"
        if 'GRANT_SUBMIT' in self.request.form:
            rolemanager = IPrincipalRoleManager(self.context)
            for role in self.get_eztranet_roles():
                for user in self.get_all_users():
                    if role.id in self.request.form and user in self.request.form[role.id]:
                        rolemanager.assignRoleToPrincipal(role.id, user)
                    else:
                        rolemanager.unsetRoleForPrincipal(role.id, user)
            return "Permissions modified"
        else:
            return False

class EztranetUserAdd(AddForm):
    u"""
    The view class for adding a user
    """
    form_fields=Fields(IEztranetUser).select('login','password','title','IsAdmin')
    label=u"Adding a user"
    def create(self, data):
        u"on crée l'objet (ici avec le constructeur, mais on devrait utiliser une named factory)"
        user=EztranetUser("","","")
        u"puis on applique les données du formulaire à l'objet (data contient les données du formulaire !)"
        applyChanges(user, self.form_fields, data)
        u"puis on choisit le nom de l'objet dans le container (le 1er nom dans la liste)"
        self.context.contentName=INameChooser(user).chooseName(user.title, user)
        return user


class EztranetUserView(DisplayForm):
    u"""
    The view class for viewing a user
    """
    form_fields=Fields(IEztranetUser).select('login','password','title','IsAdmin')
    label=u"Viewing a user"

class EztranetUserEdit(EditForm):
    u"""
    The view class for editing a user
    """
    form_fields=Fields(IEztranetUser).select('login','password','title','IsAdmin')
    label=u"Editing a user"

