
# Estratégia

## CSV 

### Primeira estratégia (Ficheiro CSV normais)

Primeiramente começamos por converter ficheiros CSV normais, sem nenhum dos requisitos adicionais

Para isso a nossa estratégia foi:

Com recurso ao lex, definimos como tokens:
- SEP (o separador ',')
- TEXT (tudo o que seja valor)
- NEWLINE (para a mudança de linha)

As expressões regulares usadas para estes tokens foram:

-  SEP 
    - `r','`
    - dá match apenas ao caratér ','

- TEXT
    - ` r'(?P<quote>[\"\']).+(?P=quote)|[^,\n]+'`
    - dá match a tudo o que esteja entre `"` ou `'`, ou tudo o que não seja `,` e `\n`

- NEWLINE
    - `r'\n+`
    - dá match ao caráter '\n', uma ou mais vezes, caso haja linhas vazias, para serem ignoradas


Já temos todos os tokens necessários para ler o csv.
Mas ainda precisamos de diferenciar os headers(1ªlinha), dos restantes valores.

Para isso, vamos usar um estado do lexer.

```py
    ("header","exclusive")
```

Este estado vai servir para diferenciar o tratamento do header com os restantes valores.


O lexer vai ter três variáveis nossas:
    - header - para guardar a informação do header
    - line - para guardar a informação da linha atual
    - values - para guardar a informação de todas as linhas

Vamos dizer ao lexer para começar no estado header.

Assim para a primeira linha, quando há uma match para o token de TEXT, iremos adicionar o valor do match para a lista de headers.

Quando chega ao fim da linha, ou seja, quando há match no token NEWLINE, já temos a nossa lista dos headres completa, iremos passar para o estado "INITIAL", o estado default para o resto das linhas.


Agora, para cada match do token TEXT, iremos adicionar para a lista "line".

E quando chegamos ao fim dessa linha, adicionamos a lista "line" à lista "values", e inicializamos a lista "line" para uma lista vazia., repetindo-se assim o processo para o resto das linhas.


Assim quando o lexer chega ao fim, temos duas listas:

- a lista "headers", que contém o nome de todos os headers

- a lista "values", que guarda uma lista dos valores para cada linha


Agora precisamos de construir o dicionário.

Para isso iremos percorrer a lista dos values, para tratar uma linha de cada vez.

Agora que temos a linha, iremos percorrer a linha juntamente com os headers, e associar o header ao seu valor.

Repete-se o processo para todas as linhas e temos o nosso dicionário completo.


### Adição da lista

Para a adição da lista, primeiramente tivemos a necessidade de criar mais um token.

O token MULT. Este Token tem como objetivo identificar o número de colunas que a lista vai abrangir.

A expressão regular utilizada para este token foi:

```py
r'{(?P<number>\d+)}'
```
Assim dá match quando um número se encontra dentro de {}. Usamos um *named group* para o digito, para posteriormente ir buscar esse resultado.

Este token é somente usado para o header.
E a utilização que ele vai ter será a seguinte:

- Quando houver um match, vemos qual o valor que está contido no grupo "number", vamos buscar o último elemento da lista de headers, pois sabemos que é esse elemento a que se está a referir. E vamos adicionar à lista de headers esse elemento N-1 vezes. Sendo N o nr obtido no grupo.

Com isto, precisamos de saber que na construção do dicionário, este tipo de elementos é para ser colocado numa lista.

Para isso, antes de colocar o elemento no dicionário, verificamos se o header que vamos adicionar é único na lista de headers.
Se for, procedemos normalmente.
Se não for, vamos verificar se já existe correspondência para esse header.
Se não existir, criamos uma lista e adicionamos o elemento.
Caso exista, adicionamos o elemento ao final da lista.

Assim conseguimos fazer a adição correta de elementos em lista

### Lista com intervalos

Para adicionar este requisito, a nossa antiga definação para o token de MULT não era suficiente, precisa de alterações.

Fizemos as devidas alterações para verificar o intervalo:

```py
r'{(?P<number>\d+)(,(?P<number2>\d+))?}'
```

Desta forma o grupo number captura o primeiro nr, e o grupo number2 captura o segundo.


Assim, guardamos o valor do grupo number como o nosso valor minimo, depois verificamos se existe o grupo *number2*, se existir guardamos como o nosso valor máximo, caso não exista, o nosso valor máximo será igual ao valor mínimo.

Anteriormente estávamos sempre à espera de um determinado nr de valores, agora esse valor pode variar. Para isso, precisamos de saber quantos existe valores em falta.

Para resolver este problema, criámos o token SKIP.

Este token tem como função identificar quando um valor se encontra vazio.

Como é óbvio não podemos identificar strings vazias. Mas sabemos que quando um valor falta, três coisas podem acontecer:
- pelo menos 2 vírgulas seguidas no meio da frase
- pelo menos 1 vírgula e um \n seguidos
- pelo menos 1 vírgula no ínicio da linha

Assim a expressão regular usada para este token verifica estes três casos:

