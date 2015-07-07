from .boost_python_back_end import set_boost_python_back_end

def set_back_end(back_end, *args, **kwargs):
    if back_end == 'boost_python':
        set_boost_python_back_end(*args, **kwargs)
    else:
        raise ValueError('\'back_end\' parameter')

set_back_end('boost_python')
