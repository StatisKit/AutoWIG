import os
import parse
from path import path

from ._scons import ShellSession

def gcc_5_feedback(err, directory, asg, **kwargs):
    if isinstance(err, ShellSession):
        err = err.err
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
    tabsize = kwargs.pop('tabsize', None)
    filename = kwargs.pop('filename', None)
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
    force = kwargs.pop('force', False)
    code = []
    for wrapper, rows in wrappers.iteritems():
        wrapper = asg[wrapper]
        if len(rows) == 1:
            row = rows[-1]
            edit = getattr(wrapper, '_feedback', None)
            if edit:
                with open(wrapper.globalname, 'r') as filehandler:
                    lines = filehandler.readlines()
                    if len(lines) == row and force:
                        code.extend(edit(None).splitlines())
                    else:
                        code.extend(edit(row).splitlines())
        else:
            edit = getattr(wrapper, '_feedback', None)
            if edit:
                for row in rows:
                    code.extend(edit(row).splitlines())
    code = "\t" * indent + ("\n" + "\t" * indent).join(code for code in code if code)
    if not code.isspace():
        code += '\n'
        if tabsize:
            code = code.expandtabs(tabsize)
        if filename:
            with open(filename, 'w') as filehandler:
                filehandler.write(code)
        return code
