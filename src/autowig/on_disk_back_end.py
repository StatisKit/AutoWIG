"""
"""

def back_end(asg, pattern='(.*)', database=None):
    for f in asg.files(pattern=pattern):
        f.write(database=database)
