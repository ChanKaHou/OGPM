'''
    ----
    (c) 2021 Wei Ke & Ka-Hou Chan
    license:          GPL-3
    license-file:     LICENSE
    ----

    abstract syntax of this minimal oo language, except pattern matching

'''

from collections import namedtuple

PrintStmt = namedtuple('PrintStmt', ['args'])
AssignStmt = namedtuple('AssignStmt', ['lexpr', 'expr'])
IfStmt = namedtuple('IfStmt', ['expr', 'then_stmt', 'else_stmt'])
WhileStmt = namedtuple('WhileStmt', ['expr', 'stmt'])
BlockStmt = namedtuple('BlockStmt', ['stmts'])

VarDecl = namedtuple('VarDecl', ['label', 'cla'])
VarEnd = namedtuple('VarEnd', ['label'])

VarExpr = namedtuple('VarExpr', ['label'])
AttrExpr = namedtuple('AttrExpr', ['expr', 'label'])
OpExpr = namedtuple('OpExpr', ['op', 'args'])
NewExpr = namedtuple('NewExpr', ['cla'])
AndExpr = namedtuple('AndExpr', ['left', 'right'])
OrExpr = namedtuple('OrExpr', ['left', 'right'])

Program = namedtuple('Program', ['block'])


##
## end of asx.py
##$Id: asx.py 4842 2021-11-14 17:09:57Z wke@IPM.EDU.MO $
