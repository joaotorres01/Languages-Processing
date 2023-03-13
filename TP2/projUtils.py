
import re 
def raiseError(fase,string):
    raise Exception(f"{fase} Error: " + string)

def elemsToString(elem):
    return ",".join(map(str,elem))

def arrayToString(elem):
    return "[" + elemsToString(elem) + "]"


def writeToFile(filename,string):
    file = open(filename,"w")
    file.write(string)
    print(f"{filename} was successfully generated")


def splitStatements (statements):
    lista = statements.split(',')
    if len(lista) == 1 : return lista
    for index,elem in enumerate(lista):
        if (elem.count('(') != elem.count(')')) or (elem.count('"')%2 != 0) or (elem.count('{') != elem.count('}')):
            lista[index+1] = lista[index] + ',' + lista[index +1]
            lista[index] = None
    return [i for i in lista if i]

def buildVar(array):
    strRes = ""
    for value in array:
        strRes += f"{value}\n"
    return strRes

def help():
    helpStr = """    PLY-SIMPLE TRANSLATOR

    Transform a ply-simple file into two ply files, one for Lex, other for Yacc.

    It contains two phases: LEX and YACC.
    To start a phase: "%%LEX" or "%%YACC"
    When you start a phase, the other ends.
    After these two phases, there is a No Conversion phase, that you can have code that will not be converted.
    These phase begins with "$$" and all the code after will stay the same.

    Each phase is composed of two parts: Declarations and Rules.

    The order matter, meaning all of the declarations has to be done before the rules.

    Parte I - Declarations:
    If it's a ply-variable, then it needs to have "%" before the variable name.
    Ply-variables available:
        - LEX : tokens, literals, ignore
        - YACC : precedence
    
    If you want to declare variables, delcare them as you normally do.
    For comments, they will appear only at the start of a line.
    If you have a comment in the same line as a declaration, that comment will appear in the next line.

    Parte II - Rules:
    Must be declared as follows:
    name : "rule" {code} #comment
    where:
        - name : name of the rule
            - it must be a string
        - rule : regular expression for LEX or production for YACC
            - has to be inside quotes, if you wants to use quotes inside a regex, use: \\'' 
        - code : the code that you want for the rule
            - has to be inside braces, you can use braces inside 
            - it must be in one line
            - comma is used as a line separator
            - you can have more complex code with proper identation with tabs, but it's recommended to use more complicated functions at No Conversion phase
        - comment (optional) : comment to better describe the rule
            - has to have a # before the comment
            - it will appear on top of the function in the generated file
            - this comment can be in the next line too, but will still be a reference to the rule above
    
    Special cases:
    - If you want to use reserved words for Lex phase, declare a dictionary with the name "reserved", then put "#reserved" in the function that will deal with them
    - To cast a value use type(value), this will transform in value = type(value)
    - For Yacc Rules, you can define a name for the function. For that in the Comment part, use "N=name", with your preffered name for the function 

    Options: 
    -t or template [filename]:
        - prints a template of ply-simple in terminal if no argument or in a file with the filename given
    """
    print(helpStr)

def template(filename=None):
    strRes = """%%LEX

%literals = "" 
%ignore = ""
%tokens = []

#Regular Expressions
RULE : "regex" {code} # comment

%% YACC

%precedence = []


# Grammar
RULE : "production" {code}

$$

# No Conversion Phase

def p_error(t):
print(f"Syntax error at '{t.value}', [{t.lexer.lineno}]")


y=yacc()
y.parse("3+4*7")
    """
    if filename is not None: writeToFile(filename,strRes)
    else : print(strRes)