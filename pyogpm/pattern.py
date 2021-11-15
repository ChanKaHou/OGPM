'''
    ----
    (c) 2021 Wei Ke & Ka-Hou Chan
    license:          GPL-3
    license-file:     LICENSE
    ----

    abstract syntax of this pattern matching

'''

from collections import namedtuple

LabeledPattern = namedtuple('LabeledPattern', ['label', 'base'])
PatternRef = namedtuple('PatternRef', ['label'])
ClassPattern = namedtuple('ClassPattern', ['cla', 'attrs'])
PatternConj = namedtuple('PatternConj', ['patterns'])
PatternDisj = namedtuple('PatternDisj', ['patterns'])
Case = namedtuple('Case', ['junc', 'stmt', 'extra'])
MatchStmt = namedtuple('MatchStmt', ['expr', 'cas'])

class Extra:
    def __init__(self, extra = None):
        self.extra = extra
    
    def put(self, extra):
        self.extra = extra
        
    def get(self):
        return self.extra


##
## end of pattern.py
##$Id: pattern.py 4838 2021-11-14 12:02:46Z wke@IPM.EDU.MO $
