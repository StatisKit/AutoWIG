from _feedback import parse_errors

def comment_feedback(err, directory, asg, **kwargs):
    wrappers = parse_errors(err, directory, asg, **kwargs)
    for wrapper, rows in wrappers.iteritems():
        with open(wrapper, 'r') as filehandler:
            content = filehandler.readlines()
        for row in rows:
            if row < len(content):
                content[row - 1] = '// TODO ' + content[row - 1]
            with open(wrapper, 'w') as filehandler:
                filehandler.writelines(content)
    return hash(frozenset(wrappers))
