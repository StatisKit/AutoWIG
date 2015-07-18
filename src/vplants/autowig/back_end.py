from .asg import AbstractSemanticGraph
from .tools import FactoryDocstring

class BackEndDiagnostic(object):

    def __init__(self, asg):
        self._asg = asg
        self._files = []
        self.elapsed = 0.0
        self.project = "semi-detached"
        self.salary = 56286
        self.overhead = 2.4

    def __len__(self):
        return len(self._files)

    def __getitem__(self, item):
        return self._asg[self._files[item]]

    @property
    def sloc(self):
        sloc = 0
        for f in self:
            sloc += f.content.count('\n')+1
        return sloc

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

    @property
    def cost(self):
        return self.overhead * self.salary * self.effort/12

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

def back_end(self, identifier=None, *args, **kwargs):
    back_end = getattr(self, '_' + identifier + '_back_end')
    return back_end(*args, **kwargs)

AbstractSemanticGraph.back_end = back_end
del back_end
FactoryDocstring.as_factory(AbstractSemanticGraph.back_end)

from .boost_python_back_end import *
from .bootstrap_back_end import *
