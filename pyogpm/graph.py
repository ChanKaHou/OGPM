'''
    ----
    (c) 2021 Wei Ke & Ka-Hou Chan
    license:          GPL-3
    license-file:     LICENSE
    ----

    graphs and graph algorithms

'''

from collections import namedtuple
from queue import Queue

from bidict import bidict
from pp import PrfxPP, sorted_list

from subtype import (
    NULL_TYPE,
    ValueSet, 
    exists_ty_le_all,
    ty_inf,
    ty_sup)

from pattern import (
    LabeledPattern, 
    PatternRef, 
    ClassPattern) 

LayoutGraph = namedtuple('LayoutGraph', ['nodes', 'edges', 'root'])
PatternGraph = namedtuple('PatternGraph', ['layout', 'types'])
StateGraph = namedtuple('StateGraph', ['layout', 'types', 'values'])
Node = namedtuple('Node', ['id'])
Label = namedtuple('Label', ['id'])
Edges = namedtuple('Edges', ['labels', 'targets'])

class GraphError(Exception): pass
class Mismatch(GraphError):  pass
class NoUnion(GraphError):  pass
class NoConj(GraphError):  pass
class UndefRef(GraphError):  pass
class RedefRef(GraphError):  pass
class NoScope(GraphError):  pass
class UndefVar(GraphError):  pass
class UndefAttr(GraphError):  pass

def unzip2(s):
    if not s:
        return ([], [])
    else:
        return list(zip(*s))

def unzip4(s):
    if not s:
        return ([], [], [], [])
    else:
        return list(zip(*s))

def set_union(ss):
    return set().union(*ss)

def set_inter(ss):
    i = iter(ss)
    for s in i:
        return set(s).intersection(*i)
    
    return set()

def layout_graph_to_pp(g):
    ns, es, p = g
    pp = {}
    pp['root'] = '({})'.format(p.id)
    pp['nodes'] = sorted_list(u.id for u in ns)
    pp['edges'] = {u.id: [(la.id, es.targets[(u, la)].id) for la in es.labels[u]] for u in sorted_list(ns)}
    return PrfxPP('LayoutGraph', pp)

class NodeFactory:
    def __init__(self):
        self._cur_id = 0
    
    def new_node(self):
        self._cur_id += 1
        return Node(self._cur_id)

NODE_FACTORY = NodeFactory()

def new_node():
    return NODE_FACTORY.new_node()

def init_state_graph():
    p = new_node()
    return StateGraph(LayoutGraph({p}, Edges({p: set()}, {}), p), {}, {})

def gc_layout(g):
    ns, es, r = g
    queue = Queue()
    queue.put(r)
    ns2 = set()
    es2 = Edges(dict(), dict())
    
    while not queue.empty():
        p = queue.get()
        if p not in ns2:
            ns2.add(p)
            las = set(es.labels[p])
            es2.labels[p] = las
            for la in las:
                q = es.targets[(p, la)]
                es2.targets[(p, la)] = q
                queue.put(q)
    
    return LayoutGraph(ns2, es2, r)

def gc_state(sg):
    g, tm, vm = sg
    g2 = gc_layout(g)
    tm2 = {p: t for (p, t) in tm.items() if p in g2.nodes}
    vm2 = {p: v for (p, v) in vm.items() if p in g2.nodes}
    return StateGraph(g2, tm2, vm2)

def extract_pattern(sg, p):
    (ns, es, r), tm, vm = sg
    g2 = gc_layout(LayoutGraph(ns, es, p))
    tm2 = {u: ValueSet({vm[u]}) if u in vm else tm[u] for u in g2.nodes}
    return PatternGraph(g2, tm2)

def swing_layout(g, p, la, q):
    ns, es, r = g
    es.labels[p].add(la)
    es.targets[(p, la)] = q
    
def swing_state(sg, p, la, q):
    swing_layout(sg.layout, p, la, q)
    
def add_object_to_layout(g, cla):
    ns, es, r = g
    p = new_node()
    ns.add(p)
    las = set(cla.attrs)
    es.labels[p] = las
    qs = []
    for la in las:
        q = new_node()
        ns.add(q)
        es.labels[q] = set()
        es.targets[(p, la)] = q
        qs.append(q)

    return (p, qs)

def add_object_to_state(sg, cla):
    g, tm, vm = sg
    p, qs  = add_object_to_layout(g, cla)
    tm[p] = cla
    for q in qs:
        tm[q] = NULL_TYPE
        
    return p
    
def add_value_to_state(sg, v):
    p  = add_object_to_state(sg, v.cla)
    sg.values[p] = v
    return p
    
def push_state(sg, sla):
    (ns, es, r), tm, vm = sg
    r2 = new_node()
    ns.add(r2)
    es.labels[r2] = {sla}
    es.targets[(r2, sla)] = r
    return StateGraph(LayoutGraph(ns, es, r2), tm, vm)

def pop_state(sg, sla):
    (ns, es, r), tm, vm = sg
    if sla not in es.labels[r]:
        raise NoScope()
    
    return gc_state(StateGraph(LayoutGraph(ns, es, es.targets[(r, sla)]), tm, vm))
    
def find_lvar(sg, sla, la):
    (ns, es, r), tm, vm = sg
    while la not in es.labels[r] and sla in es.labels[r]:
        r = es.targets[(r, sla)]
        
    if la not in es.labels[r]:
        raise UndefVar()
    
    return (r, la)

