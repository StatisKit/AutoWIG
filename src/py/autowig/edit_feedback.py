from _feedback import parse_errors

def edit_feedback(err, directory, asg, **kwargs):  
    wrappers = parse_errors(err, directory, asg, **kwargs)
    code = []
    for wrapper, rows in wrappers.iteritems():
        wrapper = asg[wrapper]
        for row in rows:
            code.extend(wrapper.edit(row).splitlines())
    indent = kwargs.pop('indent', 0)
    code = "\t" * indent + ("\n" + "\t" * indent).join(code for code in code if code)
    if not code.isspace():
        code += '\n'
    return code.strip()
