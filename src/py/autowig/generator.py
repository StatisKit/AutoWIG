from .asg import *

class IteratorRange(object):

    def __init__(self, asg, begin=None, end=None):
        self._asg = asg
        if begin:
            self._begin = begin._node
        if end:
            self._end = end._node

    def __nonzero__(self):
        return self._asg is not None and self.begin.return_type.desugared_type.globalname == self.end.return_type.desugared_type.globalname

    @property
    def begin(self):
        if self._asg:
            return self._asg[self._begin]

    @property
    def end(self):
        if self._asg:
            return self._asg[self._end]

    @property
    def iterator(self):
        if self._asg:
            return self.begin.return_type.desugared_type.unqualified_type

def iterator_range(cls):
    begins = []
    ends   = []
    for method in cls.methods():
        if method.localname == 'begin' and method.nb_parameters == 0 and not method.is_static:
            begins.append(method)
        elif method.localname == 'end' and method.nb_parameters == 0 and not method.is_static:
            ends.append(method)
    const = False
    if len(begins) == 1 or len(ends) == 1:
        if len(begins) > 1:
            const = ends[0].is_const
        elif len(ends) > 1:
            const = begins[0].is_const
    if len(begins) == 2:
        if const:
            if begins[0].is_const:
                begins = [begins[0]]
            else:
                begins = [begins[-1]]
        else:
            if begins[0].is_const:
                begins = [begins[-1]]
            else:
                begins = [begins[0]]
    if len(ends) == 2:
        if const:
            if ends[0].is_const:
                ends = [ends[0]]
            else:
                ends = [ends[-1]]
        else:
            if ends[0].is_const:
                ends = [ends[-1]]
            else:
                ends = [ends[0]]
    if len(begins) == 1 and len(ends) == 1:
        return IteratorRange(cls._asg, begins.pop(), ends.pop())
    else:
        return IteratorRange(None)
