"""
"""

def generatorer(asg, pattern='(.*)', database=None):
    for f in asg.boost_python_exports(pattern=pattern):
        f.write(database=database)
    for f in asg.boost_python_modules(pattern=pattern):
        f.write(database=database)