```py
    r'(?m)((?P<init>^,+)|,{2,}\n*|,\n)'
```

Nota: 
é usado `(?m)` para `^` dar match no ínicio de cada linha e não apenas da string

Vai verificar se existe uma vírgula ou mais no inicio da lista, 2 ou mais vírgulas seguidas podendo este caso conter um nova linha ou o caso de uma vírgula seguida de uma nova linha

Antes de explicar o que vamos fazer quando houver um match, vamos só referir uma pequena alteração que fizemos relativamente aos headers.

Anteriormente, caso um header fosse uma lista íriamos repetir esse elemento na lista de headers e na criação do dicionário verificar se o elemento era único ou não na lista.

Decidimos melhorar esta abordagem, já a pensar também na adição da função.

Alterar a lista de headers, de uma lista com apenas nomes para uma lista de pares compostas por nome e um par com o nr de colunas.

Assim, ao adicionar um valor para a lista de headers adicionamos com o valor e (1,1), e caso dps se verificar que esse elemento irá ser uma lista, alteramos esse valor de acordo.

Para a construção do dicionário também se torna mais simples, pois apenas precisa de verificar se o segundo elemento do par é (1,1) ou não, caso não seja, vai percorrer a lista da linha e adicionar os respetivos valores, o nr de vezes que se encontra no par.

Caso o nr de elementos na lista seja menor que o valor minimo da lista, a lista não é adicionada ao dicionário.

Feitas estas alterações, expliquemos agora o que vamos fazer quando houver um match no token SKIP.

Primeiramente é importante referir que a definição deste token deve se encontrar por cima da definição do token SEP, pois caso esteja em baixo nunca vai haver um match, pois o SEP dá match apenas com ','. Assim ao meter a definição primeiro garantimos que verifica primeiro o padrão do SKIP e só se este falhar, é que dá match no SEP.

Quando há um match, começamos por verificar quantos valores estão em falta e para isso fazemos uso do seguinte cálculo:

```py
count = (match.count(',')) + ('\n' in match) -1
```

Este cálculo caso não seja no inicio da linha, caso seja, verificamos apenas o nr de virgulas.

Adicionamos None à lista da linha, conforme os nrs de valores em falta.

Na criação do dicionário, quando se trata de uma lista, iremos verificar se é None ou não, e caso seja não se adiciona à lista e não percorre mais a lista à espera de valor para esse header.

Assim conseguimos implementar a falta de números quando se trata de uma lista.

Tendo o cuidado de invocar a função que trata da newLine, caso um newLine se encontra no match.

### Funções de agregação

Para este requesito final tivemos a necessidade de criar mais um token, FUNC.

Este token tem como objetivo identificar a função a que vai corresponder o header.

Para tal usamos a seguinte expressão regular:

```py
    r'::(?P<func>\w+)'
```

dá match quando existe dois pointos seguidos de uma palvra, usamos um *named group*, para posteriormente capturar o valor contido no grupo.

Para implementar este requisito temos que mais uma vez alterar a nossa lista de headers.

Vai passar de uma lista de pares, que guarda nome e nr de colunas para uma lista de triplos, que guarda o mesmo que anteriormente com a adição da lista com as funções associadas.

Para tal, primeiramente quando adicionamos um valor à lista de headers, adicionamos com este campo da função a [].

Assim quando há um match do token FUNC, iremos alterar o terceiro elemento deste par, e adicionar o valor guardade no grupo capturado *func*.

Assim posteriormente na criação do dicionário, após ter todos os elementos de uma lista prontos a ser adicionados, verificamos se há alguma função associada a esse header.

Se o campo for [], adiciona-se a lista normalmente. Caso contrário, percorremos a lista, verificamos o nome da função e calculamos o valor resultante. 

Assim, em vez do nome do header, junta-se o nome do header juntamente com o nome da função separados por um underscore e associa-se ao valor resultante.

As funções que implementamos foram:
- sum
    - Somatório da lista
- media
    - Média da lista
- median
    - Mediana da lista
- mode
    - O valor mais frequente
- range
    - O intervalo de valores (máximo - mínimo)


# JSON

A construção do JSON é feita da seguinte forma:

Fazemos uso de uma indentação de 4 espaços. 

Essa identaçao será usada para cada linha quando fazemos uso da função spaces:

```py

indent = 4

def spaces(n):
    return " " *(indent *n)

```

Percorremos assim a lista de dicionários anteriormente criada.

E para cada dicionário, iremos percorrer os seus itens como pares (key,value) com recurso da função items.

Para cada par, iremos verificar qual o seu tipo para saber como temos de o escrever.

Há 3 tipos que podem ser reconhecidos:
- float/int
- list
- str

A lista de dicionário encontra-se entre [], para cada linha do CSV corresponde um dicionário que se encontra dentro de {} e estes são separados por vírgulas

Para os números,escrevemos o valor sem aspas.

Para a lista, escrevemos os valores entre [] e separados por virgulas

Para a str, escrevemos o valor com aspas.

Para todos, a key é sempre entre aspas seguida de ":".



