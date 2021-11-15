'''
    ----
    (c) 2021 Wei Ke & Ka-Hou Chan
    license:          GPL-3
    license-file:     LICENSE
    ----

    state transition rules

'''

from bidict import dict_union, bidict_union

from subtype import (
    Value,
    NULL_TYPE,
    VALUE_TYPES,
    subtype)

from graph import (
    Mismatch,
    Label,
    gc_state,
    push_state,
    pop_state,
    add_object_to_state,
    add_value_to_state,
    swing_state,
    find_var,
    find_lvar,
    find_attr,
    find_lattr,
    extract_pattern,
    cons_match)

from pattern import (
    PatternConj,
    PatternDisj,
    MatchStmt)

from asx import (
    AssignStmt,
    IfStmt,
    WhileStmt,
    PrintStmt,
    BlockStmt,
    VarDecl,
    VarEnd,
    VarExpr,
    AttrExpr,
    OpExpr,
    NewExpr,
    AndExpr,
    OrExpr)

from op import (
    invoke_op)

SCOPE_LABEL = Label('$')

def eval_value(x, sg):
    return add_value_to_state(sg, x)

def eval_var(x, sg):
    return find_var(sg, SCOPE_LABEL, x.label)

def eval_lvar(x, sg):
    return find_lvar(sg, SCOPE_LABEL, x.label)

def eval_attr(x, sg):
    p = eval_expr(x.expr, sg)
    return find_attr(sg, p, x.label)

def eval_lattr(x, sg):
    p = eval_expr(x.expr, sg)
    return find_lattr(sg, p, x.label)

def eval_op(x, sg):
    la, args = x
    return invoke_op(sg, la, [eval_expr(arg, sg) for arg in args])

def eval_new(x, sg):
    return add_object_to_state(sg, x.cla)

def eval_and(x, sg):
    left, right = x
    p = eval_expr(left, sg)

    g, tm, vm = sg
    if vm[p].value != True:
        return p
    
    return eval_expr(right, sg)

def eval_or(x, sg):
    left, right = x
    p = eval_expr(left, sg)

    g, tm, vm = sg
    if vm[p].value != False:
        return p

    return eval_expr(right, sg)

EXPR_TAB = {
    Value: eval_value,
    VarExpr: eval_var,
    AttrExpr: eval_attr,
    OpExpr: eval_op,
    NewExpr: eval_new,
    AndExpr: eval_and,
    OrExpr: eval_or}

def eval_expr(x, sg):
    return EXPR_TAB[type(x)](x, sg)

LEXPR_TAB = {
    VarExpr: eval_lvar,
    AttrExpr: eval_lattr}

def eval_lexpr(lx, sg):
    return LEXPR_TAB[type(lx)](lx, sg)
    
def st_var_decl(vd, sg):
    la, cla = vd
    sg = push_state(sg, SCOPE_LABEL)
    q = add_object_to_state(sg, NULL_TYPE)
    swing_state(sg, sg.layout.root, la, q)
    return gc_state(sg)

def st_var_end(ve, sg):
    la = ve.label
    return pop_state(sg, SCOPE_LABEL)

def st_print(pr, sg):
    def to_str(p):
        cla = sg.types[p]
        
        if cla is NULL_TYPE:
            return 'null'
        
        if cla in VALUE_TYPES:
            return str(sg.values[p].value)
        
        return '{}@({})'.format(cla.tag, p.id)
    
    rs = [to_str(eval_expr(x, sg)) for x in pr.args]
    print(', '.join(rs))
    return sg

def st_assign(s, sg):
    lx, x = s
    (p, la) = eval_lexpr(lx, sg)
    q = eval_expr(x, sg)
    swing_state(sg, p, la, q)
    return gc_state(sg)

def st_if(s, sg):
    x, thens, elses = s
    p = eval_expr(x, sg)
    if sg.values[p].value == True:
        return st_stmt(thens, sg)
    else:
        return st_stmt(elses, sg)

def st_while(s, sg):
    x, ws = s
    p = eval_expr(x, sg)
    while sg.values[p].value == True:
        sg = st_stmt(ws, sg)
        p = eval_expr(x, sg)
    
    return gc_state(sg)

def st_block(blk, sg):
    for s in blk.stmts:
        sg = st_scope(s, sg)
        
    return gc_state(sg)

def st_scope(s, sg):
    if type(s) is VarDecl:
        return st_var_decl(s, sg)
    
    if type(s) is VarEnd:
        return st_var_end(s, sg)
    
    return st_stmt(s, sg)
    
def st_match(s, sg):
    x, cas = s
    p = eval_expr(x, sg)
    pg = extract_pattern(sg, p)
    
    for junc, s, extra in cas:
        m = match_junc(pg, junc, extra.get())
        if m is not None:
            sg = push_state(sg, SCOPE_LABEL)
            for la, q in m:
                swing_state(sg, sg.layout.root, la, q)
            sg = st_stmt(s, sg)
            return pop_state(sg, SCOPE_LABEL)
        
    return sg

def match_junc(pg, junc, extra):
    if type(junc) is PatternConj:
        pgs1, fs1, rms1 = extra
        return match_conj(pg, pgs1, rms1)
    
    if type(junc) is PatternDisj:
        pgs1, fs1, rms1 = extra
        return match_disj(pg, pgs1, fs1, rms1)
    
    pg1, rm1 = extra
    return match_one(pg, pg1, rm1)

def match_patterns(pg1, pg2):
    g1, ts1 = pg1
    g2, ts2 = pg2
    
    try:
        f = cons_match(g2, g1, subtype, ts2, ts1)
        return f
    except Mismatch:
        return None

def match_one(pg, pg1, rm1):
    f = match_patterns(pg, pg1)
    
    if f is None:
        return None
    
    return [(la, f[q]) for la, q in rm1.items()]

def match_disj(pg, pgs1, fs1, rms1):
    for pg1 in pgs1:
        f = match_patterns(pg, pg1)
        if f is not None:
            rm1 = dict_union(rms1)
            f1 = bidict_union(fs1)
            return [(la, f[(set(f1.inv[f1[u]]) & set(f)).pop()]) for la, u in rm1.items()]
        
    return None

def match_conj(pg, pgs1, rms1):
    fs = [match_patterns(pg, pg1) for pg1 in pgs1]
    if any(f is None for f in fs):
        return None
    
    rm1 = dict_union(rms1)
    f = bidict_union(fs)
    return [(la, f[u]) for la, u in rm1.items()]

STMT_TAB = {
    MatchStmt: st_match,
    AssignStmt: st_assign,
    IfStmt: st_if,
    WhileStmt: st_while,
    PrintStmt: st_print,
    BlockStmt: st_block}

def st_stmt(s, sg):
    return STMT_TAB[type(s)](s, sg)

def st_program(prog, sg):
    return st_block(prog.block, sg)


##
## end of st.py
##$Id: st.py 4841 2021-11-14 17:09:10Z wke@IPM.EDU.MO $
