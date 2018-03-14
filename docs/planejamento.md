# Planejamento Projeto MC911

## Grupo 2:

|                  Nome                 |   RA   |
|:-------------------------------------:|:------:|
|             Eric Krakauer             | 155253 |
| José Pedro Vieira do Nascimento Filho | 155981 |
|           Lucas Alves Racoci          | 156331 |
|   Luiz Fernando Rodrigues da Fonseca  | 156475 |
|          Rafael Gois Pimenta          | 157055 |

## Resumo

A ideia do projeto é implementar um programa que recebe como entrada um código em uma linguagem funcional que se aproxima de Haskell, converte para uma representação intermediária em formato de árvore baseada na notação lambda de funções anônimas, e mostra na tela o código em formato de árvore. O projeto será dividido em duas camadas: um cliente web em JavaScript que receberá a entrada e mostrará a imagem do código na tela, enquanto o servidor será feito em Python que fará analises léxica e sintática, e devolverá um JSON que o cliente web processará para mostrar as informações na tela. A comunicação entre as duas camadas será feita através de uma REST implementada com o auxílio do Flask.

## Descrição

O projeto será dividido em duas partes: um cliente web e um servidor, que se comunicam através de uma REST. O cliente web será desenvolvido em JavaScript com AngularJS. Nele, será possível enviar um arquivo em uma linguagem funcional que se aproxima de haskell, que será definida mais abaixo, ou o texto poderá ser escrito no próprio navegador. O texto será enviado através de um JSON para o servidor utilizando comunicação via REST.

O servidor será desenvolvido em Python, com o auxílio do Flask para gerenciar a REST. Ele receberá o JSON enviado pelo cliente web com o texto da linguagem funcional e utilizará um lexer e um parser para transformar o código funcional para uma representação em formato de árvore, baseada na notação lambda. Neste ponto, durante o projeto serão aplicadas otimizações na representação em árvore, como constant folding e constant propagation.

Por fim, a árvore será formatada para ser enviada para o cliente web através de um JSON. No cliente web, será mostrado o código em formato de árvore, com o auxílio da biblioteca D3.js para visualizar a imagem. Na imagem, será possível visualizar o código como um todo, expandir nós e ver os resultados da execução pela árvore. Existirão operações com listas, como map e fold, e duplas. Também será implementado visualmente as beta reductions da notação lambda, que é um processo de substituição de variáveis.

### Linguagem Funcional

A linguagem que será utilizada como entrada é baseada em Haskell, como no exemplo abaixo:

```
fib 0 = 0
fib 1 = 1
fib n = fib (n-1) + fib (n-2)
```

Como um todo, haverá definição de funções, if-else, definição e checagem de tipos, listas, operações map e fold em listas, duplas, pattern matching em funções, where, constantes.

Como ponto de entrada do programa, será obrigado a definição de uma função main, onde o código comecará a ser rodado.

Para simular entrada de dados fora do programa, ou seja, para existirem variáveis que não são consideradas constantes, será definido que os argumentos da função main serão variáveis, ou seja, não serão tratados como constantes.

### Notação Lambda

Também conhecida cálculo lambda, é um sistema formal e um modelo computacional turing completo usado na teoria da computabilidade, lógica e linguística. 
Serviu como inspiração para o paradigma de programação funcional, presentes em sua forma mais pura em linguagens como LISP e Haskell e como abstração em quase todas as linguagens mais conhecidas, tais como C/C++, Java, Javascript e Python.

#### Definição

Uma das formas mais intuitiva de definir este modelo é pensando-o como uma forma de definir funções anônimas que recebem como argumento uma função anônima e retornam uma função anônima.

Para isso normalmente é usada a notação E := λV.E | E E | V, onde V é uma variável e E é uma expressão. Note que há apenas dois operadores, o de abstração (λV.E) e o de aplicação (E E), nessa ordem de precedência. O primeiro introduz uma nova função e seu argumento. O segundo, infixo e normalmente representado pelo carácter ' ' de espaço indica que a expressão da direita é o argumento para a da esquerda.

#### Exemplos

Definição de True: T ≡ λx.λy.x

Definição de False: F ≡ λx.λy.y

Definição do número zero: 0 ≡ λf.λx.x

ISZERO ≡ λn.n (λx.F) T

### Otimizações

Da matéria de compiladores, serão feitas as otimizações:

- constant folding: processo de avaliar expressões constantes em tempo de compilação.
- constant propagation: processo de propagar uma constante para outras expressões.

Levando em consideração o cálculo lambda, será usada a redução beta como otimização, que é o processo de calcular o resultado da aplicação de uma função a uma expressão. Também será usada a redução eta, que é tirar uma abstração lambda mantendo o código equivalente.

## Objetivos

O objetivo do projeto é obter uma representação visual em formato de árvore de um código em uma linguagem funcional. Para atingir isso, a notação lambda será estudada juntamente com as possíveis otimizações.

## Resultados Esperados

### Visualização

Como visualização, no cliente web serão exibidas várias árvores. Uma conterá a visualização do código como foi digitado, sem otimizações e sem execução de funções. Outras árvores conterão as otimizações descritas. Por fim, haverá uma árvore onde será possível ver a execução do código. Também serão colocadas cores diferentes para os nós para cada tipo de dado.