# -*- coding: utf-8 -*-
from zope.app.securitypolicy.browser.granting import Granting
from zope.component import getUtility, getAllUtilitiesRegisteredFor
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.securitypolicy.interfaces import IRole, IPrincipalRoleManager
from zope.formlib.form import EditForm, Fields, AddForm, applyChanges, DisplayForm
from zope.app.container.interfaces import INameChooser
from zope.app.container.browser.contents import Contents

from users import EztranetUser
from interfaces import *


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
        u"This method is called at the beginning of the template. So do the job and return the status"
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
    form_fields=Fields(IEztranetUser).select('login','password','IsAdmin')
    label=u"Nouvel utilisateur"
    def create(self, data):
        u"on crée l'objet (ici avec le constructeur, mais on devrait utiliser une named factory)"
        user=EztranetUser("","","")
        u"puis on applique les données du formulaire à l'objet (data contient les données du formulaire !)"
        applyChanges(user, self.form_fields, data)
        u"puis on choisit le nom de l'objet dans le container (le 1er nom dans la liste)"
        self.context.contentName=INameChooser(user).chooseName(user.title, user)
        user.title = user.login
        return user

class EztranetUserView(DisplayForm):
    u"""
    The view class for viewing a user
    """
    form_fields=Fields(IEztranetUser).select('login','IsAdmin')
    label=u"Utilisateur"
    def __init__(self, context, request):
        self.context, self.request = context, request
        self.label = self.context.login

class EztranetUserEdit(EditForm):
    u"""
    The view class for editing a user
    """
    form_fields=Fields(IEztranetUser).select('password','IsAdmin')
    label=u"Modification utilisateur"
    def __init__(self, context, request):
        self.context, self.request = context, request
        self.label = self.context.login

class EztranetUsers(Contents):
    u"""
    The list of users
    """
    def supportsRename(self):
        return False
    def removeObjects(self):
        # on empeche de se supprimer soi-même
        ppal_id = unicode(self.request.principal.id)
        ids_to_remove = []
        if 'ids' in self.request.form:
            ids_to_remove = self.request.form['ids']
        if ppal_id in ids_to_remove:
            ids_to_remove.remove(ppal_id)
        super(EztranetUsers, self).removeObjects()
