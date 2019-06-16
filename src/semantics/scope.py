class scope:
    def __init__(self, _class, _parent = None):
        self._class = _class
        self._types = {}
        self._parent = _parent
        self._objs = {'self': _class}
        self._methods = {}

    def to_define_type(self, name, parent):
        self._types[name] = parent
        self._methods[name] = []

    def O(self, v, t):
        self._objs[v] = t

    def M(self, c, f):
        self._methods[c].append(f)

    def is_define_obj(self, v):
        if self._parent == None:
            return self._objs[v] if v in self._objs else False
        return self._objs[v] if v in self._objs else self._parent.is_define_obj(v)

    def is_define_method(self, c, name):
        method = None
        for m in self._methods[c]:
            if m[0] == name:
                method = m[1:]
                break
        return False if not method else method

    def is_define_type(self, t):
        return t in self._types

    def inherits(self, t1, t2):
        return self._types[t1] == t2

    def join(self, t1, t2):
        t1_parents = []
        t2_parents = []
        parent = self._types[t1]
        while (parent):
            t1_parents.append(parent)
            parent = self._types[parent]
        parent = self._types[t2]
        while (parent):
            t2_parents.append(parent)
            parent = self._types[parent]
        same_parent = 'Object'
        i = len(t1_parents) - 1
        j = len(t2_parents) - 1
        while (i >= 0 and j >= 0):
            if t1_parents[i] == t2_parents[j]:
                same_parent = t1_parents[j]
            i-=1
            j-=1
        return same_parent

    def createChildScope(self, _class = None):
        c = _class if _class else self._class
        sc = scope(c, self)
        sc._types = self._types
        sc._methods = self._methods
        return sc