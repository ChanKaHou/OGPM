'''
    ----
    (c) 2021 Wei Ke & Ka-Hou Chan
    license:          GPL-3
    license-file:     LICENSE
    ----

    prety-printing of dictionaries

'''

from collections import namedtuple

PrfxPP = namedtuple('PrefixedPP', ['prefix', 'pp'])

def pprint(s, name = None):
    def pp(s, indent):
        if isinstance(s, dict):
            if s:
                print('{')
                for k, v in s.items():
                    indent2 = indent+4
                    print('{}{!r}: '.format(' '*indent2, k), end = '')
                    pp(v, indent2)
                print(' '*indent+'}')
            else:
                print('{}')
        else:
            print('{!r}'.format(s))
    
    if type(s) is PrfxPP:
        p, t = s
        if p:
            if name:
                print('{} {}: '.format(p, name), end = '')
            else:
                print('{}: '.format(p), end = '')
        pp(t, 0)
    else:
        if name:
            print('{}: '.format(name), end = '')
        pp(s, 0)
    
def sorted_list(s):
    s2 = list(s)
    s2.sort()
    return s2


##
## end of pp.py
##$Id: pp.py 4838 2021-11-14 12:02:46Z wke@IPM.EDU.MO $
