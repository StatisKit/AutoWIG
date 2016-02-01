from openalea.core.plugin.functor import PluginFunctor

from autowig.asg import AbstractSemanticGraph

__all__ = ['back_end']

class BackEndDiagnostic(object):
    """Diagnostic class for AutoWIG back-ends.

    This class enable to perform a basic analysis of called back-ends.
    In particular, time elapsed (:attr:`elapsed`) for this step is stored and a brief summary of generated files is performed:

    * :attr:`files` denotes the total number of files generated.
    * :attr:`sloc` denotes the total number of source line of codes counted (see :var:`autowig.sloc_count.sloc_count`).
    * :attr:`project` denotes the type of basic COCOMO model software project ('organic', 'semi-detached' or 'embded').
    * :attr:`effort` denotes the estimated number of persons by month considering the basic COCOMO model.
    * :attr:`schedule` denotes the estimated number of months necessary to deliver considering the basic COCOMO model.
    * :attr:`manpower` denotes the estimated number of persons necessary to deliver considering the basic COCOMO model.
    .. seealso::
        :var:`back_end` for a detailed documentation about AutoWIG back-end step.
        :func:`autowig.boost_python_back_end.back_end` for an example.
    """

    def __init__(self):
        self.files = 0
        self.sloc = 0
        self.elapsed = 0.0
        self.project = "semi-detached"
        self.on_disk = False

    @property
    def effort(self):
        if self.project == 'organic':
            return 2.4 * (self.sloc/1000.) ** 1.05
        elif self.project == 'semi-detached':
            return 3.0 * (self.sloc/1000.) ** 1.12
        elif self.project == 'embedded':
            return 3.6 * (self.sloc/1000.) ** 1.20

    @property
    def schedule(self):
        if self.project == 'organic':
            return 2.5 * self.effort ** (.38)
        elif self.project == 'semi-detached':
            return 2.5 * self.effort ** (.35)
        elif self.project == 'embedded':
            return 2.5 * self.effort ** (.32)

    @property
    def manpower(self):
        return self.effort/self.schedule

    def __str__(self):
        string = "Total physical source lines of code: " + str(self.sloc) + " (line)"
        string += "\nDevelopment effort estimate: " + str(round(self.effort, 2)) + " (person/month)"
        string += "\nSchedule estimate: " + str(round(self.schedule, 2)) + " (month)"
        string += "\nEstimated average number of developers: " + str(round(self.manpower, 2)) + "(person)"
        return string

def get_project(self):
    return self._project

def set_project(self, project):
    if not isinstance(project, basestring):
        raise TypeError('\'project\' parameter')
    if not project in ['organic', 'semi-detached', 'embedded']:
        raise ValueError('\'project\' parameter')
    self._project = project

BackEndDiagnostic.project = property(get_project, set_project)
del get_project, set_project

back_end = PluginFunctor.factory('autowig.back_end')
#back_end.__class__.__doc__ = """AutoWIG back-ends functor
#
#.. seealso::
#    :attr:`plugin` for run-time available plugins.
#"""
