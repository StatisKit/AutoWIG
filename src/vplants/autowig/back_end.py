from .tools import FactoryDocstring
from .boost_python_back_end import *
from .bootstrap_back_end import *

def back_end(self, identifier=None, *args, **kwargs):
    back_end = getattr(self, '_' + identifier + '_back_end')
    return back_end(*args, **kwargs)

AbstractSemanticGraph.back_end = back_end
del back_end
FactoryDocstring.as_factory(AbstractSemanticGraph.back_end)
