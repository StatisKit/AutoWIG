from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter

class Interface(object):

    def __init__(self, obj, style="default", full=True, lineos=False):
        self.code = obj._repr_interface_()
        self.style = style
        self.full = full
        self.lineos = lineos

    def _repr_html_(self):
        return highlight(self.code, CppLexer(), HtmlFormatter(style=self.style, full=self.full, linenos=self.lineos))

