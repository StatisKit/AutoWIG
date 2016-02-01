import time
from .back_end import BackEndDiagnostic

def on_disk_back_end(asg, pattern='(.*)', database=None):
    for f in asg.files(pattern=pattern):
        f.write(database=database)
