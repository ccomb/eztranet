from z3c.menu.simple.menu import SimpleMenuItem
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')

class ShowPasswordMenuItem(SimpleMenuItem):
    title = _('Show password')
    url = 'showpassword.html'
    weight = 99
