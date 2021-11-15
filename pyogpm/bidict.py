'''
    ----
    (c) 2021 Wei Ke & Ka-Hou Chan
    license:          GPL-3
    license-file:     LICENSE
    ----

    bijective dictionary

'''


class BiDictError(Exception): pass
class UniqueInvError(BiDictError): pass
class InterInvError(BiDictError): pass

class bidict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inv = {}
        for k, v in self.items():
            self.inv.setdefault(v, []).append(k) 

    def __setitem__(self, k, v):
        if k in self:
            x = self[k]
            self.inv[x].remove(k) 
            if not self.inv[x]: 
                del self.inv[x]
        super().__setitem__(k, v)
        self.inv.setdefault(v, []).append(k)        

    def __delitem__(self, k):
        v = self[k]
        self.inv.setdefault(v, []).remove(k)
        if not self.inv[v]: 
            del self.inv[v]
        super().__delitem__(k)
        
    def unique_inv(self, v):
        ks = self.inv[v]
        if len(ks) != 1:
            raise UniqueInvError()
        return ks[0]
    

def dict_union(ds):
    return {k: v for d in ds for k, v in d.items()}

def bidict_union(bds):
    return bidict(dict_union(bds))


##
## end of bidict.py
##$Id: bidict.py 4838 2021-11-14 12:02:46Z wke@IPM.EDU.MO $
