
import re
import ply.lex as lex

import statistics

funcs=[
    "sum",
    "media",
    "median",
    "mode",
    "range"
]

tokens = ["SKIP","SEP","TEXT","NEWLINE","MULT","FUNC"]


states = [
    ("header","exclusive")
]

def t_header_SKIP(t):
    r'(,{2,}\n*|,\n)'
    if '\n' in t.value:
        t_header_NEWLINE(t)



def t_SKIP(t):
    r'(?m)((?P<init>^,+)|,{2,}\n*|,\n)'
    match = t.value
    if t.lexer.lexmatch.group('init'):
        count = match.count(',')
    else:
        count = (match.count(',')) + ('\n' in match) -1
    for _ in range(count):
        t.lexer.line.append(None)
    if '\n' in match:
        t_NEWLINE(t)


def t_header_FUNC(t):
    r'::(?P<func>\w+)'
    func = (t.lexer.lexmatch.group('func'))
    last = t.lexer.header[-1]
    if func == "all":
        last[2].extend(funcs)
    else:
        last[2].append(func)


def t_ANY_SEP(t):
    r','


def t_header_MULT(t):
    r'{(?P<number>\d+)(,(?P<number2>\d+))?}'
    match = t.lexer.lexmatch
    valMin= int(match.group('number'))
    if match.group('number2') is not None:
        valMax= int(match.group('number2'))
    else:
        valMax = valMin
    elem = lexer.header[-1]
    lexer.header[-1]=(elem[0],(valMin,valMax),[])

def t_header_TEXT(t):
    r'(?P<quote>[\"\']).+(?P=quote)|[^{},\n\'\"]+'
    t.value = re.sub(r'["\']',"",t.value)
    t.lexer.header.append((t.value,(1,1),[]))

def t_TEXT(t):
    r'(?P<quote>[\"\']).+(?P=quote)|[^,\n]+'
    t.value=re.sub(r'["\']',"",t.value)
    if t.value.strip() == "":
        t.lexer.line.append(None)
    else:
        t.lexer.line.append(t.value)

def t_header_NEWLINE(t):
    r'\n'
    t.lexer.begin("INITIAL")

def t_NEWLINE(t):
    r'\n'
    t.lexer.values.append(t.lexer.line)
    t.lexer.line=[]


def t_ANY_error(t):
    pass

lexer = lex.lex()
lexer.header=[]
lexer.values=[]
lexer.line=[]

lexer.begin("header")

file = "testes/test"

f = open(file +".csv","r")

texto = f.read()

lexer.input(texto)


for tok in lexer:
    pass


def doFunc(func,list):
    list = [float(i) for i in list]
    if func == "sum":
        return sum(list)
    elif func == "media":
        return sum(list)/len(list)
    elif func == "median":
        return statistics.median(list)
    elif func== "mode":
        return statistics.mode(list)
    elif func == "range":
        return max(list)-min(list)  


listDict=[]
for listLine in lexer.values:
    dictLine = dict()
    indexLine=0
    for (header,hNum,other) in lexer.header:
        if (hNum == (1,1)):
            value = listLine[indexLine]
            dictLine[header]=listLine[indexLine]
            indexLine+=1
        else: 
            lista=[]
            for i in range(hNum[1]):
                value= listLine[indexLine + i]
                if value is not None:
                    lista.append(value)
                else:
                    break
            indexLine+=hNum[1]
            if other != []:
                for func in other:
                    if len(lista) >= hNum[0]:
                        dictLine[header+"_"+func]=doFunc(func,lista)
                    else:
                        dictLine[header+"_"+func]=None     
            else:
                if len(lista) >= hNum[0]:
                    dictLine[header]=lista
                else:
                    dictLine[header]=None
    listDict.append(dictLine)


indent = 4

def spaces(n):
    return " " *(indent *n)


def writeElem(key,value):
    finalStr = ""
    if value is None:
        finalStr+=f'"{key}": null'
    elif type(value) is str:
        try:
            value = float(value)
            if value.is_integer():
                value=int(value)
            finalStr+=f'"{key}": {value}'
        except ValueError:
            finalStr+=f'"{key}": "{value}"'
    elif type(value) is list:
        finalStr+=f'"{key}": ['
        finalStr+=",".join(map(str,value))
        finalStr+="]" 
    else:
        finalStr+=f'"{key}": {value}'    
    return finalStr


def writeDict(listDict):
    finalStr= "[\n"
    for indexDict,dict in enumerate(listDict):
        finalStr+=spaces(1)
        finalStr+="{\n"
        for index,(key,elem) in enumerate(dict.items()):
            finalStr+=spaces(2)
            finalStr+=writeElem(key,elem)
            if index != len(dict)-1:
                finalStr+=","
            finalStr+="\n"  
        finalStr+=spaces(1)
        finalStr+="}"
        if indexDict != len(listDict)-1:
            finalStr+=","
        finalStr+="\n"
    finalStr+="]\n"
    return finalStr

y = writeDict(listDict)

f.close()

f = open(file + ".json","w")

f.write(y)

f.close()