def find_var(sg, sla, la):
    return sg.layout.edges.targets[find_lvar(sg, sla, la)]

def find_lattr(sg, p, la):
    (ns, es, r), tm, vm = sg
    if not p in ns:
        raise UndefVar()
    
    if la not in es.labels[p]:
        raise UndefAttr()
    
    return (p, la)

def find_attr(sg, p, la):
    return sg.layout.edges.targets[find_lattr(sg, p, la)]

def cons_match(g1, g2, le, tau1, tau2):
    ns1, es1, p1 = g1
    ns2, es2, p2 = g2
    f = bidict()
    
    def dfs_match(es1, p1, es2, p2):
        if p1 in f:
            if f[p1] != p2:
                raise Mismatch()
        else:
            if not le(tau2[p2], tau1[p1]):
                raise Mismatch()
            if p2 in f.inv:
                raise Mismatch()
            
            f[p1] = p2
            
            for la in es1.labels[p1]:
                q1 = es1.targets[(p1, la)]
                if la not in es2.labels[p2]:
                    raise Mismatch()
                q2 = es2.targets[(p2, la)]
                dfs_match(es1, q1, es2, q2)
    
    dfs_match(es1, p1, es2, p2)
    return f

def cons_union(gs):
    ess, ps = list(zip(*((es, p) for ns, es, p in gs)))
    fs = [bidict() for g in gs]
    
    def dfs_union(iz, ps):
        kz = [k for k in iz if ps[k] in fs[k]]
        cz = [c for c in iz if ps[c] not in fs[c]]
        uz = [fs[k][ps[k]] for k in kz]
        if len(uz) > 1:
            raise NoUnion()
        if cz:
            if uz:
                pd = uz[0]
                if any(pd in fs[c].inv for c in cz):
                    raise NoUnion()
            else:
                pd = new_node()
            for c in cz:
                fs[c][ps[c]] = pd
            laz = set_union(ess[i].labels[ps[i]] for i in iz)
            for la in laz:
                qs = [None]*len(gs)
                jz = [j for j in iz if la in ess[j].labels[ps[j]]]
                for j in jz:
                    qs[j] = ess[j].targets[(ps[j], la)]
                dfs_union(jz, qs)
                
    dfs_union(list(range(len(gs))), ps)
    return fs
    
def cons_inter(gs):
    ess, ps = unzip2((es, p) for ns, es, p in gs)
    fs = [bidict() for g in gs]
    
    def dfs_inter(ps):
        uz = [f[p] for f, p in zip(fs, ps) if p in f]
        if uz:
            pc = uz[0]
        else:
            pc = new_node()
        for f, p in zip(fs, ps):
            f[p] = pc
        if len(uz) != len(ps):
            laz = set_inter(es.labels[p] for es, p in zip(ess, ps))
            for la in laz:
                qs = [es.targets[(p, la)] for es, p in zip(ess, ps)]
                dfs_inter(qs)
    
    dfs_inter(ps)
    return fs

def cons_match_conj(pgs):
    gs, tms = unzip2(pgs)
    fs = cons_union(gs)
    tsd = {}
    nsd = set_union(f.inv for f in fs)
    for ud in nsd:
        ts = {tm[f.unique_inv(ud)] for tm, f in zip(tms, fs) if ud in f.inv}
        if not exists_ty_le_all(ts):
            raise NoConj()
        td = ty_inf(ts)
        tsd[ud] = td
        
    return (fs, tsd)

def cons_match_disj(pgs):
    gs, tms = unzip2(pgs)
    fs = cons_inter(gs)
    tsc = {}
    nsc = set_union(f.inv for f in fs)
    for uc in nsc:
        ts = set_union({tm[u] for u in f.inv[uc]} for tm, f in zip(tms, fs))
        tc = ty_sup(ts)
        tsc[uc] = tc
        
    return (fs, tsc)

def cons_pattern_graph(pattern):
    ns = set()
    es = Edges({}, {})
    tm = {}
    rm = bidict()
    
    def parse(pattern):
        if type(pattern) is LabeledPattern:
            la = pattern.label
            p = parse(pattern.base)
            if la in rm:
                r = rm[la]
                if r in ns:
                    raise RedefRef()
                'E[p/r]'
                nlas = [nla for nla, u in es.targets.items() if u == r]
                for nla in nlas:
                    es.targets[nla] = p
                'R[p/r]'
                las2 = [la2 for la2, u in rm.items() if u == r]
                for la2 in las2:
                    rm[la2] = p
                
            rm[la] = p
        elif type(pattern) is ClassPattern:
            cla, attrs = pattern
            p = new_node()
            ns.add(p)
            tm[p] = cla
            las, qs = unzip2([(la, parse(pattern2)) for la, pattern2 in attrs.items()])
            es.labels[p] = set(las)
            for la, q in zip(las, qs):
                es.targets[(p, la)] = q
        elif type(pattern) is PatternRef:
            la = pattern.label
            if la in rm:
                p = rm[la]
            else:
                p = new_node()
                rm[la] = p    
        elif type(pattern) is ValueSet:
            p = new_node()
            ns.add(p)
            es.labels[p] = set()
            tm[p] = pattern
        
        return p
                
    p = parse(pattern)
    if any(u not in ns for u in rm.inv):
        raise UndefRef()
    
    return (LayoutGraph(ns, es, p), tm, rm)


##
## end of graph.py
##$Id: graph.py 4838 2021-11-14 12:02:46Z wke@IPM.EDU.MO $
