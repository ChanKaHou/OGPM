'''
    ----
    (c) 2021 Wei Ke & Ka-Hou Chan
    license:          GPL-3
    license-file:     LICENSE
    ----

    test cases

'''

from pp import pprint

from subtype import (
    Tag,
    Lazy,
    Cla,
    subtype,
    INT_TYPE,
    STR_TYPE,
    BOOL_TYPE,
    NO_TYPE,
    Value,
    ValueSet)

from pattern import (
    LabeledPattern,
    ClassPattern,
    PatternRef,
    PatternConj,
    PatternDisj,    
    MatchStmt,
    Case,
    Extra
)

from graph import (
    Label,
    cons_pattern_graph,
    layout_graph_to_pp,
    init_state_graph)

from asx import (
    VarDecl,
    VarEnd,
    PrintStmt,
    AssignStmt,
    BlockStmt,
    IfStmt,
    WhileStmt,
    VarExpr,
    AttrExpr,
    NewExpr,
    OpExpr,
    AndExpr,
    OrExpr,
    Program)

from tc import (
    tc_stmt,
    tc_program,
    Env)

from st import (
    st_stmt,
    st_program)


def test_subtype():
    print(
'''
----
---- subtype ----
----
''')
    
    Cla.reset()
    
    a1 = Label('a1')
    a2 = Label('a2')
    b1 = Label('b1')
    b2 = Label('b2')
    c1 = Label('c1')
    c2 = Label('c2')
    d1 = Label('d1')
    d2 = Label('d2')
    
    A = Cla(Tag('A'),
        [], 
        {  
            a1: INT_TYPE,
            a2: STR_TYPE
        })

    B = Cla(Tag('B'),
        [A], 
        {  
            b1: INT_TYPE,
            b2: STR_TYPE
        })
    
    C = Cla(Tag('C'),
        [A], 
        {  
            c1: INT_TYPE,
            c2: STR_TYPE
        })
    
    D = Cla(Tag('D'),
        [B, C], 
        {  
            d1: INT_TYPE,
            d2: STR_TYPE
        })

    pprint(D.to_pp())

    E = Cla.inter([B, C])
    pprint(E.to_pp())
    
    print(subtype(D, E))
    print(subtype(E, D))
    
    pprint(NO_TYPE.to_pp())
    print(subtype(A, NO_TYPE))
    
    ONE = Value(INT_TYPE, 1)
    TWO = Value(INT_TYPE, 2)
    THREE = Value(INT_TYPE, 3)
    TEN = Value(INT_TYPE, 10)
    HELLO = Value(STR_TYPE, 'Hello')
    
    VSET1 = ValueSet(set(Value(INT_TYPE, x) for x in range(10)))
    print(subtype(ValueSet(set([ONE, TWO])), VSET1))
    print(subtype(ValueSet(set([ONE, TWO, TEN])), VSET1))
    print(subtype(VSET1, INT_TYPE))
    
    F = Cla.union([B, C])
    pprint(F.to_pp())
    print(subtype(F, A))
    print(subtype(A, F))
    print(A == F)
    
    h1 = Label('h1')
    h2 = Label('h2')
    k = Label('k')

    H = Cla(Tag('H'),
        [],
        {
            h1: INT_TYPE,
            h2: A
        })
    
    K = Cla(Tag('K'),
        [],
        {
            k: H
        })
    
    o = Label('o')
    q = Label('q')
    x = Label('x')
    y = Label('y')

    pb = ClassPattern(
        K,
        {
            k : ClassPattern(
                H,
                {
                    h1: ClassPattern(INT_TYPE, {}),
                    h2: ClassPattern(B, {})
                })
        }) 
    
    pc = ClassPattern(
        K,
        {
            k : ClassPattern(
                H,
                {
                    h1: ClassPattern(INT_TYPE, {}),
                    h2: LabeledPattern(x, ClassPattern(C, {}))
                })
        })
    
    s1 = BlockStmt([
        VarDecl(o, K),
        VarDecl(q, D),
        AssignStmt(VarExpr(o), NewExpr(K)),
        AssignStmt(AttrExpr(VarExpr(o), k), NewExpr(H)),
        AssignStmt(AttrExpr(AttrExpr(VarExpr(o), k), h1), Value(INT_TYPE, 3)),
        AssignStmt(VarExpr(q), NewExpr(D)),
        AssignStmt(AttrExpr(VarExpr(q), a1), Value(INT_TYPE, 4)),
        AssignStmt(AttrExpr(VarExpr(q), b1), Value(INT_TYPE, 5)),
        AssignStmt(AttrExpr(VarExpr(q), c1), Value(INT_TYPE, 6)),
        AssignStmt(AttrExpr(AttrExpr(VarExpr(o), k), h2), VarExpr(q)),
        
        MatchStmt(VarExpr(o), [
            Case(PatternConj([pb, pc]), BlockStmt([
                VarDecl(y, E),
                AssignStmt(VarExpr(y), VarExpr(x)),
                PrintStmt([
                    AttrExpr(VarExpr(y), a1),
                    AttrExpr(VarExpr(y), b1),
                    AttrExpr(VarExpr(y), c1)
                    ]),
                VarEnd(y)
                ]), Extra())
            ]),

        MatchStmt(VarExpr(o), [
            Case(PatternDisj([pb, pc]), BlockStmt([
                VarDecl(y, F),
                AssignStmt(VarExpr(y), VarExpr(x)),
                PrintStmt([AttrExpr(VarExpr(y), a1)]),
                VarEnd(y)
                ]), Extra())
            ]),

        VarEnd(q),
        VarEnd(o)])
    
    env = tc_stmt(s1, Env())
    sg = st_stmt(s1, init_state_graph())
    

