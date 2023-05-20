import json
from anytree import Node, RenderTree

from phase1.scanner import Scanner
from phase1.utils.characterchecker import keywords_set


class Parser:
    scanner = None
    data = None
    line_no = 0
    lookahead = []
    token = None
    char = None
    error_messages = dict()
    symbols = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<', '/', '*', '=', '=='}
    program_node = None

    def __init__(self, scanner_location, predictset_location):
        self.scanner = Scanner(scanner_location)
        with open(predictset_location) as f:
            self.data = json.load(f)

    def parse(self):
        while self.lookahead != '$':
            self.lookahead = self.scanner.get_next_token()
            if self.lookahead == '$':
                break
            if self.lookahead is not None:
                # print(self.lookahead)
                self.set_token(self.lookahead)
                self.set_char(self.lookahead)
                self.set_line_no(self.lookahead)
                self.program_node = Node('Program')
                f = self.program()
                if not f:
                    self.program_node = None
                # print(f)
        end_node = Node('$', self.program_node)
        print('errors:::::')
        print(self.error_messages)
        # for pre, fill, node in RenderTree(self.program_node):
        #     print("%s%s" % (pre, node.name))
        # with open('output.txt', 'w') as f:
        #     for pre, fill, node in RenderTree(self.program_node):
        #         f.write("%s%s\n" % (pre, node.name))
        output_string = ''
        for pre, fill, node in RenderTree(self.program_node):
            output_string += "%s%s\n" % (pre, node.name)
        print(output_string)
        with open('output.txt', 'w',  encoding="utf-8") as f:
            f.write(output_string)

    def get_next(self):
        self.lookahead = self.scanner.get_next_token()
        while self.lookahead is None:
            self.lookahead = self.scanner.get_next_token()
        print(self.lookahead)
        self.set_token(self.lookahead)
        self.set_char(self.lookahead)
        self.set_line_no(self.lookahead)

    def set_char(self, lk):
        if lk != '$':
            self.char = lk[0][1]
        else:
            self.char = '$'

    def set_line_no(self, lk):
        if lk != '$':
            self.line_no = lk[1]
        else:
            self.line_no = 0  # special case

    def set_token(self, lk):
        if lk != '$':
            self.token = lk[0][0]
        else:
            self.token = '$'

    def match(self, terminal):
        matched = False
        if self.is_keyword(self.char) or self.is_symbol(self.char):
            if self.char == terminal:
                matched = True
                # print(terminal)
                # # build tree
            else:
                self.add_error_message('missing ' + terminal)
        else:
            if self.token == terminal:
                matched = True
                # print(terminal)
                # build tree
            else:
                self.add_error_message('missing ' + terminal)
        self.get_next()
        return matched

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

    def check_for_second_scenario(self, check_for_epsilon, check_in_first):
        return self.check_epsilon_in_first(check_for_epsilon) and self.check_char_in_first(check_in_first)

    def apply_function(self, f, x):
        return f(x)

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
            return self.build_tree_and_return_usage(self.program_node, 'Declaration-list', self.declaration_list)
        else:
            if self.non_terminal_panic_mode('Program'):
                # self.program()
                pass
            return False

    def declaration_list(self, node):
        if self.check_char_in_first('Declaration') or self.check_for_second_scenario('Declaration', 'Declaration-list'):
            f1 = self.build_tree_and_return_usage(node, 'Declaration', self.declaration)
            f2 = self.build_tree_and_return_usage(node, 'Declaration-list', self.declaration_list)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Declaration-list'):
                # self.declaration_list()
                pass
            return False

    def declaration(self, node):
        if self.check_char_in_first('Declaration-initial'):
            f1 = self.build_tree_and_return_usage(node, 'Declaration-initial', self.declaration_initial)
            f2 = self.build_tree_and_return_usage(node, 'Declaration-prime', self.declaration_prime)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Declaration'):
                # self.declaration()
                pass
            return False

    def build_tree_and_return_usage(self, parent, child_name, function):
        child = Node(child_name, parent)
        if not self.apply_function(function, child):
            child = None
            return False
        return True

    def build_tree_for_terminals(self, parent, match_parameter):
        child = Node('(' + self.token + ', ' + self.char + ')', parent)
        if not self.apply_function(self.match, match_parameter):
            child = None
            return False
        return True

    def declaration_initial(self, node):
        if self.check_char_in_first('Type-specifier'):
            f1 = self.build_tree_and_return_usage(node, 'Type-specifier', self.type_specifier)
            f2 = self.build_tree_for_terminals(node, 'ID')
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Declaration-initial'):
                # self.declaration_initial()
                pass
            return False

    def declaration_prime(self, node):
        if self.check_char_in_first('Fun-declaration-prime'):
            return self.build_tree_and_return_usage(node, 'Fun-declaration-prime', self.fun_declaration_prime)
        elif self.check_char_in_first('Var-declaration-prime'):
            return self.build_tree_and_return_usage(node, 'Var-declaration-prime', self.var_declaration_prime)
        else:
            if self.non_terminal_panic_mode('Declaration-prime'):
                # self.declaration_prime()
                pass
            return False

    def apply_function_two_par(self, f, x, y):
        return f(x, y)

    def apply_function_three_par(self, f, x, y, z):
        return f(x, y, z)

    def fuck(self, a):
        pass

    def var_declaration_prime(self, node):
        if self.char == ';':
            return self.build_tree_for_terminals(node, ';')
        elif self.char == '[':
            f1 = self.build_tree_for_terminals(node, '[')
            f2 = self.build_tree_for_terminals(node, 'NUM')
            f3 = self.build_tree_for_terminals(node, ']')
            f4 = self.build_tree_for_terminals(node, ';')
            return f1 or f2 or f3 or f4
        else:
            if self.non_terminal_panic_mode('Var-declaration-prime'):
                pass
                # self.var_declaration_prime()
            return False

    def fun_declaration_prime(self, node):
        if self.char == '(':
            f1 = self.build_tree_for_terminals(node, '(')
            f2 = self.build_tree_and_return_usage(node, 'Params', self.params)
            f3 = self.build_tree_for_terminals(node, ')')
            f4 = self.build_tree_and_return_usage(node, 'Compound-stmt', self.compound_stmt)
            return f1 or f2 or f3 or f4
        else:
            if self.non_terminal_panic_mode('Fun-declaration-prime'):
                pass
                # self.fun_declaration_prime()
            return False

    def type_specifier(self, node):
        if self.char == 'int':
            return self.build_tree_for_terminals(node, 'int')
        elif self.char == 'void':
            return self.build_tree_for_terminals(node, 'void')
        else:
            if self.non_terminal_panic_mode('Type-specifier'):
                pass
                # self.type_specifier()
            return False

    def params(self, node):
        if self.char == 'int':
            f1 = self.build_tree_for_terminals(node, 'int')
            f2 = self.build_tree_for_terminals(node, 'ID')
            f3 = self.build_tree_and_return_usage(node, 'Param-prime', self.param_prime)
            f4 = self.build_tree_and_return_usage(node, 'Param-list', self.param_prime)
            return f1 or f2 or f3 or f4
        elif self.char == 'void':
            return self.build_tree_for_terminals(node, 'void')
        else:
            if self.non_terminal_panic_mode('Params'):
                pass
                # self.params()
            return False

    def param_list(self, node):
        if self.char == ',':
            f1 = self.build_tree_for_terminals(node, ',')
            f2 = self.build_tree_and_return_usage(node, 'Param', self.param)
            f3 = self.build_tree_and_return_usage(node, 'Param-list', self.param_list)
            return f1 or f2 or f3
        else:
            if self.non_terminal_panic_mode('Param-list'):
                pass
                # self.param_list()
            return False

    def param(self, node):
        if self.check_char_in_first('Declaration-initial'):
            f1 = self.build_tree_and_return_usage(node, 'Declaration-initial', self.declaration_initial)
            f2 = self.build_tree_and_return_usage(node, 'Param-prime', self.param_prime)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Param'):
                pass
                # self.param()
            return False

    def param_prime(self, node):
        if self.char == '[':
            f1 = self.build_tree_for_terminals(node, '[')
            f2 = self.build_tree_for_terminals(node, ']')
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Param-prime'):
                pass
                # self.param_prime()
            return False

    def compound_stmt(self, node):
        if self.char == '{':
            f1 = self.build_tree_for_terminals(node, '{')
            f2 = self.build_tree_and_return_usage(node, 'Declaration-list', self.declaration_list)
            f3 = self.build_tree_and_return_usage(node, 'Statement-list', self.statement_list)
            f4 = self.build_tree_for_terminals(node, '}')
            return f1 or f2 or f3 or f4
        else:
            if self.non_terminal_panic_mode('Compound-stmt'):
                pass
                # self.compound_stmt()
            return False

    def statement_list(self, node):
        if self.check_char_in_first('Statement'):
            f1 = self.build_tree_and_return_usage(node, 'Statement', self.statement)
            f2 = self.build_tree_and_return_usage(node, 'Statement-list', self.statement_list)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Statement-list'):
                pass
                # self.statement_list()
            return False

    def statement(self, node):
        if self.check_char_in_first('Expression-stmt'):
            return self.build_tree_and_return_usage(node, 'Expression-stmt', self.expression_stmt)
        elif self.check_char_in_first('Compound-stmt'):
            return self.build_tree_and_return_usage(node, 'Compound-stmt', self.compound_stmt)
        elif self.check_char_in_first('Selection-stmt'):
            return self.build_tree_and_return_usage(node, 'Selection-stmt', self.selection_stmt)
        elif self.check_char_in_first('Iteration-stmt'):
            return self.build_tree_and_return_usage(node, 'Iteration-stmt', self.iteration_stmt)
        elif self.check_char_in_first('Return-stmt'):
            return self.build_tree_and_return_usage(node, 'Return-stmt', self.return_stmt)
        else:
            if self.non_terminal_panic_mode('Statement'):
                pass
                # self.statement()
            return False

    def expression_stmt(self, node):
        if self.check_char_in_first('Expression'):
            f1 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            f2 = self.build_tree_for_terminals(node, ';')
            return f1 or f2
        elif self.char == 'break':
            f1 = self.build_tree_for_terminals(node, 'break')
            f2 = self.build_tree_for_terminals(node, ';')
            return f1 or f2
        elif self.char == ';':
            return self.build_tree_for_terminals(node, ';')
        else:
            if self.non_terminal_panic_mode('Expression-stmt'):
                pass
                # self.expression_stmt()
            return False

    def selection_stmt(self, node):
        if self.char == 'if':
            f1 = self.build_tree_for_terminals(node, 'if')
            f2 = self.build_tree_for_terminals(node, '(')
            f3 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            f4 = self.build_tree_for_terminals(node, ')')
            f5 = self.build_tree_and_return_usage(node, 'Statement', self.statement)
            f6 = self.build_tree_for_terminals(node, 'else')
            f7 = self.build_tree_and_return_usage(node, 'Statement', self.statement)
            return f1 or f2 or f3 or f4 or f5 or f6 or f7
        else:
            if self.non_terminal_panic_mode('Selection-stmt'):
                pass
                # self.selection_stmt()
            return False

    def iteration_stmt(self, node):
        if self.char == 'repeat':
            f1 = self.build_tree_for_terminals(node, 'repeat')
            f2 = self.build_tree_and_return_usage(node, 'Statement', self.statement)
            f3 = self.build_tree_for_terminals(node, 'until')
            f4 = self.build_tree_for_terminals(node, '(')
            f5 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            f6 = self.build_tree_for_terminals(node, ')')
            return f1 or f2 or f3 or f4 or f5 or f6
        else:
            if self.non_terminal_panic_mode('Iteration-stmt'):
                pass
                # self.iteration_stmt()
            return False

    def return_stmt(self, node):
        if self.char == 'return':
            f1 = self.build_tree_for_terminals(node, 'return')
            f2 = self.build_tree_and_return_usage(node, 'Return-stmt-prime', self.return_stmt_prime)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Return-stmt'):
                pass
                # self.return_stmt()
            return False

    def return_stmt_prime(self, node):
        if self.char == ';':
            return self.build_tree_for_terminals(node, ';')
        elif self.check_char_in_first('Expression'):
            f1 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            f2 = self.build_tree_for_terminals(node, ';')
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Return-stmt-prime'):
                pass
                # self.return_stmt_prime()
            return False

    def expression(self, node):
        if self.check_char_in_first('Simple-expression-zegond'):
            return self.build_tree_and_return_usage(node, 'Simple-expression-zegond', self.simple_expression_zegond)
        elif self.token == 'ID':  # token no char
            f1 = self.build_tree_for_terminals(node, 'ID')
            f2 = self.build_tree_and_return_usage(node, 'B', self.b)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Expression'):
                pass
                # self.expression()
            return False

    def b(self, node):
        if self.char == '=':
            f1 = self.build_tree_for_terminals(node, '=')
            f2 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            return f1 or f2
        elif self.char == '[':
            f1 = self.build_tree_for_terminals(node, '[')
            f2 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            f3 = self.build_tree_for_terminals(node, ']')
            f4 = self.build_tree_and_return_usage(node, 'H', self.h)
            return f1 or f2 or f3 or f4
        elif self.check_char_in_first('Simple-expression-prime'):
            return self.build_tree_and_return_usage(node, 'Simple-expression-prime', self.simple_expression_prime)
        else:
            if self.non_terminal_panic_mode('B'):
                pass
                # self.b()
            return False

    def h(self, node):
        if self.char == '=':
            f1 = self.build_tree_for_terminals(node, '=')
            f2 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            return f1 or f2
        elif self.check_char_in_first('G') or self.check_for_second_scenario('G', 'D'):
            f1 = self.build_tree_and_return_usage(node, 'G', self.g)
            f2 = self.build_tree_and_return_usage(node, 'D', self.d)
            f3 = self.build_tree_and_return_usage(node, 'C', self.c)
            return f1 or f2 or f3
        else:
            if self.non_terminal_panic_mode('H'):
                pass
                # self.h()
            return False

    def simple_expression_zegond(self, node):
        if self.check_char_in_first('Additive-expression-zegond'):
            f1 = self.build_tree_and_return_usage(node, 'Additive-expression-zegond', self.additive_expression_zegond)
            f2 = self.build_tree_and_return_usage(node, 'C', self.c)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Simple-expression-zegond'):
                pass
                # self.simple_expression_zegond()
            return

    def simple_expression_prime(self, node):
        if self.check_char_in_first('Additive-expression-prime') or \
                self.check_for_second_scenario('Additive-expression-prime', 'C'):
            f1 = self.build_tree_and_return_usage(node, 'Additive-expression-prime', self.additive_expression_prime)
            f2 = self.build_tree_and_return_usage(node, 'C', self.c)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Simple-expression-prime'):
                pass
                # self.simple_expression_prime()
            return False

    def c(self, node):
        if self.check_char_in_first('Relop'):
            f1 = self.build_tree_and_return_usage(node, 'Relop', self.relop)
            f2 = self.build_tree_and_return_usage(node, 'Additive-expression', self.additive_expression)
            return f1 or f2
            # if not (f1 or f2)
            #     child = ('epsilon' , node)
            # return True
        else:
            if self.non_terminal_panic_mode('C'):
                pass
                # self.c()
            return False

    def relop(self, node):
        if self.char == '<':
            return self.build_tree_for_terminals(node, '<')
        elif self.char == '==':
            return self.build_tree_for_terminals(node, '==')
        else:
            if self.non_terminal_panic_mode('Relop'):
                pass
                # self.relop()
            return False

    def additive_expression(self, node):
        if self.check_char_in_first('Term'):
            f1 = self.build_tree_and_return_usage(node, 'Term', self.term)
            f2 = self.build_tree_and_return_usage(node, 'D', self.d)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Additive-expression'):
                pass
                # self.additive_expression()
            return False

    def additive_expression_prime(self, node):
        if self.check_char_in_first('Term-prime') or self.check_for_second_scenario('Term-prime', 'D'):
            f1 = self.build_tree_and_return_usage(node, 'Term-prime', self.term_prime)
            f2 = self.build_tree_and_return_usage(node, 'D', self.d)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Additive-expression-prime'):
                pass
                # self.additive_expression_prime()
            return False

    def additive_expression_zegond(self, node):
        if self.check_char_in_first('Term-zegond'):
            f1 = self.build_tree_and_return_usage(node, 'Term-zegond', self.term_zegond)
            f2 = self.build_tree_and_return_usage(node, 'D', self.d)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Additive-expression-zegond'):
                pass
                # self.additive_expression_zegond()
            return False

    def d(self, node):
        if self.check_char_in_first('Addop'):
            f1 = self.build_tree_and_return_usage(node, 'Addop', self.addop)
            f2 = self.build_tree_and_return_usage(node, 'Term', self.term)
            f3 = self.build_tree_and_return_usage(node, 'D', self.d)
            return f1 or f2 or f3
        else:
            if self.non_terminal_panic_mode('D'):
                pass
                # self.d()
            return False

    def addop(self, node):
        if self.char == '+':
            return self.build_tree_for_terminals(node, '+')
        elif self.char == '-':
            return self.build_tree_for_terminals(node, '-')
        else:
            if self.non_terminal_panic_mode('Addop'):
                pass
                # self.addop()
            return False

    def term(self, node):
        if self.check_char_in_first('Factor'):
            f1 = self.build_tree_and_return_usage(node, 'Factor', self.factor)
            f2 = self.build_tree_and_return_usage(node, 'G', self.g)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Term'):
                pass
                # self.term()
            return False

    def term_prime(self, node):
        if self.check_char_in_first('Factor-prime') or self.check_for_second_scenario('Factor-prime', 'G'):
            f1 = self.build_tree_and_return_usage(node, 'Factor-prime', self.factor_prime)
            f2 = self.build_tree_and_return_usage(node, 'G', self.g)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Term-prime'):
                pass
                # self.term_prime()
            return False

    def term_zegond(self, node):
        if self.check_char_in_first('Factor-zegond'):
            f1 = self.build_tree_and_return_usage(node, 'Factor-zegond', self.factor_zegond)
            f2 = self.build_tree_and_return_usage(node, 'G', self.g)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Term-zegond'):
                pass
                # self.term_zegond()
            return False

    def g(self, node):
        if self.char == '*':
            f1 = self.build_tree_for_terminals(node, '*')
            f2 = self.build_tree_and_return_usage(node, 'Factor', self.factor)
            f3 = self.build_tree_and_return_usage(node, 'G', self.g)
            return f1 or f2 or f3
        else:
            if self.non_terminal_panic_mode('G'):
                pass
                # self.g()
            return False

    def factor(self, node):
        if self.char == '(':
            f1 = self.build_tree_for_terminals(node, '(')
            f2 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            f3 = self.build_tree_for_terminals(node, ')')
            return f1 or f2 or f3
        elif self.token == 'ID':  # token not char
            f1 = self.build_tree_for_terminals(node, 'ID')
            f2 = self.build_tree_and_return_usage(node, 'Var-call-prime', self.var_call_prime)
            return f1 or f2
        elif self.token == 'NUM':  # token not char
            return self.build_tree_for_terminals(node, 'NUM')
        else:
            if self.non_terminal_panic_mode('Factor'):
                pass
                # self.factor()
            return False

    def var_call_prime(self, node):
        if self.char == '(':
            f1 = self.build_tree_for_terminals(node, '(')
            f2 = self.build_tree_and_return_usage(node, 'Args', self.args)
            f3 = self.build_tree_for_terminals(node, ')')
            return f1 or f2 or f3
        elif self.check_char_in_first('Var-prime'):
            return self.build_tree_and_return_usage(node, 'Var-prime', self.var_prime)
        else:
            if self.non_terminal_panic_mode('Var-call-prime'):
                pass
                # self.var_call_prime()
            return False

    def var_prime(self, node):
        if self.char == '[':
            f1 = self.build_tree_for_terminals(node, '[')
            f2 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            f3 = self.build_tree_for_terminals(node, ']')
            return f1 or f2 or f3
        else:
            if self.non_terminal_panic_mode('Var-prime'):
                pass
                # self.var_prime()
            return False

    def factor_prime(self, node):
        if self.char == '(':
            f1 = self.build_tree_for_terminals(node, '(')
            f2 = self.build_tree_and_return_usage(node, 'Args', self.args)
            f3 = self.build_tree_for_terminals(node, ')')
            return f1 or f2 or f3
        else:
            if self.non_terminal_panic_mode('Factor-prime'):
                pass
                # self.factor_prime()
            return False

    def factor_zegond(self, node):
        if self.char == '(':
            f1 = self.build_tree_for_terminals(node, '(')
            f2 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            f3 = self.build_tree_for_terminals(node, ')')
            return f1 or f2 or f3
        elif self.token == 'NUM':  # token not char
            return self.build_tree_for_terminals(node, 'NUM')
        else:
            if self.non_terminal_panic_mode('Factor-zegond'):
                pass
                # self.factor_zegond()
            return False

    def args(self, node):
        if self.check_char_in_first('Arg-list'):
            return self.build_tree_and_return_usage(node, 'Arg-list', self.arg_list)
        else:
            if self.non_terminal_panic_mode('Args'):
                pass
                # self.args()
            return False

    def arg_list(self, node):
        if self.check_char_in_first('Expression'):
            f1 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            f2 = self.build_tree_and_return_usage(node, 'Arg-list-prime', self.arg_list_prime)
            return f1 or f2
        else:
            if self.non_terminal_panic_mode('Arg-list'):
                pass
                # self.arg_list()
            return False

    def arg_list_prime(self, node):
        if self.char == ',':
            f1 = self.build_tree_for_terminals(node, ',')
            f2 = self.build_tree_and_return_usage(node, 'Expression', self.expression)
            f3 = self.build_tree_and_return_usage(node, 'Arg-list-prime', self.arg_list_prime)
            return f1 or f2 or f3
        else:
            if self.non_terminal_panic_mode('Arg-list-prime'):
                pass
                # self.arg_list_prime()
            return False
