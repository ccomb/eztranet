from zope.schema.interfaces import IField
from zope.schema import Text
from zope.interface import implements

class IHtmlText(IField):
    """An html text field"""

class HtmlText(Text):
    """Field describing an html text field"""
    implements(IHtmlText)
    
    def _validate(self, value):
        super(HtmlText, self)._validate(value)

class TinyHeader(object):
    def update(self):
        pass
    def render(self):
        return """
<script type="text/javascript" src="++resource++tinymce/jscripts/tiny_mce/tiny_mce.js"></script>
<script type="text/javascript">
	tinyMCE.init({
		mode : "textareas",
		theme : "advanced",
    theme_advanced_buttons1 :
    "bold,italic,underline,strikethrough,|bullist,numlist,|,justifyleft,justifycenter,justifyright,justifyfull,|,blockquote,link,unlink,|,formatselect,fontsizeselect,|,code,|,forecolor,removeformat,hr",
    theme_advanced_buttons2 : "",
    theme_advanced_buttons3 : ""

	});
</script>
"""
