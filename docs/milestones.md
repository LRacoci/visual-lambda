# Milestones Projeto MC911

## Grupo 2:
|                  Nome                 |   RA   |
|:-------------------------------------:|:------:|
|             Eric Krakauer             | 155253 |
| José Pedro Vieira do Nascimento Filho | 155981 |
|           Lucas Alves Racoci          | 156331 |
|   Luiz Fernando Rodrigues da Fonseca  | 156475 |
|          Rafael Gois Pimenta          | 157055 |

Assim como descrito no planejamento, o projeto é dividido em duas partes cliente web e servidor. O cliente web será desenvolvido em JavaScript com AngularJS e D3JS, e o servidor será desenvolvido em Python com Flask.

## Iteração 1

Na primeira iteração a linguagem e a visualização ainda serão simples, como descrito a seguir.

### Servidor

O servidor será capaz de parsear uma linguagem funcional simples, contendo:

- Constantes
- Números Naturais
- Booleanos
- Operadores Lógicos
- Operadores Aritméticos

#### Lexer

O Lexer será capaz de identificar tokens de:

- Nome de Variáveis
- Números Naturais
- Booleanos como "True" e "False"
- Operadores Aritméticos (+,-,*,/,^)
- Operadores Lógicos (and, or, not)

Responsáveis: Eric Krakauer e Rafael Gois.

#### Parser

O Parser traduzirá os tokens passados pelo Lexer, e resultará na linguagem do cálculo lambda:

- Expressões Lambda
- Definição de Funções
- Estruturas Condicionais (if-else)
- Expressões Aritméticas
- Expressões Booleanas
- Tratamento especial para a função main

Responsáveis: José Pedro e Luiz Fernando.

#### Tradução para Estrutura de Árvore

Por fim, o código em formato cálculo lambda será traduzido para a representação em árvore que será enviada para o cliente web para a visualização.

Responsáveis: Eric Krakauer e Lucas Racoci.

### Comunicação Entre Cliente Web e Servidor

Será feita a comunicação do cliente web com o servidor. O servidor rodará com o auxílio do Flask, enquanto as chamadas para a REST serão feitas com o AngularJS pelo cliente web.

Responsáveis: Luiz Fernando.

### Cliente Web

O cliente web será capaz de gerar uma imagem dinâmica (interativa) de uma árvore com nós colapsáveis baseada na estrutura que lhe for passada pelo servidor.
Os nós que representam os operadores e as constantes mais comuns começarão colapsados, para facilitar a visualização, mas poderão ser abertos dependendo da interação com o usuário.
Assim, de certa forma a mesma árvore representará a linguagem de alto nível e a notação lambda.
Também será feito um estilo em css para a página.

Responsáveis: Lucas Racoci e Rafael Gois.

### Docker

Configurar o projeto e o código para rodar com o docker.

Responsáveis: Luiz Fernando.

## Iteração 2

Essa e as próximas iterações serão responsáveis por extender a linguagem original para representar estruturas e conceitos mais complexos.

### Servidor

#### Análise Sintática

O Lexer e o Parser serão adaptados para reconhecer a definição de tipos abstratos, e também para reconhecer estruturas de definição de variáveis depois das expressões (where).

##### Lexer

O Lexer será capaz de identificar tokens para:

- Definição de tipos de dados
- Palavra especial **where**
- Tipos de dados: inteiro, ponto flutuante, string

Responsáveis: José Pedro e Luiz Fernando.

##### Parser

O Parser será capaz de traduzir:

- Estrutura com definições **where**
- Tipos de dados

Responsáveis: Eric Krakauer e Rafael Gois.

#### Análise Semântica

O Backend agora será capaz de checar o tipo das variáveis e apontar operações inválidas.

Responsáveis: José Pedro e Lucas Racoci.

### Cliente Web

O cliente web implementará visualmente a redução beta e a redução eta para execução do código.

Responsáveis: Eric Krakauer e Rafael Gois.

### Otimizações

Será feito redução beta e redução eta como otimização de código.

Responsáveis: Lucas Racoci e Luiz Fernando.

## Iteração 3

### Servidor

#### Análise Sintática

Será implementada uma sintaxe especial para declaração de listas.
Também implementado o *pattern matching* (casamento de padrões), muito utilizado na linguagem Haskell.
Serão feitos os casamentos de padrões envolvendo a definição de funções, e declaração de seus argumentos.

##### Lexer

O Lexer será capaz de identificar tokens para:

- Listas
- Tokens especiais de pattern matching

Responsáveis: Eric Krakauer e Lucas Racoci.

##### Parser

O Parser será capaz de traduzir:

- Definições de listas
- Pattern matching

Responsáveis: José Pedro e Rafael Gois.

### Cliente Web

Implementar visualmente as otimizações constant folding e constant propagation.
Adaptar também a visualização para tratar listas, assim como adaptar a visualização para uma execução dinâmica do código.

Responsáveis: José Pedro e Luiz Fernando.

### Otimizações

Será feito constant folding e constant propagation no processo de compilação.

Responsáveis: Eric Krakauer e Rafael Gois.
