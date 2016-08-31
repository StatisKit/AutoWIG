import os
import parse
from path import path


def gcc_5_feedback(err, directory, asg, **kwargs):
    if not isinstance(err, basestring):
        raise TypeError('\'err\' parameter')
    if not isinstance(directory, path):
        directory = path(directory)
    variantdir = kwargs.pop('variantdir', None)
    if variantdir:
        variantdir = directory/variantdir
    else:
        variantdir = directory
    indent = kwargs.pop('indent', 0)
    directory = str(directory.abspath()) + os.sep
    variantdir = str(variantdir.relpath(directory))
    if variantdir == '.':
        variantdir = ''
    else:
        variantdir += os.sep
    wrappers = dict()
    for line in err.splitlines():
        parsed = parse.parse(variantdir+'{filename}:{row}:{column}:{message}', line)
        if parsed:
            try:
                row = int(parsed['row'])
                node = directory + parsed['filename']
                if node in asg:
                    if node not in wrappers:
                        wrappers[node] = [row]
                    else:
                        wrappers[node].append(row)
            except:
                pass
    code = []
    for wrapper, rows in wrappers.iteritems():
        wrapper = asg[wrapper]
        for row in rows:
            code.extend(wrapper.edit(row).splitlines())
    code = "\t" * indent + ("\n" + "\t" * indent).join(code for code in code if code)
    if not code.isspace():
        code += '\n'
    return code
