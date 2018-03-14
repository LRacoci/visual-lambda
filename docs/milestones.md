# Milestones Projeto MC911

## Grupo 2:
|                  Nome                 |   RA   |
|:-------------------------------------:|:------:|
|             Eric Krakauer             | 155253 |
| José Pedro Vieira do Nascimento Filho | 155981 |
|           Lucas Alves Racoci          | 156331 |
|   Luiz Fernando Rodrigues da Fonseca  | 156475 |
|          Rafael Gois Pimenta          | 157055 |

Assim como descrito no planejamento, o projeto é dividido em duas partes cliente web e servidor. O cliente web será desenvolvido em JavaScript com AngularJS e o servidor será desenvolvido em Python com Flask.

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

#### Parser

O Parser traduzirá os tokens passados pelo Lexer, e resultará na linguagem do cálculo lambda:

- Expressões Lambda
- Definição de Funções
- Estruturas Condicionais (if-else)
- Expressões Aritméticas
- Expressões Booleanas

#### Tradução para Estrutura de Árove

Por fim, o código em formato cálculo lambda será traduzido para a representação em árvore que será enviada para o cliente web para a visualização.

### Comunicação Entre Cliente Web e Servidor

Será feita a comunicação do cliente web com o servidor. O servidor rodará com o auxílio do Flask, enquanto as chamadas para a REST serão feitas com o AngularJS pelo cliente web.

### Cliente Web

O cliente web será capaz de gerar uma imagem dinâmica (interativa) de uma árvore com nós colapsáveis baseada na estrutura que lhe for passada pelo servidor.
Os nós que representam os operadores e as constantes mais comuns começarão colapsados, para facilitar a visualização, mas poderão ser abertos dependendo da interação com o usuário. 
Assim, de certa forma a mesma árvore representará a linguagem de alto nível e a notação lambda.
Também será feito um estilo em css para a página.

## Iteração 2

## Iteração 3
