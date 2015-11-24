import time
from vplants.autowig.middle_end import MiddleEndDiagnostic

def default_middle_end(asg, *args, **kwargs):
    asg.clean()
