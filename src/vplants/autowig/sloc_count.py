from openalea.core.plugin.functor import PluginFunctor

__all__ = ['sloc_count']

sloc_count = PluginFunctor.factory('autowig.sloc_count')
#sloc_count.__class__.__doc__ = """Source Line Of Code counters functor
#
#.. seealso::
#    :attr:`plugin` for run-time available plugins.
#"""

class BasicSlocCountPlugin(object):
    """Basic plugin for source line of codes count"""

    def __call__(self):
        return self

    def implementation(self, content, *args, **kwargs):
        """
        """
        return content.count('\n')+1

sloc_count['basic'] = BasicSlocCountPlugin
#sloc_count.plugin = 'basic'

class IntermediateSlocCountPlugin(object):
    """Intermediate plugin for source line of codes count"""

    def __call__(self):
        return self

    def implementation(self, content, *args, **kwargs):
        """
        """
        return len([line for line in content.splitlines() if line])

sloc_count['intermediate'] = IntermediateSlocCountPlugin

class AdvancedSlocCountPlugin(object):
    """Advanced plugin for source of coudes count"""

    def implementation(self, content, language=None, *args, **kwargs):
        """
        """
        sloc = 0
        skip = False
        if language.lower() in ['c', 'c++']:
            for line in self.content.splitlines():
                line = line.strip()
                if line:
                    if line.startswith('//'):
                        continue
                    else:
                        if skip and '*/' in line:
                            line = line[line.index('*/')+2:]
                            skip = False
                        while '/*' in line and '*/' in line:
                            line = line[:line.index('/*')] + line[line.index('*/')+2:]
                        if '/*' in line:
                            skip = True
                        elif not skip and line.strip():
                            sloc += 1
        elif language.lower()[:2] == 'py':
            for line in self.content.splitlines():
                line = line.strip()
                if line:
                    if line.startswith('#'):
                        continue
                    else:
                        if skip:
                            if line.startswith('"""'):
                                skip = False
                        else:
                            if line.startswith('"""'):
                                skip = True
                            else:
                                sloc += 1
        else:
            warnings.warn('\'language\' parameter \'' + str(language) +'\' not found', UserWarning)
            sloc = intermediate_sloc(content)
        return sloc

sloc_count['advanced'] = AdvancedSlocCountPlugin