def test_fig2():
    print(
'''
----
---- figure 2 ----
----
''')

    Cla.reset()
    
    e = Label('e')
    l = Label('l')
    r = Label('r')
    
    w = Label('w')
    x = Label('x')
    y = Label('y')
    z = Label('z')
    
    T_lz = Lazy(Tag('T'))
    
    T = Cla(T_lz.tag,
        [], 
        {
            e: INT_TYPE,  
            l: T_lz,
            r: T_lz
        }).resolve_lazy()
    
    pprint(T.to_pp())
    
    pattern = ClassPattern(
        T,
        {
            e: ValueSet({Value(INT_TYPE, 0)}),
            l: LabeledPattern(w, ClassPattern(
                T,
                {
                    l: LabeledPattern(x, ClassPattern(T, {})),
                    r: LabeledPattern(y, ClassPattern(
                        T,
                        {
                            l: PatternRef(w),
                            r: PatternRef(z)
                        }))
                })),
            r: LabeledPattern(z, ClassPattern(T, {}))
        })
    
    g, tm, rm = cons_pattern_graph(pattern)
    pprint(layout_graph_to_pp(g))
    
    o = Label('o')
    
    s1 = BlockStmt([
        VarDecl(o, T),
        AssignStmt(VarExpr(o), NewExpr(T)),
        AssignStmt(AttrExpr(VarExpr(o), l), NewExpr(T)),
        AssignStmt(AttrExpr(VarExpr(o), r), NewExpr(T)),
        AssignStmt(AttrExpr(AttrExpr(VarExpr(o), l), l), NewExpr(T)),
        AssignStmt(AttrExpr(AttrExpr(VarExpr(o), l), r), NewExpr(T)),
        AssignStmt(AttrExpr(AttrExpr(AttrExpr(VarExpr(o), l), r), l), AttrExpr(VarExpr(o), l)),
        AssignStmt(AttrExpr(AttrExpr(AttrExpr(VarExpr(o), l), r), r), AttrExpr(VarExpr(o), r)),
        
        AssignStmt(AttrExpr(VarExpr(o), e), Value(INT_TYPE, 0)),
        AssignStmt(AttrExpr(AttrExpr(VarExpr(o), l), e), Value(INT_TYPE, 1)),
        AssignStmt(AttrExpr(AttrExpr(AttrExpr(VarExpr(o), l), l), e), Value(INT_TYPE, 2)),
        AssignStmt(AttrExpr(AttrExpr(AttrExpr(VarExpr(o), l), r), e), Value(INT_TYPE, 3)),
        AssignStmt(AttrExpr(AttrExpr(VarExpr(o), r), e), Value(INT_TYPE, 4)),
        
        MatchStmt(VarExpr(o), [
            Case(pattern, PrintStmt([
                AttrExpr(VarExpr(w), e), 
                AttrExpr(VarExpr(x), e), 
                AttrExpr(VarExpr(y), e), 
                AttrExpr(VarExpr(z), e)
                ]), Extra())
            ]),
        VarEnd(o)])
        
    env = tc_stmt(s1, Env())
    sg = st_stmt(s1, init_state_graph())

    
