"""
"""

class Class(object):
    """
    """

    def __init__(self, cursor):
        self.name = cursor.spelling
        self.variables = []
        self.functions = []
