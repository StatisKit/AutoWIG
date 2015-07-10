import warnings

def load_ipython_extension(ipython):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics or aliases, for example.
    try:
        from pygments import highlight
        from pygments.lexers import CLexer, CppLexer, PythonLexer
        from pygments.formatters import HtmlFormatter
    except ImportError as error:
        warnings.warn(error.msg, ImportWarning)
    except:
        raise
    else:
        from .asg import FileProxy

        def _repr_html_(self):
            from pygments import highlight
            from pygments.lexers import CLexer, CppLexer, PythonLexer
            from pygments.formatters import HtmlFormatter
            if not self.language is None:
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
                return str(self)

        FileProxy._repr_html_ = _repr_html_
        del _repr_html_

    try:
        from matplotlib import pyplot as plt
    except ImportError as error:
        warnings.warn(error.msg, ImportWarning)
    except:
        raise
    else:
        from .front_end import FrontEndDiagnostic, PostProcessingDiagnostic

        def plot(self, axes=None, norm=False, width=.8, rotation=30, *args, **kwargs):
            if axes is None:
                axes = plt.subplot(1,1,1)
            elif not isinstance(axes, plt.Axes):
                raise TypeError('`axes` parameter')
            y = [self.preprocessing, self.processing.total, self.checking, self.postprocessing.total]
            if norm:
                y = [i/self.total*100 for i in y]
            axes.bar([i-width/2. for i in range(len(y))], y, *args, **kwargs)
            axes.set_xticks(range(len(y)))
            axes.set_xticklabels(['Pre-processing', 'Processing', 'Checking', 'Post-Processing'], rotation=rotation)
            if norm:
                axes.set_ylabel('Time passed in each step (%)')
            else:
                axes.set_ylabel('Time passed in each step (s)')
            return axes

        FrontEndDiagnostic.plot = plot
        del plot

        def plot(self, axes=None, norm=False, width=.8, rotation=30, *args, **kwargs):
            if axes is None:
                axes = plt.subplot(1,1,1)
            elif not isinstance(axes, plt.Axes):
                raise TypeError('`axes` parameter')
            y = [self.overloading, self.purging]
            if norm:
                y = [i/self.total*100 for i in y]
            axes.bar([i-width/2. for i in range(len(y))], y, *args, **kwargs)
            axes.set_xticks(range(len(y)))
            axes.set_xticklabels(['Overloading', 'Purging'], rotation=rotation)
            if norm:
                axes.set_ylabel('Time passed in each step (%)')
            else:
                axes.set_ylabel('Time passed in each step (s)')
            return axes

        PostProcessingDiagnostic.plot = plot
        del plot

        from .libclang_front_end import LibclangDiagnostic

        def plot(self, axes=None, norm=False, width=.8, rotation=30, *args, **kwargs):
            if axes is None:
                axes = plt.subplot(1,1,1)
            elif not isinstance(axes, plt.Axes):
                raise TypeError('`axes` parameter')
            y = [self.parsing, self.translating]
            if norm:
                y = [i/self.total*100 for i in y]
            axes.bar([i-width/2. for i in range(len(y))], y, *args, **kwargs)
            axes.set_xticks(range(len(y)))
            axes.set_xticklabels(['Parsing', 'Translating'], rotation=rotation)
            if norm:
                axes.set_ylabel('Time passed in each step (%)')
            else:
                axes.set_ylabel('Time passed in each step (s)')
            return axes

        LibclangDiagnostic.plot = plot
        del plot

        from .middle_end import MiddleEndDiagnostic

        def plot(self, viewpoint='nodes', axes=None, *args, **kwargs):
            if axes is None:
                axes = plt.subplot(1,1,1)
            elif not isinstance(axes, plt.Axes):
                raise TypeError('`axes` parameter')
            if viewpoint == 'nodes':
                if not 'autopct' in kwargs:
                    kwargs['autopct'] = '%1.1f%%'
                elif kwargs['autopct'] is None:
                    kwargs.pop('autopct')
                axes.pie([self.previous-self.current, self.current-self.marked, self.marked], *args, labels=['Cleaned', 'Unchanged', 'Marked'], **kwargs)
                axes.axis('equal')
            elif viewpoint == 'timings':
                y = [self.cleaning, self.invalidating]
                xlabels = ['Cleaning', 'Invalidating']
                if not self.preprocessing is None:
                    y = [self.preprocessing.total] + y
                    xlabels = ['Pre-processing'] + xlabels
                norm = kwargs.pop('norm', False)
                if norm:
                    y = [i/self.total*100 for i in y]
                width = kwargs.pop('width', .8)
                axes.bar([i-width/2. for i in range(len(y))], y, *args, **kwargs)
                axes.set_xticks(range(len(y)))
                axes.set_xticklabels(xlabels, *args, rotation=kwargs.pop('rotation', 10), **kwargs)
                if norm:
                    axes.set_ylabel('Time passed in each step (%)')
                else:
                    axes.set_ylabel('Time passed in each step (s)')
            else:
                raise ValueError('\'viewpoint\' parameter')
            return axes

        MiddleEndDiagnostic.plot = plot
        del plot
