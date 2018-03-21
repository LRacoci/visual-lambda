from lexer import *
    
class Parser(lp.Parser):

    LEXER = Lexer
    START = 'start'
    EXPRESSION = 'expression'

    PRECEDENCE = (
        (lp.RIGHT, 'UMINUS'),
        (lp.LEFT, 'TIMES', 'DIVIDE'),
        (lp.LEFT, 'PLUS', 'MINUS')
    )
    
    @lp.attach('start : MAIN DEFINITION expression')
    def main(self,  main, _, expr):
        return ['main', expr]
    
    @lp.attach('expression : INTEGER')
    def number(self, num):
        return [int(num)]
    
    @lp.attach('expression : LPAREN expression RPAREN')
    def brackets(self, lp, expr, rp):
        return expr

    @lp.attach('expression : expression PLUS expression')
    def addition(self, left, _, right):
        return [['+', left], right]

    @lp.attach('expression : expression MINUS expression')
    def subtract(self, left, _, right):
        return [['-', left], right]

    @lp.attach('expression : expression TIMES expression')
    def multiply(self, left, _, right):
        return [['*', left], right]

    @lp.attach('expression : expression DIVIDE expression')
    def division(self, left, _, right):
        return [['/', left], right]
    
    @lp.attach('expression : MINUS expression', prec_symbol='UMINUS')
    def negate(self, minus, expr):
        return ['-', expr]
