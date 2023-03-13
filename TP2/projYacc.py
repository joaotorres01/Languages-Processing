from numpy import mat
import ply.yacc as yacc
from yaml import parse
from projLex import tokens, literals 
import re
from projUtils import *


def p_Program (p):
    "Program : Fases "

def p_Fases_list (p):
    "Fases : Fases Fase"

def p_Fases (p):
    "Fases : Fase"

def p_Fase (p):
    "Fase : '%' '%' FactorFase"

def p_Fase_end (p):
    "Fase : allNoConv"
    p.parser.noConv = p[1][2:]


def p_FactorFase_list (p):
    "FactorFase : FaseId Group"

def p_FaseId_lex(p):
    "FaseId : LEX"
    p.parser.current = p.parser.lex


def p_FaseId_yacc(p):
    "FaseId : YACC"
    p.parser.current = p.parser.yacc


def p_Group(p):
    "Group : Declarations Rules"


def p_Declarations_list(p):
    "Declarations : Declarations Declaration"

def p_Declarations_Empty(p):
    "Declarations :  "

def p_Declaration(p):
    "Declaration : '%' PlyDeclaration"

def p_Declaration_Comment(p):
    "Declaration : COMMENT"
    p.parser.current[1].append(p[1])


def p_Declaration_Var(p):
    "Declaration : str '=' Var"
    p.parser.current[1].append(f"{p[1]} = {p[3]}")

def p_Declaration_Var_error(p):
    "Declaration : error '=' Var"
    print("Info : variable name has to be string")


def p_PlyDeclaration_literals(p):
    "PlyDeclaration : LITERALS '=' LiteralsFactor"
    p.parser.current[0][p[1]] = p[3] 
    p[0] = p[3]

def p_PlyDeclaration_literals_error(p):
    "PlyDeclaration : LITERALS '=' error"
    print("Info : literals value must be a string or array")


def p_LiteralsFactor_Array(p):
    "LiteralsFactor : Array"
    p[0] = p[1]

def p_LiteralsFactor_String(p):
    "LiteralsFactor : allQuotes"
    p[0] = p[1]

def p_PlyDeclaration_ignore(p):
    "PlyDeclaration : IGNORE '=' allQuotes"
    p.parser.current[0][p[1]] = p[3] 
    p[0] = p[3]

def p_PlyDeclaration_ignore_error(p):
    "PlyDeclaration : IGNORE '=' error"
    print("Info : ignore value must be a string")


def p_PlyDeclaration_tokens(p):
    "PlyDeclaration : TOKENS '=' Array"
    p.parser.current[0][p[1]] = p[3] 
    p[0] = p[3]

def p_PlyDeclaration_tokens_error(p):
    "PlyDeclaration : TOKENS '=' error"
    print("Info : tokens value must be an array")


def p_PlyDeclaration_precedence(p):
    "PlyDeclaration : PRECEDENCE '=' PrecedenceFactor"
    p.parser.current[0][p[1]] = p[3] 
    p[0] = p[3]


def p_PlyDeclaration_precedence_error(p):
    "PlyDeclaration : PRECEDENCE '=' error"
    print("Info : precedence value must be a tuple or an array")

def p_PlyDeclaration_error(p):
    "PlyDeclaration : error '=' Var"
    print(f"Info : There's no ply variable with name:'{p[1].value}'")


def p_PrecedenceFactor_Array(p):
    "PrecedenceFactor : Array"
    p[0] = p[1]

def p_PrecedenceFactor_Tuple(p):
    "PrecedenceFactor : Tuple"
    p[0] = p[1]



def p_Var_Array(p):
    "Var : Array"
    p[0] = arrayToString(p[1])

def p_Var_Dict(p):
    "Var : Dict"
    if p[1] == "":
        p[0] = "{}"
    else:
        strRes = ""
        for elem in p[1]:
            lista = elem.split(':')
            key = lista[0]
            value = lista[1]
            strRes += f"\t{key} : {value},\n"
        p[0] = "{\n" + strRes + "}\n"


def p_Var_String(p):
    "Var : allQuotes ElemFactor"
    p[0] = p[1] + p[2]


def p_Var_int(p):
    "Var : int"
    p[0] = p[1]

def p_Var_float(p):
    "Var : float"
    p[0] = p[1]


def p_Var_Tuple(p):
    "Var : Tuple"
    p[0] = p[1]

def p_Tuple(p):
    "Tuple : '(' Lista ')'"
    strRes = '(' +  elemsToString(p[2]) + ')'
    p[0] = strRes

def p_Array(p):
    "Array : '[' Lista ']'"
    p[0] = p[2]

def p_Dict(p):
    "Dict : '{' Lista '}'"
    p[0] = p[2]