def test_fig3():
    print(
'''
----
---- figure 3 ----
----
''')

    Cla.reset()
    
    a = Label('a')
    b = Label('b')
    c = Label('c')
    d = Label('d')
    e = Label('e')
    x = Label('x')
    y = Label('y')
    
    X = Cla(Tag('X'),
        [], 
        {  
            b: INT_TYPE,
            c: STR_TYPE,
            d: STR_TYPE
        })

    pprint(X.to_pp())

    Y = Cla(Tag('Y'),
        [X], 
        {  
            a: INT_TYPE,
        })
    
    pprint(Y.to_pp())

    Z = Cla(Tag('Z'),
        [X], 
        {  
            e: BOOL_TYPE,
        })
    
    pprint(Z.to_pp())

    W = Cla(Tag('W'),
        [Y, Z],
        {})
    
    pprint(W.to_pp())
    
    p1 = ClassPattern(
        Y,
        {
            a: ValueSet(set(Value(INT_TYPE, x) for x in range(3))),
            c: LabeledPattern(x, ClassPattern(STR_TYPE, {})),
            d: ClassPattern(STR_TYPE, {})
        })
    
    p2 = ClassPattern(
        Z,
        {
            c: ClassPattern(STR_TYPE, {}),
            d: ClassPattern(STR_TYPE, {}),
            e: ValueSet({Value(BOOL_TYPE, False)})
        })
    
    p3 = ClassPattern(
        X,
        {
            b: ValueSet({Value(INT_TYPE, 1)}),
            c: ValueSet({Value(STR_TYPE, 'apple')}),
            d: ValueSet({Value(STR_TYPE, 'banana')})
        })
    
    p4 = ClassPattern(
        Z,
        {
            b: ValueSet({Value(INT_TYPE, 1)}),
            c: LabeledPattern(y, ValueSet({Value(STR_TYPE, 'apple')})),
            d: PatternRef(y)
        })
    
    conj = PatternConj([p1, p2, p3])
    disj = PatternDisj([p3, p4])
    
    o = Label('o')
    q = Label('q')
    u = Label('u')
    v = Label('v')
    
    prog = Program(BlockStmt([
        VarDecl(o, W),
        VarDecl(q, STR_TYPE),
        VarDecl(u, BOOL_TYPE),
        VarDecl(v, INT_TYPE),
        AssignStmt(VarExpr(o), NewExpr(W)),
        AssignStmt(AttrExpr(VarExpr(o), a), Value(INT_TYPE, 1)),
        AssignStmt(AttrExpr(VarExpr(o), b), AttrExpr(VarExpr(o), a)),
        AssignStmt(AttrExpr(VarExpr(o), c), Value(STR_TYPE, 'apple')),
        AssignStmt(AttrExpr(VarExpr(o), d), Value(STR_TYPE, 'banana')),
        AssignStmt(AttrExpr(VarExpr(o), e), Value(BOOL_TYPE, False)),

        MatchStmt(VarExpr(o), [
            Case(p4, PrintStmt([Value(STR_TYPE, 'p4, This should not match.')]), Extra())
            ]),
        PrintStmt([Value(STR_TYPE, 'after p4'), VarExpr(q)]),
        MatchStmt(VarExpr(o), [
            Case(p4, PrintStmt([Value(STR_TYPE, 'p4, This should not match.')]), Extra()),
            Case(disj, BlockStmt([
                AssignStmt(VarExpr(q), VarExpr(y)),
                PrintStmt([Value(STR_TYPE, 'disj'), VarExpr(q)])]), Extra())
            ]),
        MatchStmt(VarExpr(o), [
            Case(conj, BlockStmt([
                AssignStmt(VarExpr(q), VarExpr(x)),
                PrintStmt([Value(STR_TYPE, 'conj'), VarExpr(q)])]), Extra()),
            Case(p1, BlockStmt([
                AssignStmt(VarExpr(q), VarExpr(x)),
                PrintStmt([Value(STR_TYPE, 'p1'), VarExpr(q)])]), Extra())
            ]),
        MatchStmt(VarExpr(o), [
            Case(p4, PrintStmt([Value(STR_TYPE, 'p4, This should not match.')]), Extra()),
            Case(p1, BlockStmt([
                AssignStmt(VarExpr(q), VarExpr(x)),
                PrintStmt([Value(STR_TYPE, 'p1'), VarExpr(q)])]), Extra())
            ]),
        MatchStmt(VarExpr(o), [
            Case(p4, PrintStmt([Value(STR_TYPE, 'p4, This should not match.')]), Extra()),
            Case(p2, BlockStmt([
                AssignStmt(VarExpr(v), AttrExpr(VarExpr(o), b)),
                PrintStmt([Value(STR_TYPE, 'p2'), VarExpr(v)])]), Extra())
            ]),
        MatchStmt(VarExpr(o), [
            Case(p4, PrintStmt([Value(STR_TYPE, 'p4, This should not match.')]), Extra()),
            Case(p3, BlockStmt([
                AssignStmt(VarExpr(u), AttrExpr(VarExpr(o), e)),
                PrintStmt([Value(STR_TYPE, 'p3'), VarExpr(u)])]), Extra())
            ]),
        VarEnd(v),
        VarEnd(u),
        VarEnd(q),
        VarEnd(o)]))
    
    env = tc_program(prog, Env())
    sg = st_program(prog, init_state_graph())
    

