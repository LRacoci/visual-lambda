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

A ideia do projeto é implementar um programa que recebe como entrada um código em uma linguagem funcional que se aproxima de Haskell, converte para uma representação intermediária em formato de árvore baseada na notação lambda de funções anônimas, e mostra na tela o código em formato de árvore. O projeto será dividido em duas camadas: um front-end em JavaScript que receberá a entrada e mostrará a imagem do código na tela, enquanto o back-end será feito em Python que fará analises léxica e sintática, e devolverá um JSON que o front-end processará para mostrar as informações na tela. A comunicação entre as duas camadas será feita através de uma REST implementada com o auxílio do Flask.

## Descrição

O projeto será dividido em duas partes: um front-end e um back-end, que se comunicam através de uma REST. O front-end será desenvolvido em JavaScript com AngularJS. Nele, será possível enviar um arquivo em uma linguagem funcional que se aproxima de haskell, que será definida mais abaixo, ou o texto poderá ser escrito no próprio navegador. O texto será enviado através de um JSON para o back-end utilizando comunicação via REST.

O back-end será desenvolvido em Python, com o auxílio do Flaks para gerenciar a REST. Ele receberá o JSON enviado pelo front-end com o texto da linguagem funcional e utilizará um lexer e um parser para transformar o código funcional para uma representação em formato de árvore, baseada na notação lambda. Neste ponto, durante o projeto serão aplicadas otimizações na representação em árvore, como constant folding, constant propagation, common subexpression elimination e dead code elimination.

Por fim, a árvore será formatada para ser enviada para o front-end através de um JSON. No front-end, será mostrado o código em formato de árvore, com o auxílio da biblioteca D3.js para visualizar a imagem. Na imagem, será possível visualizar o código como um todo, expandir nós e ver os resultados da execução pela árvore. Existirão operações com listas, como map e fold, e duplas. Também será implementado visualmente as beta reductions da notação lambda, que é um processo de substituição de variáveis.

### Linguagem Funcional

### Notação Lambda

Também conhecida cálculo lambda, é um sistema formal e um modelo computacional turing completo usado na teoria da computabilidade, lógica e linguística. 
Serviu como inspiração para o paradigma de programação funcional, presentes em sua forma mais pura em linguagens como LISP e Haskell e como abstração em quase todas as linguagens mais conhecidas, tais como C/C++, Java, Javascript e Python.

#### Definição

Uma das formas mais intuitiva de definir este modelo é pensando-o como uma forma de definir funções anônimas que recebem como argumento uma função anônima e retornam uma função anônima.

Para isso normalmente é usada a notação E := λV. E | (E E) | V, onde V é uma variável e E é uma expressão. Note que há apenas dois operadores, o de abstração e o de aplicação, nessa ordem de precedência. O primeiro introduz uma nova função e seu argumento. O segundo, infixo e normalmente representado pelo carácter ' ' de espaço indica que a expressão da direita é o argumento para a da esquerda.

No nosso projeto mudaremos um pouco a sintaxe para fascilitar a visualização, dessa forma, consideraremos E := E E | E λV. em que o operador ' ' terá associatividade a direita.
Assim, o combinador de ponto fixo Y, que pode ser expresso por λf.(λy. y y) (λx. f (x x)) em nossa sintaxe é expresso por y y λy. f x x λx. λf. , tornando todos os parenteses desnecessários.

### Visualização

### Otimizações


## Objetivos

## Resultados Esperados