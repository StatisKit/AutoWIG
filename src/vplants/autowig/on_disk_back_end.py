import time
from vplants.autowig.back_end import BackEndDiagnostic

def on_disk_back_end(asg, pattern='(.*)', database=None):
    for f in asg.files(pattern=pattern):
        f.write(database=database)