def test_gcd():
    print(
'''
----
---- gcd ----
----
''')
    
    Cla.reset()
    
    m = Label('m')
    n = Label('n')
    t = Label('t')
    
    s1 = BlockStmt([
        VarDecl(m, INT_TYPE),
        VarDecl(n, INT_TYPE),
        AssignStmt(VarExpr(m), Value(INT_TYPE, 210)),
        AssignStmt(VarExpr(n), Value(INT_TYPE, 120)),
        PrintStmt([Value(STR_TYPE, 'numbers'), VarExpr(m), VarExpr(n)]),

        IfStmt(
            OrExpr(
                OpExpr(Label('igt'), [VarExpr(m), Value(INT_TYPE, 200)]), 
                OpExpr(Label('igt'), [VarExpr(n), Value(INT_TYPE, 200)])),
            PrintStmt([Value(STR_TYPE, 'one is > 200')]),
            PrintStmt([Value(STR_TYPE, 'none is > 200')])),
        
        IfStmt(
            AndExpr(
                OpExpr(Label('igt'), [VarExpr(m), Value(INT_TYPE, 200)]), 
                OpExpr(Label('igt'), [VarExpr(n), Value(INT_TYPE, 200)])),
            PrintStmt([Value(STR_TYPE, 'both are > 200')]),
            PrintStmt([Value(STR_TYPE, 'one is <= 200')])),
            
        BlockStmt([
            WhileStmt(
                OpExpr(Label('ine'), [VarExpr(n), Value(INT_TYPE, 0)]),
                BlockStmt([
                    VarDecl(t, INT_TYPE),
                    AssignStmt(VarExpr(t), VarExpr(m)),
                    AssignStmt(VarExpr(m), VarExpr(n)),
                    AssignStmt(VarExpr(n), OpExpr(Label('mod'), [VarExpr(t), VarExpr(n)])),
                    VarEnd(t)])),
            PrintStmt([Value(STR_TYPE, 'gcd'), VarExpr(m)])
        ]),
        
        VarEnd(n),
        VarEnd(m)
        ])
    
    env = tc_stmt(s1, Env())
    sg = st_stmt(s1, init_state_graph())
    

if __name__ == '__main__':
    test_subtype()
    test_fig2()
    test_fig3()
    test_gcd()


##
## end of test_cases.py
##$Id: test_cases.py 4841 2021-11-14 17:09:10Z wke@IPM.EDU.MO $
