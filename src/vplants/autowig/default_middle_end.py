import time
from vplants.autowig.middle_end import MiddleEndDiagnostic

def default_middle_end(asg, *args, **kwargs):
    diagnostic = MiddleEndDiagnostic()
    diagnostic.previous = len(asg)
    prev = time.time()
    asg.clean()
    curr = time.time()
    diagnostic.cleaning = curr - prev
    diagnostic.current = len(asg)
    return diagnostic
