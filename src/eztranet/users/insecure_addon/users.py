from zope.security.proxy import removeSecurityProxy
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.component import adapter
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces  import IObjectModifiedEvent
from zope.i18nmessageid import MessageFactory
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from eztranet.users.interfaces import IEztranetUser


import zope.security.management
import zope.security.interfaces
import zope.publisher.interfaces


def __getRequest():
    i = zope.security.management.getInteraction() # raises NoInteraction

    for p in i.participations:
        if zope.publisher.interfaces.IRequest.providedBy(p):
            return p

    raise RuntimeError('Could not find current request.')

def __store_password_like_you_never_should(user):
    annotations = IAnnotations(user)
    if 'eztranet' not in annotations:
        annotations['eztranet'] = PersistentDict()
    if 'insecure_addon' not in annotations['eztranet']:
        annotations['eztranet']['insecure_addon'] = None
    request = __getRequest()
    if hasattr(request, 'form') and 'form.password' in request.form:
        newpass = request.form['form.password']
        if newpass != '':
            annotations['eztranet']['insecure_addon'] = newpass

@adapter(IEztranetUser, IObjectAddedEvent)
def EztranetUserAdded(user, event):
    """
    a silly subscriber that stores the password in an annotation
    Please don't use!
    """
    __store_password_like_you_never_should(user)

@adapter(IEztranetUser, IObjectModifiedEvent)
def EztranetUserModified(user, event):
    """
    a silly subscriber that store the password in an annotation
    Please don't use!
    """
    __store_password_like_you_never_should(user)

class ShowPassword(BrowserView):
    def __init__(self, context, request):
        self.context, self.request = context, request
        try:
            self.password = IAnnotations(removeSecurityProxy(self.context))['eztranet']['insecure_addon']
        except:
            self.password = None
