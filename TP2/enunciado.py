import ply.lex as lex
import ply.yacc as yacc

#LEX

literals = "+-/*=()" ## a single char
t_ignore = " \t\n"
tokens = [ 'VAR','NUMBER']


def t_VAR(t):
    "[a-zA-Z_][a-zA-Z0-9_]*"
    return t

def t_NUMBER (t):
    "\d+(\.\d+)?"
    t.value = float(t.value)
    return t

def t_error(t):
    "."
    print(f"Illegal character '{t.value[0]}', [{t.lexer.lineno}]")
    t.lexer.skip(1)

lexer = lex.lex()

# YACC

precedence = [
    ('left','+','-'),
    ('left','*','/'),
    ('right','UMINUS'),
]

ts = {}

def p_stat_VAR(p):
    "stat : VAR '=' exp"
    ts[p[1]] = p[3]

def p_stat_exp(p):
    "stat : exp"
    print(p[1])



def p_exp_plus(p):
    "exp : exp '+' exp"
    p[0] = p[1] + p[3]


def p_exp_sub(p):
    "exp : exp '-' exp"
    p[0] = p[1] - p[3]


def p_exp_mult(p):
    "exp : exp '*' exp"
    p[0] = p[1] * p[3]

def p_exp_div(p):
    "exp : exp '/' exp"
    p[0] = p[1] / p[3]

def p_exp_UMINUS(p):
    "exp : '-' exp %prec UMINUS"
    p[0] = -p[2]

def p_exp_parentesis(p):
    "exp : '(' exp ')'"
    p[0] = p[2]

def p_exp_NUMBER(p):
    "exp : NUMBER"
    p[0] = p[1]

def p_exp_VAR(p):
    "exp : VAR"
    p[0] = getval(p[1])

def p_error(t):
    print(f"Syntax error at ’{t.value}’, [{t.lexer.lineno}]")

def getval(n):
    if n not in ts: print(f"Undefined name ’{n}’")
    return ts.get(n,0)

y=yacc.yacc()
y.parse("3+4*7")
y.parse("a=3+4*7")

print(ts)