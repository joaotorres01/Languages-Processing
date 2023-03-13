import ply.lex as lex

reserved = {
    'literals'   : 'LITERALS',
    'ignore'     : 'IGNORE',
    'tokens'     : 'TOKENS',
    'precedence' : 'PRECEDENCE',
    'LEX'        : 'LEX',
    'YACC'       : 'YACC',
}


literals = ['%','#','[',']','"',',','=',':','(',')','$','{','}']
tokens = ['str','int','float','allQuotes','allBraces','allNoConv','COMMENT'] + list(reserved.values())




def t_float(t):
    r"\d+\.\d+"
    t.value = float(t.value)
    return t


def t_int(t):
    r"\d+"
    t.value = int(t.value)
    return t

def t_str(t):
    r"\w+"
    t.type = reserved.get(t.value,'str')
    return t

def t_COMMENT(t):
    r'\#.*'
    return t
    
def t_allBraces(t):
    r"{.*}"
    #r"(?P<one>{.*})|(?m){(.|\n)*^}+?"
    return t

def t_allQuotes(t):
    r"\".*?\"|'.*?'"
    return t


def t_allNoConv(t):
    r"\$\$(.*\s*)+\Z"
    return t


t_ignore = " \n"

def t_error(t):
    print('Caráter ilegal: ', t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()