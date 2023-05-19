import json
import anytree
from anytree import Node, RenderTree

from phase1.scanner import Scanner
from phase1.utils.characterchecker import keywords_set


class Parser:
    scanner = None
    data = None
    line_no = 0
    lookahead = None
    token = None
    char = None
    error_messages = dict()
    symbols = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<', '/', '*', '=', '=='}
    parse_tree = None

    def __init__(self, scanner_location, predictset_location):
        self.scanner = Scanner(scanner_location)
        with open(predictset_location) as f:
            self.data = json.load(f)

    def parse(self):
        while True:
            self.lookahead = self.scanner.get_next_token()
            if self.lookahead == '$':
                print(self.error_messages)
                # print(RenderTree(parse_tree))
                break
            if self.lookahead is not None:
                # self.lookahead = str(self.lookahead)
                self.set_token(self.lookahead)
                self.set_char(self.lookahead)
                self.set_line_no(self.lookahead)
                # self.parse_tree = Node('Program')
                self.program()

    def get_next(self):
        self.lookahead = self.scanner.get_next_token()
        while self.lookahead is None:
            self.lookahead = self.scanner.get_next_token()
        # self.lookahead = str(self.lookahead)
        self.set_token(self.lookahead)
        self.set_char(self.lookahead)
        self.set_line_no(self.lookahead)

    def set_char(self, lk):
        # lk = lk[3:]
        # lk = lk.split(', ')
        # lk = lk[1]
        # lk = lk[:-2]
        # self.char = lk[1:]
        # print(self.char)
        self.char = lk[0][1]

    def set_line_no(self, lk):
        # lk = lk[3:]
        # lk = lk[:-1]
        # lk = lk.split(', ')
        # self.line_no = int(lk[2])
        self.line_no = lk[1]

    def set_token(self, lk):
        # lk = lk[3:]
        # lk = lk.split(', ')
        # lk = lk[0]
        # lk = lk[:-1]
        # self.token = lk
        self.token = lk[0][0]

    def match(self, terminal):
        # if self.char == terminal:
        #     self.get_next()
        # build tree
        # else:
        #     self.add_error_message(self.missing_error_message())
        if self.is_keyword(self.char) or self.is_symbol(self.char):
            if self.char == terminal:

                print(terminal)
                # build tree
            else:
                self.add_error_message('missing ' + terminal)
        else:
            if self.token == terminal:
                print(terminal)
                # build tree
            else:
                self.add_error_message('missing ' + terminal)
        self.get_next()

    def is_keyword(self, v):
        return v in keywords_set

    def is_symbol(self, v):
        return v in self.symbols

    def check_char_in_first(self, non_terminal):
        if self.is_keyword(self.char) or self.is_symbol(self.char):
            return self.char in self.data['first'][non_terminal]
        return self.token in self.data['first'][non_terminal]

    def check_epsilon_in_first(self, non_terminal):
        return 'EPSILON' in self.data['first'][non_terminal]

    def check_char_in_follow(self, non_terminal):
        if self.is_keyword(self.char) or self.is_symbol(self.char):
            return self.char in self.data['follow'][non_terminal]
        return self.token in self.data['follow'][non_terminal]

    def add_error_message(self, error_message):
        if self.line_no not in self.error_messages:
            self.error_messages[self.line_no] = []
        self.error_messages[self.line_no].append(error_message)

    def illegal_error_message(self):
        if self.is_keyword(self.char) or self.is_symbol(self.char):
            return 'illegal ' + self.char
        else:
            return 'illegal ' + self.token

    def missing_error_message(self):
        if self.is_keyword(self.char) or self.is_symbol(self.char):
            return 'missing ' + self.char
        else:
            return 'missing ' + self.token

    def non_terminal_panic_mode(self, non_terminal):
        if self.check_char_in_follow(non_terminal):
            if self.check_epsilon_in_first(non_terminal):
                pass  # EPSILON
            else:
                self.add_error_message(self.missing_error_message())
            return False  # No recursion
        else:
            self.add_error_message(self.illegal_error_message())
            self.get_next()
            return True  # Recursion

    def program(self):
        if self.check_char_in_first('Declaration-list'):
            # self.parse_tree = Node('Declaration-list')
            self.declaration_list()
        else:
            if self.non_terminal_panic_mode('Program'):
                self.program()

    def declaration_list(self):
        if self.check_char_in_first('Declaration'):
            self.declaration()
            self.declaration_list()
        else:
            if self.non_terminal_panic_mode('Declaration-list'):
                self.declaration_list()

    def declaration(self):
        if self.check_char_in_first('Declaration-initial'):
            self.declaration_initial()
            self.declaration_prime()
        else:
            if self.non_terminal_panic_mode('Declaration'):
                self.declaration()

    def declaration_initial(self):
        if self.check_char_in_first('Type-specifier'):
            self.type_specifier()
            self.match('ID')
        else:
            if self.non_terminal_panic_mode('Declaration-initial'):
                self.declaration_initial()

    def declaration_prime(self):
        if self.check_char_in_first('Fun-declaration-prime'):
            self.fun_declaration_prime()
        elif self.check_char_in_first('Var-declaration-prime'):
            self.var_declaration_prime()
        else:
            if self.non_terminal_panic_mode('Declaration-prime'):
                self.declaration_prime()

    def var_declaration_prime(self):
        if self.char == ';':
            self.match(';')
        elif self.char == '[':
            self.match('[')
            self.match('NUM')
            self.match(']')
            self.match(';')
        else:
            if self.non_terminal_panic_mode('Var-declaration-prime'):
                self.var_declaration_prime()

    def fun_declaration_prime(self):
        if self.char == '(':
            self.match('(')
            self.params()
            self.match(')')
            self.compound_stmt()
        else:
            if self.non_terminal_panic_mode('Fun-declaration-prime'):
                self.fun_declaration_prime()

    def type_specifier(self):
        if self.char == 'int':
            self.match('int')
        elif self.char == 'void':
            self.match('void')
        else:
            if self.non_terminal_panic_mode('Type-specifier'):
                self.type_specifier()

    def params(self):
        if self.char == 'int':
            self.match('int')
            self.match('ID')
            self.param_prime()
            self.param_list()
        elif self.char == 'void':
            self.match('void')
        else:
            if self.non_terminal_panic_mode('Params'):
                self.params()

    def param_list(self):
        if self.char == ',':
            self.match(',')
            self.param()
            self.param_list()
        else:
            if self.non_terminal_panic_mode('Param-list'):
                self.param_list()

    def param(self):
        if self.check_char_in_first('Declaration-initial'):
            self.declaration_initial()
            self.param_prime()
        else:
            if self.non_terminal_panic_mode('Param'):
                self.param()

    def param_prime(self):
        if self.char == '[':
            self.match('[')
            self.match(']')
        else:
            if self.non_terminal_panic_mode('Param-prime'):
                self.param_prime()

    def compound_stmt(self):
        if self.char == '{':
            self.match('{')
            self.declaration_list()
            self.statement_list()
            self.match('}')
        else:
            if self.non_terminal_panic_mode('Compound-stmt'):
                self.compound_stmt()

    def statement_list(self):
        if self.check_char_in_first('Statement'):
            self.statement()
            self.statement_list()
        else:
            if self.non_terminal_panic_mode('Statement-list'):
                self.statement_list()

    def statement(self):
        if self.check_char_in_first('Expression-stmt'):
            self.expression_stmt()
        elif self.check_char_in_first('Compound-stmt'):
            self.compound_stmt()
        elif self.check_char_in_first('Selection-stmt'):
            self.selection_stmt()
        elif self.check_char_in_first('Iteration-stmt'):
            self.iteration_stmt()
        elif self.check_char_in_first('Return-stmt'):
            self.return_stmt()
        else:
            if self.non_terminal_panic_mode('Statement'):
                self.statement()

    def expression_stmt(self):
        if self.check_char_in_first('Expression'):
            self.expression()
            self.match(';')
        elif self.char == 'break':
            self.match('break')
            self.match(';')
        elif self.char == ';':
            self.match(';')
        else:
            if self.non_terminal_panic_mode('Expression-stmt'):
                self.expression_stmt()

    def selection_stmt(self):
        if self.char == 'if':
            self.match('if')
            self.match('(')
            self.expression()
            self.match(')')
            self.statement()
            self.match('else')
            self.statement()
        else:
            if self.non_terminal_panic_mode('Selection-stmt'):
                self.selection_stmt()

    def iteration_stmt(self):
        if self.char == 'repeat':
            self.match('repeat')
            self.statement()
            self.match('until')
            self.match('(')
            self.expression()
            self.match(')')
        else:
            if self.non_terminal_panic_mode('Iteration-stmt'):
                self.iteration_stmt()

    def return_stmt(self):
        if self.char == 'return':
            self.match('return')
            self.return_stmt_prime()
        else:
            if self.non_terminal_panic_mode('Return-stmt'):
                self.return_stmt()

    def return_stmt_prime(self):
        if self.char == ';':
            self.match(';')
        elif self.check_char_in_first('Expression'):
            self.expression()
            self.match(';')
        else:
            if self.non_terminal_panic_mode('Return-stmt-prime'):
                self.return_stmt_prime()

    def expression(self):
        if self.check_char_in_first('Simple-expression-zegond'):
            self.simple_expression_zegond()
        elif self.token == 'ID': # token no char
            self.match('ID')
            self.b()
        else:
            if self.non_terminal_panic_mode('Expression'):
                self.expression()

    def b(self):
        if self.char == '=':
            self.match('=')
            self.expression()
        elif self.char == '[':
            self.match('[')
            self.expression()
            self.match(']')
            self.h()
        elif self.check_char_in_first('Simple-expression-prime'):
            self.simple_expression_prime()
        else:
            if self.non_terminal_panic_mode('B'):
                self.b()

    def h(self):
        if self.check_char_in_first('Expression'):
            self.expression()
        elif self.check_char_in_first('g'):
            self.g()
            self.d()
            self.c()
        else:
            if self.non_terminal_panic_mode('H'):
                self.h()

    def simple_expression_zegond(self):
        if self.check_char_in_first('Additive-expression-zegond'):
            self.additive_expression_zegond()
            self.c()
        else:
            if self.non_terminal_panic_mode('Simple-expression-zegond'):
                self.simple_expression_zegond()

    def simple_expression_prime(self):
        if self.check_char_in_first('Additive-expression-prime'):
            self.additive_expression_prime()
            self.c()
        else:
            if self.non_terminal_panic_mode('Simple-expression-prime'):
                self.simple_expression_prime()

    def c(self):
        if self.check_char_in_first('Relop'):
            self.relop()
            self.additive_expression()
        else:
            if self.non_terminal_panic_mode('c'):
                self.c()

    def relop(self):
        if self.char == '<':
            self.match('<')
        elif self.char == '==':
            self.match('==')
        else:
            if self.non_terminal_panic_mode('Relop'):
                self.relop()

    def additive_expression(self):
        if self.check_char_in_first('Term'):
            self.term()
            self.d()
        else:
            if self.non_terminal_panic_mode('Additive-expression'):
                self.additive_expression()

    def additive_expression_prime(self):
        if self.check_char_in_first('Term-prime'):
            self.term_prime()
            self.d()
        else:
            if self.non_terminal_panic_mode('Additive-expression-prime'):
                self.additive_expression_prime()

    def additive_expression_zegond(self):
        if self.check_char_in_first('Term-zegond'):
            self.term_zegond()
            self.d()
        else:
            if self.non_terminal_panic_mode('Additive-expression-zegond'):
                self.additive_expression_zegond()

    def d(self):
        if self.check_char_in_first('Addop'):
            self.addop()
            self.term()
            self.d()
        else:
            if self.non_terminal_panic_mode('D'):
                self.d()

    def addop(self):
        if self.char == '+':
            self.match('+')
        elif self.char == '-':
            self.match('-')
        else:
            if self.non_terminal_panic_mode('addop'):
                self.addop()

    def term(self):
        if self.check_char_in_first('Factor'):
            self.factor()
            self.g()
        else:
            if self.non_terminal_panic_mode('Term'):
                self.term()

    def term_prime(self):
        if self.check_char_in_first('Factor-prime'):
            self.factor_prime()
            self.g()
        else:
            if self.non_terminal_panic_mode('Term-prime'):
                self.term_prime()

    def term_zegond(self):
        if self.check_char_in_first('Factor-zegond'):
            self.factor_zegond()
            self.g()
        else:
            if self.non_terminal_panic_mode('Term-zegond'):
                self.term_zegond()

    def g(self):
        if self.char == '*':
            self.match('*')
            self.factor()
            self.g()
        else:
            if self.non_terminal_panic_mode('G'):
                self.g()

    def factor(self):
        if self.char == '(':
            self.match('(')
            self.expression()
            self.match(')')
        elif self.token == 'ID':  # token not char
            self.match('ID')
            self.var_call_prime()
        elif self.char == 'NUM':
            self.match('NUM')
        else:
            if self.non_terminal_panic_mode('Factor'):
                self.factor()

    def var_call_prime(self):
        if self.char == '(':
            self.match('(')
            self.args()
            self.match(')')
        elif self.check_char_in_first('Var-prime'):
            self.var_prime()
        else:
            if self.non_terminal_panic_mode('Var-call-prime'):
                self.var_call_prime()

    def var_prime(self):
        if self.char == '[':
            self.match('[')
            self.expression()
            self.match(']')
        else:
            if self.non_terminal_panic_mode('Var-prime'):
                self.var_prime()

    def factor_prime(self):
        if self.char == '(':
            self.match('(')
            self.args()
            self.match(')')
        else:
            if self.non_terminal_panic_mode('Factor_prime'):
                self.factor_prime()

    def factor_zegond(self):
        if self.char == '(':
            self.match('(')
            self.expression()
            self.match(')')
        elif self.char == 'NUM':
            self.match('NUM')
        else:
            if self.non_terminal_panic_mode('Factor-zegond'):
                self.factor_zegond()

    def args(self):
        if self.check_char_in_first('Arg-list'):
            self.arg_list()
        else:
            if self.non_terminal_panic_mode('Args'):
                self.args()

    def arg_list(self):
        if self.check_char_in_first('Expression'):
            self.expression()
            self.arg_list_prime()
        else:
            if self.non_terminal_panic_mode('Arg-list'):
                self.arg_list()

    def arg_list_prime(self):
        if self.char == ',':
            self.match(',')
            self.expression()
            self.arg_list_prime()
        else:
            if self.non_terminal_panic_mode('Arg-list-prime'):
                self.arg_list_prime()
