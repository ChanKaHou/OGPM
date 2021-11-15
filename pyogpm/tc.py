'''
    ----
    (c) 2021 Wei Ke & Ka-Hou Chan
    license:          GPL-3
    license-file:     LICENSE
    ----

    type-checking rules

'''

from subtype import (
    Cla,
    Value,
    subtype,
    min_type,
    classof,
    BOOL_TYPE,
    VALUE_TYPES)

from op import (
    is_op,
    get_op)

from asx import (
    PrintStmt,
    AssignStmt, 
    IfStmt,
    WhileStmt,
    VarDecl,
    VarEnd,
    VarExpr,
    AttrExpr,
    OpExpr,
    NewExpr,
    AndExpr,
    OrExpr,
    Program)

from pattern import (
    PatternConj,
    PatternDisj,
    MatchStmt)

from graph import (
    PatternGraph,
    cons_pattern_graph,
    cons_match_conj,
    cons_match_disj,
    unzip4)

class Env:
    def __init__(self, outer = None, items = []):
        self.tab = dict(items)
        self.outer = outer

    def __contains__(self, k):
        return k in self.tab or (self.outer is not None and k in self.outer)

    def __getitem__(self, k):
        if k in self.tab:
            return self.tab[k]
        else:
            return self.outer[k]
        
    def __setitem__(self, k, v):
        self.tab[k] = v
        
    def top(self):
        return set(self.tab)
    
    def pop(self):
        return self.outer
    
    def show(self):
        print(self.tab)
        env = self.outer
        while env is not None:
            print(env.tab)
            env = env.outer
            
class TypeCheckingError(Exception): pass
class NodeTypeError(TypeCheckingError): pass
class NodeSubtypeError(TypeCheckingError): pass
class IncompatibleTypesError(TypeCheckingError): pass
class UndefVarError(TypeCheckingError): pass
class ParentObjectError(TypeCheckingError): pass
class AttrError(TypeCheckingError): pass
class OpError(TypeCheckingError): pass
class OpArgLenError(TypeCheckingError): pass
class OpArgTypeError(TypeCheckingError): pass
class VarEndError(TypeCheckingError): pass
class LeftExprError(TypeCheckingError): pass
class ClassError(TypeCheckingError): pass
class AssignTypeError(TypeCheckingError): pass
class CondTypeError(TypeCheckingError): pass
class ScopeError(TypeCheckingError): pass
class PrintArgTypeError(TypeCheckingError): pass
class BoolTypeError(TypeCheckingError): pass

def tc_node(p, env, es, types):
    if p in env:
        return env[p]
    
    if p not in types:
        raise NodeTypeError()
    
    t = types[p]
    env2 = Env(env, {p: t})
    
    for la in es.labels[p]:
        q = es.targets[(p, la)]
        s = tc_node(q, env2, es, types)
        if not subtype(s, classof(t, [la])):
            raise NodeSubtypeError()
    
    return t

def tc_graph(pg, env):
    (ns, es, p), types = pg
    t = tc_node(p, env, es, types)
    return t

def tc_ref(la, env, pg, refs):
    p = refs[la]
    (ns, es, p2), types = pg
    t = tc_node(p, env, es, types)
    return t

def tc_pattern(pattern, env):
    g, tm, rm = cons_pattern_graph(pattern)
    pg = PatternGraph(g, tm)
    t = tc_graph(pg, env)
    rtm = {la: tc_ref(la, env, pg, rm) for la in rm}
    return (t, rtm, pg, rm)

def tc_conj(patterns, env):
    ts, rtms, pgs, rms = unzip4([tc_pattern(pattern, env) for pattern in patterns])
    fs, tsd = cons_match_conj(pgs)
    rtm2 = {la: min_type(s, tsd[f[rm[la]]]) for f, rtm, rm in zip(fs, rtms, rms) for la, s in rtm.items()}
    th = tsd[fs[0][pgs[0].layout.root]]
    pts = [min_type(t, th) for t in ts]
    return (th, pts, rtm2, pgs, fs, rms)
                       
def tc_disj(patterns, env):
    ts, rtms, pgs, rms = unzip4([tc_pattern(pattern, env) for pattern in patterns])
    fs, tsc = cons_match_disj(pgs)
    rtm2 = {la: tsc[f[rm[la]]] for f, rtm, rm in zip(fs, rtms, rms) for la in rtm}
    th = tsc[fs[0][pgs[0].layout.root]]
    pts = [t for t in ts]
    return (th, pts, rtm2, pgs, fs, rms)

