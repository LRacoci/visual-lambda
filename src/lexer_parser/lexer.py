import purplex as lp

class Lexer(lp.Lexer):

    MAIN = lp.TokenDef(r'main')
    DEFINITION = lp.TokenDef(r'=')

    #SINGLE_SPACE = lp.TokenDef(r' ')

    LAMBDA = lp.TokenDef(r'\\')
    NAME = lp.TokenDef(r'[a-zA-Z_]')


    LPAREN = lp.TokenDef(r'\(')
    RPAREN = lp.TokenDef(r'\)')
    
    NEWLINE = lp.TokenDef(r'\n')

    INTEGER = lp.TokenDef(r'\d+')

    TIMES = lp.TokenDef(r'\*')
    DIVIDE = lp.TokenDef(r'/')
    PLUS = lp.TokenDef(r'\+')
    MINUS = lp.TokenDef(r'-')

    BOOLEAN = lp.TokenDef(r'(True)|(False)')

    AND = lp.TokenDef(r'and')
    NOT = lp.TokenDef(r'not')
    OR  = lp.TokenDef(r'or')

    WHITESPACE = lp.TokenDef(r'[ \t\n]+', ignore=True)
    #_NEW_LINE_ = lp.TokenDef(r'\n', ignore=True)
