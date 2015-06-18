__all__ = []

try:
    from pygments import highlight
    from pygments.lexers import CLexer, CppLexer, PythonLexer
    from pygments.formatters import HtmlFormatter

    from .asg import FileProxy

    def _repr_html_(self):
        if hasattr(self, 'language'):
            if self.language == 'c':
                lexer = CLexer()
            elif self.language == 'c++':
                lexer = CppLexer()
            elif self.language == 'py':
                lexer = PythonLexer()
            else:
                raise NotImplementedError('\'language\': '+str(self.language))
            return highlight(str(self), lexer, HtmlFormatter(full = True))
        else:
            raise NotImplementedError('')

    FileProxy._repr_html_ = _repr_html_
    del _repr_html_

except:
    pass
