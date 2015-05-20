import os

class Scope(object):

    def __init__(self, name, uniformize=True):
        if uniformize:
            self.name = ''
            index = 0
            for char in name:
                if char in ['<', ',']:
                    self.name += char + ' '
                elif char == '>':
                    self.name += ' >'
                elif char in ['*', '&']:
                    self.name += ' '+char
                else:
                    self.name += char
            self.name = ' '.join(self.name.split()).replace('& &', '&&')
        else:
            self.name = name

    def __repr__(self):
        return self.name

    def __len__(self):
        return len(self.name)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Scope(self.name[index], False)
        else:
            return self.name[index]

    @property
    def is_global(self):
        return self.name.startswith('::')

    def split(self):
        if self.has_scopes:
            scopes = []
            current = 0
            previous = 0
            delimiter = 0
            while current < len(self):
                if self[current] in ['<', '(', '[']:
                    delimiter += 1
                    current += 1
                elif self[current] in ['>', ')', ']']:
                    delimiter -= 1
                    current += 1
                elif delimiter == 0 and self[current:current+2].name == '::':
                    if not self.is_global or not previous == 0:
                        scope = self[previous:current]
                        scope.has_scopes = False
                        scopes.append(scope)
                    current += 2
                    previous = current
                else:
                    current += 1
            scope = self[previous:current]
            scope.has_scopes = False
            scopes.append(scope)
            return scopes
        else:
            return [self]

    def to_path(self, lower=True):
        scopes = self.split()
        for index, scope in enumerate(scopes):
            scope = scope.name
            for delimiter in ['<', '(', '[', ']', ')', '>']:
                scope = scope.replace(delimiter, '_')
            scopes[index] = scope.replace(' ', '_')
        path = os.sep.join(scopes)
        if lower: path = path.lower()
        return path

    @property
    def has_templates(self):
        return self[-1].endswith('>')

    def remove_templates(self, nb=None):
        index = 0
        delimiter = 0
        while delimiter == 0 and index < len(self):
            if self[index] == '<':
                delimiter += 1
            else:
                index += 1
        if nb is None:
            return self[:index]
        else:
            raise NotImplementedError()

def get_has_scopes(self):
    if not hasattr(self, '_has_scopes'):
        index = 0
        delimiter = 0
        found = self.is_global
        while not found and not index == len(self):
            if self[index] in ['<', '(', '[']:
                delimiter += 1
                index += 1
            elif self[index] in ['>', ')', ']']:
                delimiter -= 1
                index += 1
            elif delimiter == 0 and self[index:index+2].name == '::':
                found = True
            else:
                index += 1
        if found:
            self._has_scopes = True
        else:
            self._has_scopes = False
    return self._has_scopes

def set_has_scopes(self, has_scopes):
    self._has_scopes = has_scopes

Scope.has_scopes = property(get_has_scopes, set_has_scopes)
del get_has_scopes, set_has_scopes

def get_templates(self):
    if self.has_scopes:
        return self.scopes[-1].templates
    else:
        delimiter = 0
        index = 0
        while delimiter == 0 and index < len(self):
            if self[index] == '<':
                delimiter += 1
            index += 1
        if index == len(self):
            return []
        else:
            templates = ['']
            for char in self.name[index:]:
                if char == '<':
                    delimiter += 1
                elif char == '>':
                    delimiter -= 1
                elif delimiter == 1 and char == ',':
                    templates[-1] = templates[-1].strip()
                    templates.append('')
                else:
                    templates[-1] += char
            templates[-1] = templates[-1].strip()
            return [Scope(template, False) for template in templates]

Scope.templates = property(get_templates)
del get_templates