def p_Dict_Empty(p):
    "Dict : allBraces"
    elem = re.sub("{(.*)}","\1",p[1])
    if "," in elem:
        lista = elem.split(',') 
        p[0] = lista
    else:        
        p[0] = ""

def p_Lista_empty(p):
    "Lista :"
    p[0] = ""

def p_Lista(p):
    "Lista : Elems Final"
    p[0] = p[1]

def p_Final(p):
    "Final : ','"

def p_Final_empty(p):
    "Final : "

def p_Elems_list (p):
    "Elems : Elems ',' Var"
    p[0] = p[1] + [p[3]] 

def p_Elems_single(p):
    "Elems : Var"
    p[0] = [p[1]]

def p_ElemFactor_dict(p):
    "ElemFactor : ':' Var"
    p[0] = f":{p[2]}"

def p_ElemFactor_empty(p):
    "ElemFactor : "
    p[0] = ""

def p_Rules_list(p):
    "Rules : Rules Rule"

def p_Rules_empty(p):
    "Rules : Rule"


def p_Comment(p):
    "Comment : COMMENT"
    p[0] = p[1]

def p_Comment_empty(p):
    "Comment : "
    p[0] = ""

def p_Rule(p):
    "Rule : str ':' allQuotes allBraces Comment"
    if p[1] not in p.parser.current[0]:
         p.parser.current[0][p[1]] = []
    p.parser.current[0][p[1]] += [{"rule": p[3], "code":p[4], "comment" : p[5]}]

def p_Rule_errorName(p):
    "Rule : error ':' allQuotes allBraces"
    if p[1].type != "COMMENT":
        print(f"Info : Rule name '{p[1].value}' is invalid. Has to be string.")

def p_Rule_errorRule(p):
    "Rule : str ':' error allBraces"
    print(f"Info : Rule '{p[3].value}' is invalid. The rule has to be inside quotes(\").")

def p_Rule_errorCode(p):
    "Rule : str ':' allQuotes error"
    print(f"Info : The code '{p[4].value}' for function '{p[1]}' is invalid. The code has to be inside braces " + "{}.")



def p_error(p):
    if p is not None:
        if p.type == "COMMENT":
            print("Comment ignored (out of section): ", p.value)
        else :
            parser.sucess = False
            print ("Syntax Error -> illegal token (value : %s | type :%s)" % (p.value,p.type))
    else:
        print('Unexpected end of input')


def checkCast(statements,name):
    strRes =""
    types=["float","int"] # possible types to cast 
    # split into each statement
    lista = splitStatements(statements)
    for elem in lista:
        lRes = re.findall("(\w.+?)\((.+?)\)",elem) # check if is function
        if lRes:
            for res in lRes:
                #case for cast
                if res[0] in types: strRes += f"\t{res[1]} = {res[0]}({res[1]})\n"
                else: strRes += f"\t{elem}\n"
        else:
            # case for reserved
            if (elem == "#reserved") : strRes +=f"\t{lexVar}.type = reserved.get({lexVar}.value,'{name}')\n"   
            else: strRes += f"\t{elem}\n"
    return strRes


def lexFunction(name,function):
    strRes = ""
    elem= function[0]
    strRes += elem['comment'] + "\n"
    strRes += f"def t_{name}({lexVar}):\n"
    rule = elem['rule']
    rule = re.sub("\\''",'\"',rule)
    if name != "error": strRes += f"\tr{rule}\n"
    code = elem['code']
    code = code[1:-1] # remove braces
    if code != "":
        code = checkCast(code,name)
        strRes+= f"{code}"
    if name != "error": strRes += f"\treturn {lexVar}\n\n"
    return strRes


def findVarLex(rules):
    lista = ["value","type","lineno","lexpos","lexer"]
    elem = ".".join(map(str,rules))
    l = re.findall("(\w)\.(\w+)",elem)
    l = [x[0] for x in l if x[1] in lista]
    global lexVar
    if l:
        lexVar = max(set(l), key=l.count)

def buildLex(dict,arrayVar):
    str = ""
    str += "import ply.lex as lex\n\n" 
    listTokens = dict['tokens']
    listTokens = [elem.replace("'","") for elem in listTokens] # remove single quotes from each token
    findVarLex(dict.values())
    str += buildVar(arrayVar)
    lista = ["ignore","literals","tokens"]
    for key,elem in dict.items():
        if key not in lista:
            if key not in listTokens and key != "error":
                raiseError("Lex",f"'{key}' not in Tokens")
            str += lexFunction(key,elem)
            if key in listTokens:
                listTokens.remove(key)
        else:
            if key == "ignore":
                key = "t_ignore"
            if type(elem) is list:
                elem = arrayToString(elem)
            str += f"{key} = {elem}"
            if key == "tokens" and any ([x.startswith("reserved ") for x in arrayVar]):
                str += "+ list(reserved.values())"
            str += "\n\n"
    if listTokens:
        raiseError("Lex",f"these tokens {arrayToString(listTokens)} are not defined")
    str += "lex.lex()\n"
    return str

    
