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

        from .back_end import BackEndDiagnostic

        def _repr_html_(self):
            return "<table>\n\t<tr>\n\t\t<th>Total files generated</th>\n\t\t<td>" + str(self.files) + " <i>(f)</i></td>\n\t</tr>\n\t<tr>\n\t\t<th>Total physical source lines of code</th>\n\t\t<td>" + str(self.sloc) + " <i>(l)</i></td>\n\t</tr>\n\t<tr>\n\t\t<th>Elapsed time</th>\n\t\t<td>" + str(round(self.elapsed, 2)) + " <i>(s)</i></td>\n\t</tr>\n\t<tr>\n\t\t<th> Basic COCOMO model software project</th>\n\t\t<td>" + self.project + "</td>\n\t</tr>\n\t<tr>\n\t\t<th>Development effort estimate</th>\n\t\t<td>" + str(round(self.effort, 2)) +" <i>(p/m)</i></td>\n\t</tr>\n\t<tr>\n\t\t<th>Schedule estimate</th>\n\t\t<td>" + str(round(self.schedule, 2)) + " <i>(m)</i></td>\n\t</tr>\n\t<tr>\n\t\t<th>Estimated average number of developers</th>\n\t\t<td>" + str(round(self.manpower, 2)) + " <i>(p)</i></td>\n\t</tr>\n</table></td></table>"

        BackEndDiagnostic._repr_html_ = _repr_html_
        del _repr_html_

    try:
        from matplotlib import pyplot as plt
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from tempfile import NamedTemporaryFile
        from IPython.core import display
    except ImportError as error:
        warnings.warn(error.msg, ImportWarning)
    except:
        raise
    else:
        from .asg import AbstractSemanticGraph, FileProxy, CodeNodeProxy, FundamentalTypeProxy
        from .tools import subclasses, lower

        #def plot(self, viewpoint='code', axes=None, norm=False, width=.8, rotation=30, *args, **kwargs):
        #    if axes is None:
        #        axes = plt.subplot(1,1,1)
        #    elif not isinstance(axes, plt.Axes):
        #        raise TypeError('`axes` parameter')
        #    if viewpoint == 'code':
        #        classes = subclasses(CodeNodeProxy, True)
        #        y = [0] * len(classes)
        #        for node in self.nodes(metaclass=CodeNodeProxy):
        #            y[classes.index(node.__class__)] += 1
        #        y, classes = zip(*[(value, cls) for value, cls in zip(y, classes) if not issubclass(cls, FundamentalTypeProxy) and issubclass(cls, CodeNodeProxy)])
        #        xlabels = [lower(cls.__name__.replace('Proxy', '')).replace('_', ' ').capitalize().replace('template partial specialization', 'TpS').replace('template specialization', 'TS').replace('constant', 'cst') for cls in classes]
        #        y, xlabels = zip(*[(value, xlabel) for value, xlabel in zip(y, xlabels) if value > 0])
        #    elif viewpoint == 'file':
        #        files = self.files()
        #        xlabels = {str(f.language) : 0 for f in files}
        #        for f in files:
        #            xlabels[str(f.language)] += 1
        #        y, xlabels = xlabels.values(), xlabels.keys()
        #    else:
        #        raise ValueError('\'viewpoint\' parameter')
        #    axes.bar([i-width/2. for i in range(len(y))], y, *args, **kwargs)
        #    axes.set_xticks(range(len(y)))
        #    axes.set_xticklabels(xlabels, rotation=rotation)
        #    if norm:
        #        axes.set_ylabel('Number of nodes (%)')
        #    else:
        #        axes.set_ylabel('Number of nodes (#)')
        #    return axes

        #AbstractSemanticGraph.plot = plot
        #del plot

        #def _repr_svg_(self):
        #    fig = Figure()
        #    axes = self.plot('code', axes=fig.add_subplot(1,2,1))
        #    axes.set_title('Code nodes')
        #    axes = self.plot('file', axes=fig.add_subplot(1,2,2))
        #    axes.set_title('File languages')
        #    canvas = FigureCanvasAgg(fig)
        #    filehandler = NamedTemporaryFile(suffix='.svg')
        #    canvas.print_figure(filehandler.name)
        #    ip_img = display.SVG(filename=filehandler.name)
        #    return ip_img._repr_svg_()

        #AbstractSemanticGraph._repr_svg_ = _repr_svg_
        #del _repr_svg_

        def _repr_html_(self):
            return '<img src="data:image/svg+xml;utf8,' + self._repr_svg_().replace('"', "'") + '" class="Image" />\n<style> img.Image { max-width: 100%; } </style>'

        from .front_end import FrontEndDiagnostic, PostProcessingDiagnostic

        def plot(self, viewpoint, axes=None, *args, **kwargs):
            if axes is None:
                axes = plt.subplot(1,1,1)
            elif not isinstance(axes, plt.Axes):
                raise TypeError('`axes` parameter')
            if viewpoint == 'asg':
                values = [self.constant, self.enum, self.typedef, self.variable, self.field, self.function,
                        self.method, self.constructor, self.destructor, self.class_non_template, self.class_template, self.namespace]
                values = [self.current-sum(values)] + values
                if not 'autopct' in kwargs:
                    def autopct(pct):
                        total=sum(values)
                        val=int(round(pct*total/100.0, 0))
                        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
                    kwargs['autopct'] = autopct
                labels = ['Other', 'Enum Constant', 'Enum', 'Typedef', 'Variable', 'Field', 'Function', 'Method',
                        'Constructor', 'Destructor', 'Class', 'Class Template', 'Namespace']
                values, labels = zip(*[(value, label) for value, label in zip(values, labels) if value > 0])
                axes.pie(values, *args, labels=labels, **kwargs)
                axes.axis('equal')
            elif viewpoint == 'step':
                y = [self.preprocessing, self.processing.total, self.postprocessing.total]
                norm = kwargs.pop('norm', False)
                if norm:
                    y = [i/self.total*100 for i in y]
                width = kwargs.pop('width', .8)
                axes.bar([i-width/2. for i in range(len(y))], y, *args, **kwargs)
                axes.set_xticks(range(len(y)))
                axes.set_xticklabels(['Pre-processing', 'Processing', 'Post-Processing'], *args, **kwargs)
                if norm:
                    axes.set_ylabel('Elapsed time (%)')
                else:
                    axes.set_ylabel('Elapsed time (s)')
            else:
                raise ValueError('\'viewpoint\' parameter')
            return axes

        FrontEndDiagnostic.plot = plot
        del plot

        def _repr_svg_(self):
            fig = Figure(figsize=(15,10))
            axes = self.plot('step', axes=fig.add_subplot(2,2,1))
            axes.set_title('Front-end steps')
            axes = self.plot('asg', axes=fig.add_subplot(2,2,2))
            axes.set_title('Abstract Semantic Graph')
            axes = self.processing.plot(axes=fig.add_subplot(4,2,5), norm=True)
            axes.set_title('Front-end ' + self.processing.name + ' processing step')
            axes = self.postprocessing.plot(axes=fig.add_subplot(4,2,6), norm=True)
            axes.set_title('Front-end post-processing step')
            canvas = FigureCanvasAgg(fig)
            filehandler = NamedTemporaryFile(suffix='.svg')
            canvas.print_figure(filehandler.name)
            plt.close(fig)
            ip_img = display.SVG(filename=filehandler.name)
            return ip_img._repr_svg_()

        FrontEndDiagnostic._repr_svg_ = _repr_svg_
        del _repr_svg_

        FrontEndDiagnostic._repr_html_ = _repr_html_

        def plot(self, axes=None, norm=False, width=.8, rotation=0, *args, **kwargs):
            if axes is None:
                axes = plt.subplot(1,1,1)
            elif not isinstance(axes, plt.Axes):
                raise TypeError('`axes` parameter')
            y = [self.overloading, self.discarding, self.accessing]
            if norm:
                y = [i/self.total*100 for i in y]
            axes.bar([i-width/2. for i in range(len(y))], y, *args, **kwargs)
            axes.set_xticks(range(len(y)))
            axes.set_xticklabels(['Overloading', 'Discarding', 'Accessing'], rotation=rotation)
            if norm:
                axes.set_ylabel('Elapsed time (%)')
            else:
                axes.set_ylabel('Elapsed time (s)')
            return axes

        PostProcessingDiagnostic.plot = plot
        del plot

        def _repr_svg_(self):
            fig = Figure(figsize=(5,5))
            axes = self.plot(axes=fig.add_subplot(1,1,1))
            axes.set_title('Front-end post-processing step')
            canvas = FigureCanvasAgg(fig)
            filehandler = NamedTemporaryFile(suffix='.svg')
            canvas.print_figure(filehandler.name)
            plt.close(fig)
            ip_img = display.SVG(filename=filehandler.name)
            return ip_img._repr_svg_()

        PostProcessingDiagnostic._repr_svg_ = _repr_svg_
        del _repr_svg_

        PostProcessingDiagnostic._repr_html_ = _repr_html_

        from .libclang_front_end import LibclangDiagnostic

        def plot(self, axes=None, norm=False, width=.8, rotation=0, *args, **kwargs):
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
                axes.set_ylabel('Elapsed time (%)')
            else:
                axes.set_ylabel('Elapsed time (s)')
            return axes

        LibclangDiagnostic.plot = plot
        del plot

        from .pyclang_front_end import PyClangDiagnostic

        def plot(self, axes=None, norm=False, width=.8, rotation=0, *args, **kwargs):
            if axes is None:
                axes = plt.subplot(1,1,1)
            elif not isinstance(axes, plt.Axes):
                raise TypeError('`axes` parameter')
            y = [self.parsing, self.translating, self.bootstrapping]
            if norm:
                y = [i/self.total*100 for i in y]
            axes.bar([i-width/2. for i in range(len(y))], y, *args, **kwargs)
            axes.set_xticks(range(len(y)))
            axes.set_xticklabels(['Parsing', 'Translating', 'Bootstrapping'], rotation=rotation)
            if norm:
                axes.set_ylabel('Elapsed time (%)')
            else:
                axes.set_ylabel('Elapsed time (s)')
            return axes

        PyClangDiagnostic.plot = plot
        del plot

        def _repr_svg_(self):
            fig = Figure(figsize=(5,5))
            axes = self.plot(axes=fig.add_subplot(1,1,1))
            axes.set_title('Front-end libclang processing step')
            canvas = FigureCanvasAgg(fig)
            filehandler = NamedTemporaryFile(suffix='.svg')
            canvas.print_figure(filehandler.name)
            plt.close(fig)
            ip_img = display.SVG(filename=filehandler.name)
            return ip_img._repr_svg_()

        LibclangDiagnostic._repr_svg_ = _repr_svg_
        PyClangDiagnostic._repr_svg_ = _repr_svg_
        del _repr_svg_

        LibclangDiagnostic._repr_html_ = _repr_html_
        LibclangDiagnostic._repr_html_ = _repr_html_

        from .middle_end import MiddleEndDiagnostic

        def plot(self, viewpoint='nodes', axes=None, *args, **kwargs):
            if axes is None:
                axes = plt.subplot(1,1,1)
            elif not isinstance(axes, plt.Axes):
                raise TypeError('`axes` parameter')
            if viewpoint == 'asg':
                values = [self.previous - self.current,
                        self.current - self.invalidated,
                        self.invalidated]
                if not 'autopct' in kwargs:
                    def autopct(pct):
                        total=sum(values)
                        val=int(round(pct*total/100.0, 0))
                        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
                    kwargs['autopct'] = autopct
                colors = kwargs.pop('colors', dict(Cleaned = 'r', Unchanged = 'g', Invalidated = 'y'))
                labels = ['Cleaned', 'Unchanged', 'Invalidated']
                values, labels = zip(*[(value, label) for value, label in zip(values, labels) if value > 0])
                colors = [colors[label] for label in labels]
                axes.pie(values, *args, labels=labels, colors=colors, **kwargs)
                axes.axis('equal')
            elif viewpoint == 'step':
                y = [self.cleaning, self.invalidating]
                xlabels = ['Cleaning', 'Invalidating']
                if not self.preprocessing is None:
                    y = [self.preprocessing] + y
                    xlabels = ['Pre-processing'] + xlabels
                norm = kwargs.pop('norm', False)
                if norm:
                    y = [i/self.total*100 for i in y]
                width = kwargs.pop('width', .8)
                axes.bar([i-width/2. for i in range(len(y))], y, *args, **kwargs)
                axes.set_xticks(range(len(y)))
                axes.set_xticklabels(xlabels, *args, **kwargs)
                if norm:
                    axes.set_ylabel('Elapsed time (%)')
                else:
                    axes.set_ylabel('Elapsed time (s)')
            else:
                raise ValueError('\'viewpoint\' parameter')
            return axes

        MiddleEndDiagnostic.plot = plot
        del plot

        def _repr_svg_(self):
            fig = Figure(figsize=(15,5))
            axes = self.plot('step', axes=fig.add_subplot(1,2,1))
            axes.set_title('Middle-end steps')
            axes = self.plot('asg', axes=fig.add_subplot(1,2,2))
            axes.set_title('Abstract Semantic Graph')
            canvas = FigureCanvasAgg(fig)
            filehandler = NamedTemporaryFile(suffix='.svg')
            canvas.print_figure(filehandler.name)
            plt.close(fig)
            ip_img = display.SVG(filename=filehandler.name)
            return ip_img._repr_svg_()

        MiddleEndDiagnostic._repr_svg_ = _repr_svg_
        del _repr_svg_

        MiddleEndDiagnostic._repr_html_ = _repr_html_

        del _repr_html_
