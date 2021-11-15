'''
    ----
    (c) 2021 Wei Ke & Ka-Hou Chan
    license:          GPL-3
    license-file:     LICENSE
    ----

    types and subtyping rules

'''

from collections import namedtuple

from pp import PrfxPP, sorted_list

class SubtypeError(Exception): pass
class DuplicateClassError(SubtypeError): pass
class UndefinedClassError(SubtypeError): pass
class AttrTypeConflictError(SubtypeError): pass
class MinTypeError(SubtypeError): pass

Tag = namedtuple('Tag', ['id'])
Lazy = namedtuple('Lazy', ['tag'])

def is_anon_tag(tag):
    return not tag or tag.id[0] == '*'

CLA_TAB = {}

class Cla:
    def __init__(self, tag, supers = [], attrs = [], tags = []):
        if tag:
            if tag in CLA_TAB:
                raise DuplicateClassError()
            CLA_TAB[tag] = self
        
        self.tag = tag
        self.tags = set(tags)
        if not is_anon_tag(tag):
            self.tags.add(tag)
            
        self.attrs = dict(attrs)
        
        for su in supers:
            self.tags.update(su.tags)
            for la, ty in su.attrs.items():
                if la in self.attrs:
                    if self.attrs[la] != ty:
                        raise AttrTypeConflictError()
                else:
                    self.attrs[la] = ty
                    
        self.hashcode_cache = self.compute_hash()
                    
    def compute_hash(self):
        s = list(self.tags)
        s.sort()
        return hash(('Cla', tuple(s)))
                    
    def resolve_lazy(self):
        lzs = [(la, ty) for la, ty in self.attrs.items() if type(ty) is Lazy]
        for la, ty in lzs:
            self.attrs[la] = CLA_TAB[ty.tag]
        return self        

    def __eq__(self, y):
        if self is y:
            return True
        
        if not is_anon_tag(self.tag) and self.tag == y.tag:
            return True
        
        return self.tags == y.tags
    
    def __hash__(self):
        return self.hashcode_cache

    def __le__(self, y):
        if self is y:
            return True
        
        if not is_anon_tag(self.tag) and self.tag == y.tag:
            return True

        return self.tags >= y.tags
    
    def to_pp(self):
        pp = {}
        pp['class tag'] = None if self.tag is None else self.tag.id
        pp['supers'] = sorted_list(tag.id for tag in self.tags)
        pp['attrs'] = {la.id: cla.tag.id for la, cla in self.attrs.items()}
        return PrfxPP('Cla', pp)

    @staticmethod
    def get(tag):
        if tag not in CLA_TAB:
            raise UndefinedClassError()
        return CLA_TAB[tag]
    
    @staticmethod
    def reset():
        CLA_TAB = {}

    @staticmethod
    def inter(cs):
        return Cla(None, cs)

    @staticmethod
    def union(cs):
        tags = set.intersection(*(cla.tags for cla in cs))
        attrs = set.intersection(*(set(cla.attrs.items()) for cla in cs))
        return Cla(None, [], attrs, tags)
    
NO_TYPE = Cla(Tag('*TOP'))
NULL_TYPE = Cla(Tag('NULL'), set(), {})
INT_TYPE = Cla(Tag('INT'), set(), {})
STR_TYPE = Cla(Tag('STR'), set(), {})
BOOL_TYPE = Cla(Tag('BOOL'), set(), {})

VALUE_TYPES = {INT_TYPE, STR_TYPE, BOOL_TYPE}

Value = namedtuple('Value', ['cla', 'value'])

class ValueSet:
    def __init__(self, vs):
        self.values = set(vs)
        s = list(self.values)
        s.sort()
        self.vector = tuple(s)
        
    def __hash__(self):
        return hash(('ValueSet', self.vector))
    
    def __eq__(self, y):
        return self.vector == y.vector
        
def subtype(x, y):
    if x is NULL_TYPE:
        return True
    
    if type(x) is Cla and type(y) is Cla:
        return x <= y
    
    if type(x) is ValueSet and type(y) is ValueSet:
        return x.values <= y.values
    
    if type(x) is ValueSet and type(y) is Cla:
        return all(v.cla == y for v in x.values) 
    
    return False

def min_type(x, y):
    if subtype(x, y):
        return x
    
    if subtype(y, x):
        return y
    
    raise MinTypeError()

def classof(x, path = []):
    if type(x) is ValueSet:
        if path:
            return None
        clas = set(v.cla for v in x.values)
        if len(clas) != 1:
            return None
        return clas.pop()
    
    if type(x) is Cla:
        cla = x 
        for na in path:
            if na not in cla.attrs:
                return None
            cla = cla.attrs[na]
        return cla
    
    return None

def exists_ty_le_all(ts):
    clas = [classof(t) for t in ts]
    if any(cla is None for cla in clas):
        return False
    
    if any(cla in VALUE_TYPES for cla in clas):
        return len(set(clas)) == 1
    
    return True

def ty_inf(ts):
    clas = [classof(t) for t in ts]
    if any(cla in VALUE_TYPES for cla in clas):
        vss = [t for t in ts if type(t) is ValueSet]
        if vss:
            return ValueSet(set().union(*[vs.values for vs in vss]))
        else:
            return clas[0]
    else:
        return Cla.inter(clas)

def ty_sup(ts):
    clas = [classof(t) for t in ts]
    if any(cla in VALUE_TYPES for cla in clas):
        vss = [t for t in ts if type(t) is ValueSet]
        if vss:
            return ValueSet(set().intersection(*[vs.values for vs in vss]))
        else:
            return clas[0]
    else:
        return Cla.union(clas)


##
## end of subtype.py
##$Id: subtype.py 4838 2021-11-14 12:02:46Z wke@IPM.EDU.MO $

