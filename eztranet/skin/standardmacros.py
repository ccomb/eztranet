# -*- coding: utf-8 -*-
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.basicskin.standardmacros import StandardMacros

# l'ordre est le suivant :
##########################
# On part du ZPT de la vue, dans lequel on veut accéder à une macro nommée « page » disponible dans une vue « standard_macros ».
# (voir : metal:use-macro="context/@@standard_macros/page")
# Il faut donc d'abord REdéfinir la vue « standard_macros »
# Ceci se fait grâce à la vue ci-dessous MyOwnStandardMacros (qui étend StandardMacros) et qui est
# inscrite comme « standard_macros ». L'attribut macro_pages permet de définir la liste des macros accessibles depuis la vue.
#
# Ensuite on veut accéder à la macro « page » de la vue « standard_macro ».
# Pour ce faire, on définit une vue basée sur un template, et on donne accès aux éléments de ce template
# grâce à la méthode __getitem__. La vue en elle-même ne sert à rien, juste à pouvoir accéder aux macros du template.
#
# L'ordre de définition est donc le suivant :
# standard_macros -> ZCML -> MyOwnStandardMacros -> mymainmacro -> ZCML -> MyMainMacro -> main_template.pt -> page

class MyOwnStandardMacros(StandardMacros):
    """
    l'implémentation de la vue "standard_macros" (inscrite comme telle dans ZCML),
    implémentée sur base de StandardMacros.
    Elle donne la liste des vues/macros disponibles dans la vue my_macros.
    (Celles-ci sont définies/inscrites dans ZCML)
    """
    macro_pages=('mymainmacro', 'navigation_macros') #navigation_macros is for xmltree from rotterdam

class MyMainMacro(BrowserView):
    """
    la vue qui permet de fournir les macros personnalisées définies par un template
    """
    template = ViewPageTemplateFile("main_template.pt")
    def __getitem__(self, key):
        return self.template.macros[key]