def buildCodeStatements(statements):
    strRes =""
    # split into each statement
    lista = splitStatements(statements)
    for elem in lista:
        strRes += f"\t{elem}\n"
    return strRes


# find which variable is used for yacc rules
def findVarYacc(lista):
    elem = ".".join(map(str,lista))
    l = re.findall("(\w)\[\d\]",elem)
    global grammarVar
    if l:
        grammarVar = max(set(l), key=l.count)

def checkComment(comment):
    match = re.search("N=(\w+)",comment)
    if match is not None:
        comment = re.sub(match[0],"",comment)
        res = re.match("#(.+)",comment)
        res = res[1].strip()
        return (match[1],res)
    return(None,comment)


def buildGrammarRules(name,ruleList):
    strRes = ""
    count = 0
    for dict in ruleList:
        (cName,comment) = checkComment(dict['comment'])
        if cName:
            strRes += '# ' + comment + "\n"
            strRes += f"def p_{name}_{cName}({grammarVar}):\n"
        else:
            strRes += comment + "\n"
            strRes += f"def p_{name}_{count}({grammarVar}):\n"
            count += 1
        rule = dict['rule']
        rule = rule[1:-1] # remove quotes
        strRes += f"\t\"{name} : {rule}\"\n"
        code = dict['code']
        code = code[1:-1].strip() # remove braces and spaces in beg
        code = buildCodeStatements(code)
        strRes += f"{code}\n"
    return strRes


def buildYacc(grammar, dictVar):
    strRes = buildVar(dictVar)
    findVarYacc(grammar.values())
    for key,elem in grammar.items():
        if key == "precedence":
            if type(elem) is list:
                elem = arrayToString(elem)
            strRes += f"{key} = {elem}\n\n"
        else:
            strRes += buildGrammarRules(key,elem)
    return strRes


def doImportYacc():
    resStr = ""
    l = None
    if  parser.noConv != "":
        l = re.search("(.*=)?(\w+)\.yacc\(\)",parser.noConv)
    if l is not None:
        resStr += f"import ply.yacc as {l[2]}\n"
    else:
        resStr += "from ply.yacc import *\n"
    return resStr


def errorExit(error):
    print("Error :" + error)
    print(" Run '-h' or 'help' for more info.")
    exit()

def checkArguments():
    fase = "Arguments"
    lenArgs = len(sys.argv)
    if lenArgs != 2:
        option = sys.argv[1]
        filename = sys.argv[2]
        if lenArgs == 3 and (option == '-t' or option == 'template'):
            if option == '-t' or option == 'template':
                template(filename)
                exit()
            else:
                raiseError(fase,"These arguments are not valid.")
        else:
            raiseError(fase,"These arguments are not valid.")
    filename = sys.argv[1]
    #help
    if filename == '-h' or filename == 'help':
        help()
        exit()
    #template 
    if filename == '-t' or filename == 'template':
        template()
        exit()
    # file exists 
    if not os.path.exists(filename):
        raiseError(fase,f"There's no file with name:'{filename}'.")
    return filename



# Build the parser
parser = yacc.yacc()
parser.yacc=({},[])
parser.lex=({},[])
parser.current = ()
parser.noConv = ""
parser.sucess = True


import sys, os

try:
    filename = checkArguments()
except Exception as error:
    print(error)
    exit()


f = open(filename)
program = f.read()
parser.parse(program)

grammarVar = "p"
lexVar = "t"


if parser.sucess:
    # Build Lex
    importLex = False
    if parser.lex != ({},[]):
        filenameLex = filename.split('.')[0] + "_lex.py"
        try:
            lexStr = buildLex(parser.lex[0],parser.lex[1])
        except Exception as error:
            print(error)
            exit()
        writeToFile(filenameLex,lexStr)
        importLex = True

    if parser.yacc != ({},[]):
        # Build Yacc
        yaccStr = ""
        yaccStr += doImportYacc()
        if importLex:
            importNameLex = filenameLex.split('.')[0]
            yaccStr += f"from {importNameLex} import tokens, literals\n\n"
        yaccStr += buildYacc(parser.yacc[0],parser.yacc[1])
        yaccStr += parser.noConv

        #Write Files
        filenameYacc = filename.split('.')[0] + "_yacc.py"
        writeToFile(filenameYacc,yaccStr)
else:
    print("Execution aborted. For help, run programm with help or -h.")

