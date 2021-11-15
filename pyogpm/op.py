'''
    ----
    (c) 2021 Wei Ke & Ka-Hou Chan
    license:          GPL-3
    license-file:     LICENSE
    ----

    operations on values

'''

from collections import namedtuple

import operator

from subtype import (
    Value,
    INT_TYPE,
    STR_TYPE,
    BOOL_TYPE)

from graph import (
    Label,
    add_value_to_state)

OpDef = namedtuple('OpDef', ['op', 'par_types', 'res_type', 'f'])

OP_TAB = {}

def is_op(la):
    return la in OP_TAB

def get_op(la):
    return OP_TAB[la]

def invoke_op(sg, op, args):
    f = OP_TAB[op].f
    return f(sg, *args)

def op_binary(sg, x, y, t, f):
    g, tm, vm = sg
    return add_value_to_state(sg, Value(t, f(vm[x].value, vm[y].value)))

def op_unary(sg, x, t, f):
    g, ts, vs = sg
    return add_value_to_state(sg, t, Value(t, f(vs[x].value)))

def op_add(sg, x, y):
    return op_binary(sg, x, y, INT_TYPE, operator.add)
    
def op_sub(sg, x, y):
    return op_binary(sg, x, y, INT_TYPE, operator.sub)

def op_mul(sg, x, y):
    return op_binary(sg, x, y, INT_TYPE, operator.mul)

def op_div(sg, x, y):
    return op_binary(sg, x, y, INT_TYPE, operator.floordiv)

def op_mod(sg, x, y):
    return op_binary(sg, x, y, INT_TYPE, operator.mod)

def op_neg(sg, x):
    return op_unary(sg, x, INT_TYPE, operator.neg)

def op_not(sg, x):
    return op_unary(sg, x, BOOL_TYPE, operator.not_)

def op_cat(sg, x, y):
    return op_binary(sg, x, y, STR_TYPE, operator.concat)

def op_lower(sg, x):
    return op_unary(sg, x, STR_TYPE, lambda x: x.lower())

def op_upper(sg, x):
    return op_unary(sg, x, STR_TYPE, lambda x: x.lower())

def op_ieq(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.eq)

def op_ine(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.ne)

def op_ilt(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.lt)

def op_ile(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.le)

def op_igt(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.gt)

def op_ige(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.ge)

def op_seq(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.eq)

def op_sne(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.ne)

def op_slt(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.lt)

def op_sle(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.le)

def op_sgt(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.gt)

def op_sge(sg, x, y):
    return op_binary(sg, x, y, BOOL_TYPE, operator.ge)

OP_TAB = {
    Label('add'): OpDef(Label('add'), [INT_TYPE, INT_TYPE], INT_TYPE, op_add),
    Label('sub'): OpDef(Label('sub'), [INT_TYPE, INT_TYPE], INT_TYPE, op_sub),
    Label('mul'): OpDef(Label('mul'), [INT_TYPE, INT_TYPE], INT_TYPE, op_mul),
    Label('div'): OpDef(Label('div'), [INT_TYPE, INT_TYPE], INT_TYPE, op_div),
    Label('mod'): OpDef(Label('mod'), [INT_TYPE, INT_TYPE], INT_TYPE, op_mod),
    Label('neg'): OpDef(Label('neg'), [INT_TYPE], INT_TYPE, op_neg),
    Label('not'): OpDef(Label('not'), [BOOL_TYPE], BOOL_TYPE, op_not),
    Label('cat'): OpDef(Label('cat'), [STR_TYPE, STR_TYPE], STR_TYPE, op_cat),
    Label('lower'): OpDef(Label('lower'), [STR_TYPE], STR_TYPE, op_lower),
    Label('upper'): OpDef(Label('upper'), [STR_TYPE], STR_TYPE, op_upper),
    Label('ieq'): OpDef(Label('ieq'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_ieq),
    Label('ine'): OpDef(Label('ine'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_ine),
    Label('ilt'): OpDef(Label('ilt'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_ilt),
    Label('ile'): OpDef(Label('ile'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_ile),
    Label('igt'): OpDef(Label('igt'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_igt),
    Label('ige'): OpDef(Label('ige'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_ige),
    Label('seq'): OpDef(Label('seq'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_seq),
    Label('sne'): OpDef(Label('sne'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_sne),
    Label('slt'): OpDef(Label('slt'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_slt),
    Label('sle'): OpDef(Label('sle'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_sle),
    Label('sgt'): OpDef(Label('sgt'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_sgt),
    Label('sge'): OpDef(Label('sge'), [INT_TYPE, INT_TYPE], BOOL_TYPE, op_sge)}


##
## end of op.py
##$Id: op.py 4838 2021-11-14 12:02:46Z wke@IPM.EDU.MO $