def tc_case(ca, env):
    junc, stmt, extra = ca
    
    if type(junc) is PatternConj:
        t, pts, rtm, pgs, fs, rms = tc_conj(junc.patterns, env)
        extra.put((pgs, fs, rms))
    elif type(junc) is PatternDisj:
        t, pts, rtm, pgs, fs, rms = tc_disj(junc.patterns, env)
        extra.put((pgs, fs, rms))
    else:    
        t, rtm, pg, rm = tc_pattern(junc, env)
        extra.put((pg, rm))

    env2 = Env(env, rtm)
        
    tc_stmt(stmt, env2)
    return t

def tc_value(v, env):
    return v.cla

def tc_var(x, env):
    la = x.label
    
    if la not in env:
        print(la)
        env.show()
        raise UndefVarError()
    
    return env[la]

def tc_attr(x, env):
    y, la = x 
    t = tc_expr(y, env)
    
    if type(t) is not Cla:
        raise ParentObjectError()
    
    if la not in t.attrs:
        print(la)
        raise AttrError()
    
    return t.attrs[la]

def tc_op(x, env):
    op, args = x
    if not is_op(op):
        raise OpError()
    
    d = get_op(op)
    if len(args) != len(d.par_types):
        raise OpArgLenError()
    
    for y, pty in zip(args, d.par_types):
        if tc_expr(y, env) != pty:
            raise OpArgTypeError()
        
    return d.res_type

def tc_new(x, env):
    if type(x.cla) is not Cla:
        raise ClassError()
    
    return x.cla

def tc_and_or(x, env):
    left, right = x
        
    if tc_expr(left, env) is not BOOL_TYPE or tc_expr(right, env) is not BOOL_TYPE:
        raise BoolTypeError()
    
    return BOOL_TYPE    

EXPR_TAB = {
    Value: tc_value,
    VarExpr: tc_var,
    AttrExpr: tc_attr,
    OpExpr: tc_op,
    NewExpr: tc_new,
    AndExpr: tc_and_or,
    OrExpr: tc_and_or}

def tc_expr(x, env):
    return EXPR_TAB[type(x)](x, env)
    
def tc_match(m, env):
    expr, cas = m
    t2 = tc_expr(expr, env)
    
    for ca in cas:
        t = tc_case(ca, env)
        if not (subtype(t2, t) or subtype(t, t2)):
            raise IncompatibleTypesError()
    
    return env

def tc_var_decl(vd, env):
    la, cla = vd
    return Env(env, {la: cla})

def tc_var_end(ve, env, env_base):
    if env is env_base:
        raise VarEndError()
    
    if set([ve.label]) != env.top():
        raise VarEndError()
    
    return env.pop()

def tc_print(pr, env):
    for x in pr.args:
        tc_expr(x, env)
        
    return env

def tc_assign(assign, env):
    lx, x = assign
    
    if type(lx) not in {VarExpr, AttrExpr}:
        raise LeftExprError()
    
    t = tc_expr(lx, env)
    t2 = tc_expr(x, env)
    
    if not subtype(t2, t):
        raise AssignTypeError()

    return env
    
def tc_if(ifs, env):
    x, thens, elses = ifs
    
    if tc_expr(x, env) is not BOOL_TYPE:
        raise CondTypeError()
    
    tc_stmt(thens, env)
    tc_stmt(elses, env)
    return env
    
def tc_while(ws, env):
    x, s = ws
    
    if tc_expr(x, env) is not BOOL_TYPE:
        raise CondTypeError()
    
    tc_stmt(s, env)
    return env
    
def tc_stmt(s, env):
    if type(s) is MatchStmt:
        return tc_match(s, env)
    
    if type(s) is AssignStmt:
        return tc_assign(s, env)
    
    if type(s) is IfStmt:
        return tc_if(s, env)
    
    if type(s) is WhileStmt:
        return tc_while(s, env)
    
    if type(s) is PrintStmt:
        return tc_print(s, env)
    
    return tc_block(s, env)

def tc_block(blk, env):
    env2 = env
    for s in blk.stmts:
        env2 = tc_scope(s, env2, env)
        
    if env2 is not env:
        raise ScopeError()
    
    return env
    
def tc_scope(s, env, env_base):
    if type(s) is VarDecl:
        return tc_var_decl(s, env)
    
    if type(s) is VarEnd:
        return tc_var_end(s, env, env_base)
    
    return tc_stmt(s, env)

def tc_program(prog, env):
    return tc_block(prog.block, env)


##
## end of tc.py
##$Id: tc.py 4841 2021-11-14 17:09:10Z wke@IPM.EDU.MO $
