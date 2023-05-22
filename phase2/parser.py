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
                self.set_token(self.lookahead)
                self.set_char(self.lookahead)
                self.set_line_no(self.lookahead)
                self.program_node = Node('Program')
                f = self.program()
                if not f:
                    self.program_node = None
        end_node = Node('$', self.program_node)
        # print('errors:::::')
        print(self.error_messages)
        output_string = ''
        for pre, fill, node in RenderTree(self.program_node):
            output_string += "%s%s\n" % (pre, node.name)
        output_string = output_string[:-1]
        with open('parse_tree.txt', 'w', encoding="utf-8") as f:
            f.write(output_string)

        output_string2 = 'There is no syntax error.'
        with open('syntax_errors.txt', 'w', encoding="utf-8") as f:
            f.write(output_string2)

    def get_next(self):
        self.lookahead = self.scanner.get_next_token()
        while self.lookahead is None:
            self.lookahead = self.scanner.get_next_token()
        # print(self.lookahead)
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

    def check_all2_go_to_epsilon(self, a, b):
        return 'EPSILON' in self.data['first'][a] and 'EPSILON' in self.data['first'][b]

    def check_all3_go_to_epsilon(self, a, b, c):
        return 'EPSILON' in self.data['first'][a] and 'EPSILON' in self.data['first'][b] \
               and 'EPSILON' in self.data['first'][c]

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

    def non_terminal_panic_mode(self, non_terminal, node):
        if self.check_char_in_follow(non_terminal):
            if self.check_epsilon_in_first(non_terminal):
                self.epsilon_in_tree(node)
                return True
            else:
                self.add_error_message(self.missing_error_message())
                return False  # No recursion
        else:
            self.add_error_message(self.illegal_error_message())
            self.get_next()
            return False  # Recursion

    def epsilon_in_tree(self, parent):
        child = Node('epsilon', parent)

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

    def program(self):
        if self.check_char_in_first('Declaration-list') or self.check_all2_go_to_epsilon('Program', 'Declaration-list'):
            return self.build_tree_and_return_usage(self.program_node, 'Declaration-list', self.declaration_list)
        else:
            return self.non_terminal_panic_mode('Program', self.program_node)
            # self.program()

    def declaration_list(self, node):
        if self.check_char_in_first('Declaration') or self.check_for_second_scenario('Declaration', 'Declaration-list') \
                or self.check_all2_go_to_epsilon('Declaration', 'Declaration-list'):
            self.build_tree_and_return_usage(node, 'Declaration', self.declaration)
            self.build_tree_and_return_usage(node, 'Declaration-list', self.declaration_list)
            return True
        else:
            return self.non_terminal_panic_mode('Declaration-list', node)
            # self.declaration_list()

    def declaration(self, node):
        if self.check_char_in_first('Declaration-initial') \
                or self.check_all3_go_to_epsilon('Declaration-initial', 'Declaration-prime', 'Declaration-prime'):
            self.build_tree_and_return_usage(node, 'Declaration-initial', self.declaration_initial)
            self.build_tree_and_return_usage(node, 'Declaration-prime', self.declaration_prime)
            return True
        else:
            return self.non_terminal_panic_mode('Declaration', node)
            # self.declaration()

    def declaration_initial(self, node):
        if self.check_char_in_first('Type-specifier'):
            self.build_tree_and_return_usage(node, 'Type-specifier', self.type_specifier)
            self.build_tree_for_terminals(node, 'ID')
            return True
        else:
            return self.non_terminal_panic_mode('Declaration-initial', node)
            # self.declaration_initial()

    def declaration_prime(self, node):
        if self.check_char_in_first('Fun-declaration-prime') \
                or self.check_all2_go_to_epsilon('Fun-declaration-prime', 'Declaration-prime'):
            return self.build_tree_and_return_usage(node, 'Fun-declaration-prime', self.fun_declaration_prime)
        elif self.check_char_in_first('Var-declaration-prime') \
                or self.check_all2_go_to_epsilon('Var-declaration-prime', 'Declaration-prime'):
            return self.build_tree_and_return_usage(node, 'Var-declaration-prime', self.var_declaration_prime)
        else:
            return self.non_terminal_panic_mode('Declaration-prime', node)
            # self.declaration_prime()

    def var_declaration_prime(self, node):
        if self.char == ';':
            return self.build_tree_for_terminals(node, ';')
        elif self.char == '[':
            self.build_tree_for_terminals(node, '[')
            self.build_tree_for_terminals(node, 'NUM')
            self.build_tree_for_terminals(node, ']')
            self.build_tree_for_terminals(node, ';')
            return True
        else:
            return self.non_terminal_panic_mode('Var-declaration-prime', node)

            # self.var_declaration_prime()

    def fun_declaration_prime(self, node):
        if self.char == '(':
            self.build_tree_for_terminals(node, '(')
            self.build_tree_and_return_usage(node, 'Params', self.params)
            self.build_tree_for_terminals(node, ')')
            self.build_tree_and_return_usage(node, 'Compound-stmt', self.compound_stmt)
            return True
        else:
            return self.non_terminal_panic_mode('Fun-declaration-prime', node)

            # self.fun_declaration_prime()

    def type_specifier(self, node):
        if self.char == 'int':
            return self.build_tree_for_terminals(node, 'int')
        elif self.char == 'void':
            return self.build_tree_for_terminals(node, 'void')
        else:
            return self.non_terminal_panic_mode('Type-specifier', node)

            # self.type_specifier()

    def params(self, node):
        if self.char == 'int':
            self.build_tree_for_terminals(node, 'int')
            self.build_tree_for_terminals(node, 'ID')
            self.build_tree_and_return_usage(node, 'Param-prime', self.param_prime)
            self.build_tree_and_return_usage(node, 'Param-list', self.param_prime)
            return True
        elif self.char == 'void':
            return self.build_tree_for_terminals(node, 'void')
        else:
            return self.non_terminal_panic_mode('Params', node)

            # self.params()

    def param_list(self, node):
        if self.char == ',':
            self.build_tree_for_terminals(node, ',')
            self.build_tree_and_return_usage(node, 'Param', self.param)
            self.build_tree_and_return_usage(node, 'Param-list', self.param_list)
            return True
        else:
            return self.non_terminal_panic_mode('Param-list', node)

            # self.param_list()

    def param(self, node):
        if self.check_char_in_first('Declaration-initial') \
                or self.check_all3_go_to_epsilon('Param', 'Declaration-initial', 'Param-prime'):
            self.build_tree_and_return_usage(node, 'Declaration-initial', self.declaration_initial)
            self.build_tree_and_return_usage(node, 'Param-prime', self.param_prime)
            return True
        else:
            return self.non_terminal_panic_mode('Param', node)

            # self.param()

    def param_prime(self, node):
        if self.char == '[':
            self.build_tree_for_terminals(node, '[')
            self.build_tree_for_terminals(node, ']')
            return True
        else:
            return self.non_terminal_panic_mode('Param-prime', node)

            # self.param_prime()

    def compound_stmt(self, node):
        if self.char == '{':
            self.build_tree_for_terminals(node, '{')
            self.build_tree_and_return_usage(node, 'Declaration-list', self.declaration_list)
            self.build_tree_and_return_usage(node, 'Statement-list', self.statement_list)
            self.build_tree_for_terminals(node, '}')
            return True
        else:
            return self.non_terminal_panic_mode('Compound-stmt', node)

            # self.compound_stmt()

    def statement_list(self, node):
        if self.check_char_in_first('Statement') or self.check_all2_go_to_epsilon('Statement', 'Statement-list'):
            self.build_tree_and_return_usage(node, 'Statement', self.statement)
            self.build_tree_and_return_usage(node, 'Statement-list', self.statement_list)
            return True
        else:
            return self.non_terminal_panic_mode('Statement-list', node)

            # self.statement_list()

    def statement(self, node):
        if self.check_char_in_first('Expression-stmt') or self.check_all2_go_to_epsilon('Statement', 'Expression-stmt'):
            return self.build_tree_and_return_usage(node, 'Expression-stmt', self.expression_stmt)
        elif self.check_char_in_first('Compound-stmt') or self.check_all2_go_to_epsilon('Statement', 'Compound-stmt'):
            return self.build_tree_and_return_usage(node, 'Compound-stmt', self.compound_stmt)
        elif self.check_char_in_first('Selection-stmt') or self.check_all2_go_to_epsilon('Statement', 'Selection-stmt'):
            return self.build_tree_and_return_usage(node, 'Selection-stmt', self.selection_stmt)
        elif self.check_char_in_first('Iteration-stmt') or self.check_all2_go_to_epsilon('Statement', 'Iteration-stmt'):
            return self.build_tree_and_return_usage(node, 'Iteration-stmt', self.iteration_stmt)
        elif self.check_char_in_first('Return-stmt') or self.check_all2_go_to_epsilon('Statement', 'Return-stmt'):
            return self.build_tree_and_return_usage(node, 'Return-stmt', self.return_stmt)
        else:
            return self.non_terminal_panic_mode('Statement', node)

            # self.statement()

    def expression_stmt(self, node):
        if self.check_char_in_first('Expression'):
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            self.build_tree_for_terminals(node, ';')
            return True
        elif self.char == 'break':
            self.build_tree_for_terminals(node, 'break')
            self.build_tree_for_terminals(node, ';')
            return True
        elif self.char == ';':
            return self.build_tree_for_terminals(node, ';')
        else:
            return self.non_terminal_panic_mode('Expression-stmt', node)

            # self.expression_stmt()

    def selection_stmt(self, node):
        if self.char == 'if':
            self.build_tree_for_terminals(node, 'if')
            self.build_tree_for_terminals(node, '(')
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            self.build_tree_for_terminals(node, ')')
            self.build_tree_and_return_usage(node, 'Statement', self.statement)
            self.build_tree_for_terminals(node, 'else')
            self.build_tree_and_return_usage(node, 'Statement', self.statement)
            return True
        else:
            return self.non_terminal_panic_mode('Selection-stmt', node)

            # self.selection_stmt()

    def iteration_stmt(self, node):
        if self.char == 'repeat':
            self.build_tree_for_terminals(node, 'repeat')
            self.build_tree_and_return_usage(node, 'Statement', self.statement)
            self.build_tree_for_terminals(node, 'until')
            self.build_tree_for_terminals(node, '(')
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            self.build_tree_for_terminals(node, ')')
            return True
        else:
            return self.non_terminal_panic_mode('Iteration-stmt', node)

            # self.iteration_stmt()

    def return_stmt(self, node):
        if self.char == 'return':
            self.build_tree_for_terminals(node, 'return')
            self.build_tree_and_return_usage(node, 'Return-stmt-prime', self.return_stmt_prime)
            return True
        else:
            return self.non_terminal_panic_mode('Return-stmt', node)

            # self.return_stmt()

    def return_stmt_prime(self, node):
        if self.char == ';':
            return self.build_tree_for_terminals(node, ';')
        elif self.check_char_in_first('Expression'):
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            self.build_tree_for_terminals(node, ';')
            return True
        else:
            return self.non_terminal_panic_mode('Return-stmt-prime', node)

            # self.return_stmt_prime()

    def expression(self, node):
        if self.check_char_in_first('Simple-expression-zegond') \
                or self.check_all2_go_to_epsilon('Simple-expression-zegond', 'Expression'):
            return self.build_tree_and_return_usage(node, 'Simple-expression-zegond', self.simple_expression_zegond)
        elif self.token == 'ID':  # token no char
            self.build_tree_for_terminals(node, 'ID')
            self.build_tree_and_return_usage(node, 'B', self.b)
            return True
        else:
            return self.non_terminal_panic_mode('Expression', node)

            # self.expression()

    def b(self, node):
        if self.char == '=':
            self.build_tree_for_terminals(node, '=')
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            return True
        elif self.char == '[':
            self.build_tree_for_terminals(node, '[')
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            self.build_tree_for_terminals(node, ']')
            self.build_tree_and_return_usage(node, 'H', self.h)
            return True
        elif self.check_char_in_first('Simple-expression-prime') \
                or self.check_all2_go_to_epsilon('B', 'Simple-expression-prime'):
            return self.build_tree_and_return_usage(node, 'Simple-expression-prime', self.simple_expression_prime)
        else:
            return self.non_terminal_panic_mode('B', node)

            # self.b()

    def h(self, node):
        if self.char == '=':
            self.build_tree_for_terminals(node, '=')
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            return True
        elif self.check_char_in_first('G') or self.check_for_second_scenario('G', 'D') \
                or (self.check_all3_go_to_epsilon('H', 'G', 'D') and self.check_epsilon_in_first('C')):
            self.build_tree_and_return_usage(node, 'G', self.g)
            self.build_tree_and_return_usage(node, 'D', self.d)
            self.build_tree_and_return_usage(node, 'C', self.c)
            return True
        else:
            return self.non_terminal_panic_mode('H', node)

            # self.h()

    def simple_expression_zegond(self, node):
        if self.check_char_in_first('Additive-expression-zegond') \
                or self.check_all3_go_to_epsilon('Simple-expression-zegond', 'Additive-expression-zegond', 'C'):
            self.build_tree_and_return_usage(node, 'Additive-expression-zegond', self.additive_expression_zegond)
            self.build_tree_and_return_usage(node, 'C', self.c)
            return True
        else:
            return self.non_terminal_panic_mode('Simple-expression-zegond', node)

            # self.simple_expression_zegond()

    def simple_expression_prime(self, node):
        if self.check_char_in_first('Additive-expression-prime') or \
                self.check_for_second_scenario('Additive-expression-prime', 'C') \
                or self.check_all3_go_to_epsilon('Simple-expression-prime', 'Additive-expression-prime', 'C'):
            self.build_tree_and_return_usage(node, 'Additive-expression-prime', self.additive_expression_prime)
            self.build_tree_and_return_usage(node, 'C', self.c)
            return True
        else:
            return self.non_terminal_panic_mode('Simple-expression-prime', node)

            # self.simple_expression_prime()

    def c(self, node):
        if self.check_char_in_first('Relop') or self.check_all3_go_to_epsilon('C', 'Relop', 'Additive-expression'):
            self.build_tree_and_return_usage(node, 'Relop', self.relop)
            self.build_tree_and_return_usage(node, 'Additive-expression', self.additive_expression)
            return True
            # if not (True )
            #     child = ('epsilon' , node)
            # return True
        else:
            return self.non_terminal_panic_mode('C', node)

            # self.c()

    def relop(self, node):
        if self.char == '<':
            return self.build_tree_for_terminals(node, '<')
        elif self.char == '==':
            return self.build_tree_for_terminals(node, '==')
        else:
            return self.non_terminal_panic_mode('Relop', node)

            # self.relop()

    def additive_expression(self, node):
        if self.check_char_in_first('Term') or self.check_all3_go_to_epsilon('Additive-expression', 'Term', 'D'):
            self.build_tree_and_return_usage(node, 'Term', self.term)
            self.build_tree_and_return_usage(node, 'D', self.d)
            return True
        else:
            return self.non_terminal_panic_mode('Additive-expression', node)

            # self.additive_expression()

    def additive_expression_prime(self, node):
        if self.check_char_in_first('Term-prime') or self.check_for_second_scenario('Term-prime', 'D') \
                or self.check_all3_go_to_epsilon('Additive-expression-prime', 'Term-prime', 'D'):
            self.build_tree_and_return_usage(node, 'Term-prime', self.term_prime)
            self.build_tree_and_return_usage(node, 'D', self.d)
            return True
        else:
            return self.non_terminal_panic_mode('Additive-expression-prime', node)

            # self.additive_expression_prime()

    def additive_expression_zegond(self, node):
        if self.check_char_in_first('Term-zegond') \
                or self.check_all3_go_to_epsilon('Additive-expression-zegond', 'Term-zegond', 'D'):
            self.build_tree_and_return_usage(node, 'Term-zegond', self.term_zegond)
            self.build_tree_and_return_usage(node, 'D', self.d)
            return True
        else:
            return self.non_terminal_panic_mode('Additive-expression-zegond', node)

            # self.additive_expression_zegond()

    def d(self, node):
        if self.check_char_in_first('Addop') or self.check_all3_go_to_epsilon('Addop', 'Term', 'D'):
            self.build_tree_and_return_usage(node, 'Addop', self.addop)
            self.build_tree_and_return_usage(node, 'Term', self.term)
            self.build_tree_and_return_usage(node, 'D', self.d)
            return True
        else:
            return self.non_terminal_panic_mode('D', node)

            # self.d()

    def addop(self, node):
        if self.char == '+':
            return self.build_tree_for_terminals(node, '+')
        elif self.char == '-':
            return self.build_tree_for_terminals(node, '-')
        else:
            return self.non_terminal_panic_mode('Addop', node)

            # self.addop()

    def term(self, node):
        if self.check_char_in_first('Factor') or self.check_all3_go_to_epsilon('Factor', 'G', 'Term'):
            self.build_tree_and_return_usage(node, 'Factor', self.factor)
            self.build_tree_and_return_usage(node, 'G', self.g)
            return True
        else:
            return self.non_terminal_panic_mode('Term', node)

            # self.term()

    def term_prime(self, node):
        if self.check_char_in_first('Factor-prime') or self.check_for_second_scenario('Factor-prime', 'G') \
                or self.check_all3_go_to_epsilon('Term-prime', 'Factor-prime', 'G'):
            self.build_tree_and_return_usage(node, 'Factor-prime', self.factor_prime)
            self.build_tree_and_return_usage(node, 'G', self.g)
            return True
        else:
            return self.non_terminal_panic_mode('Term-prime', node)

            # self.term_prime()

    def term_zegond(self, node):
        if self.check_char_in_first('Factor-zegond') \
                or self.check_all3_go_to_epsilon('Term-zegond', 'G', 'Factor-zegond'):
            self.build_tree_and_return_usage(node, 'Factor-zegond', self.factor_zegond)
            self.build_tree_and_return_usage(node, 'G', self.g)
            return True
        else:
            return self.non_terminal_panic_mode('Term-zegond', node)

            # self.term_zegond()

    def g(self, node):
        if self.char == '*':
            self.build_tree_for_terminals(node, '*')
            self.build_tree_and_return_usage(node, 'Factor', self.factor)
            self.build_tree_and_return_usage(node, 'G', self.g)
            return True
        else:
            return self.non_terminal_panic_mode('G', node)

            # self.g()

    def factor(self, node):
        if self.char == '(':
            self.build_tree_for_terminals(node, '(')
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            self.build_tree_for_terminals(node, ')')
            return True
        elif self.token == 'ID':  # token not char
            self.build_tree_for_terminals(node, 'ID')
            self.build_tree_and_return_usage(node, 'Var-call-prime', self.var_call_prime)
            return True
        elif self.token == 'NUM':  # token not char
            return self.build_tree_for_terminals(node, 'NUM')
        else:
            return self.non_terminal_panic_mode('Factor', node)

            # self.factor()

    def var_call_prime(self, node):
        if self.char == '(':
            self.build_tree_for_terminals(node, '(')
            self.build_tree_and_return_usage(node, 'Args', self.args)
            self.build_tree_for_terminals(node, ')')
            return True
        elif self.check_char_in_first('Var-prime') or self.check_all2_go_to_epsilon('Var-call-prime', 'Var-prime'):
            return self.build_tree_and_return_usage(node, 'Var-prime', self.var_prime)
        else:
            return self.non_terminal_panic_mode('Var-call-prime', node)

            # self.var_call_prime()

    def var_prime(self, node):
        if self.char == '[':
            self.build_tree_for_terminals(node, '[')
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            self.build_tree_for_terminals(node, ']')
            return True
        else:
            return self.non_terminal_panic_mode('Var-prime', node)

            # self.var_prime()

    def factor_prime(self, node):
        if self.char == '(':
            self.build_tree_for_terminals(node, '(')
            self.build_tree_and_return_usage(node, 'Args', self.args)
            self.build_tree_for_terminals(node, ')')
            return True
        else:
            return self.non_terminal_panic_mode('Factor-prime', node)

            # self.factor_prime()

    def factor_zegond(self, node):
        if self.char == '(':
            self.build_tree_for_terminals(node, '(')
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            self.build_tree_for_terminals(node, ')')
            return True
        elif self.token == 'NUM':  # token not char
            return self.build_tree_for_terminals(node, 'NUM')
        else:
            return self.non_terminal_panic_mode('Factor-zegond', node)

            # self.factor_zegond()

    def args(self, node):
        if self.check_char_in_first('Arg-list') or self.check_all2_go_to_epsilon('Args', 'Arg-list'):
            return self.build_tree_and_return_usage(node, 'Arg-list', self.arg_list)
        else:
            return self.non_terminal_panic_mode('Args', node)

            # self.args()

    def arg_list(self, node):
        if self.check_char_in_first('Expression') \
                or self.check_all3_go_to_epsilon('Arg-list', 'Expression', 'Arg-list-prime'):
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            self.build_tree_and_return_usage(node, 'Arg-list-prime', self.arg_list_prime)
            return True
        else:
            return self.non_terminal_panic_mode('Arg-list', node)

            # self.arg_list()

    def arg_list_prime(self, node):
        if self.char == ',':
            self.build_tree_for_terminals(node, ',')
            self.build_tree_and_return_usage(node, 'Expression', self.expression)
            self.build_tree_and_return_usage(node, 'Arg-list-prime', self.arg_list_prime)
            return True
        else:
            return self.non_terminal_panic_mode('Arg-list-prime', node)

            # self.arg_list_prime()
