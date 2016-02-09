__all__ = ['camel_case_to_lower', 'to_camel_case', 'camel_case_to_upper']

def subclasses(cls, recursive=True):
    if recursive:
        subclasses = []
        front = [cls]
        while len(front) > 0:
            cls = front.pop()
            front.extend(cls.__subclasses__())
            subclasses.append(cls)
        return {subclass.__name__ : subclass for subclass in subclasses}.values()
    else:
        return cls.__subclasses__()

def camel_case_to_lower(name):
    """
    :Examples:
    >>> camel_case_to_lower('squareRoot')
    'square_root'
    >>> camel_case_to_lower('SquareRoot')
    'square_root'
    >>> camel_case_to_lower('ComputeSQRT')
    'compute_sqrt'
    >>> camel_case_to_lower('SQRTCompute')
    'sqrt_compute'
    """
    lowername = '_'
    index = 0
    while index < len(name):
        if name[index].islower():
            lowername += name[index]
            index += 1
        else:
            if not name[index] == '_':
                if not lowername[-1] == '_':
                    lowername += '_'
                lowername += name[index].lower()
                index += 1
                if index < len(name) and not name[index].islower():
                    while index < len(name) and not name[index].islower():
                        lowername += name[index].lower()
                        index += 1
                    if index < len(name):
                        lowername = lowername[:-1] + '_' + lowername[-1]
            else:
                if not lowername[-1] == '_':
                    lowername += '_'
                index += 1
    lowername = lowername.lstrip('_')
    return lowername

def camel_case_to_upper(name):
    """
    :Examples:
    >>> camel_case_to_upper('squareRoot')
    'SQUARE_ROOT'
    >>> camel_case_to_upper('SquareRoot')
    'SQUARE_ROOT'
    >>> camel_case_to_upper('ComputeSQRT')
    'COMPUTE_SQRT'
    >>> camel_case_to_upper('SQRTCompute')
    'SQRT_COMPUTE'
    >>> camel_case_to_upper('Char_U')
    """
    lowername = '_'
    index = 0
    while index < len(name):
        if name[index].islower():
            lowername += name[index].upper()
            index += 1
        else:
            if not name[index] == '_':
                if not lowername[-1] == '_':
                    lowername += '_'
                lowername += name[index].upper()
                index += 1
                if index < len(name) and not name[index].islower():
                    while index < len(name) and not name[index].islower():
                        lowername += name[index]
                        index += 1
                    if index < len(name):
                        lowername = lowername[:-1] + '_' + lowername[-1]
            else:
                if not lowername[-1] == '_':
                    lowername += '_'
                index += 1
    lowername = lowername.lstrip('_')
    return lowername

def to_camel_case(name):
    """
    :Examples:
    >>> lower_to_camel_case(camel_case_to_lower('squareRoot'))
    'SquareRoot'
    >>> lower_to_camel_case(camel_case_to_lower('SquareRoot'))
    'SquareRoot'
    >>> lower_to_camel_case(camel_case_to_lower('ComputeSQRT'))
    'ComputeSqrt'
    >>> lower_to_camel_case(camel_case_to_lower('SQRTCompute'))
    'SqrtCompute'
    """
    camelname = ''
    index = 0
    while index < len(name):
        if name[index] == '_':
            index += 1
            while index < len(name) and name[index] == '_':
                index += 1
            if index < len(name):
                camelname += name[index].upper()
        else:
            camelname += name[index]
        index += 1
    if camelname[0].islower():
       camelname  = camelname[0].upper() + camelname[1:]
    return camelname
