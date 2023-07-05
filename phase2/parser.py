import json
from anytree import Node, RenderTree

from phase1.scanner import Scanner
from phase1.utils.characterchecker import keywords_set
from phase3.codegen import CodeGen
from phase3.element import Element

class Parser:
    scanner = None
    codegen = None
    data = None
    line_no = 0
    lookahead = []
    token = None
    char = None
    error_messages = dict()
    symbols = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<', '/', '*', '=', '=='}
    program_node = None
    reached_eof = False
    early_stop = False

    def __init__(self, scanner_location, predictset_location):
        self.scanner = Scanner(scanner_location)
        self.codegen = CodeGen()
        with open(predictset_location) as f:
            self.data = json.load(f)

    def get_error_messages(self):
        if len(self.error_messages) == 0:
            return 'There is no syntax error.'
        res = []
        for key in sorted(list(self.error_messages.keys())):
            for i in self.error_messages[key]:
                res.append('#' + str(key) + ' : syntax error, ' + i)
        return '\n'.join(res)

    def parse(self):
        while self.lookahead != '$':
            self.lookahead = self.scanner.get_next_token()
            if self.lookahead == '$':
                break
            if self.lookahead is not None:
                self.set_token(self.lookahead)
                self.set_char(self.lookahead)
                self.set_line_no(self.lookahead)
                if self.token == 'KEYWORD' or self.token == 'ID':
                    self.codegen.symbol_table.append(Element(self.char, self.token, self.line_no))
                # self.program_node = Node('Program')
                self.program_node = self.program()
                # if not f:
                #     self.program_node = None
        # if len(self.error_messages) == 1:
        #     self.error_messages = {}
        # end_node = Node('$', self.program_node)
        if not self.early_stop:
            Node('$', self.program_node)
        # print('errors:::::')
        # print(self.error_messages)
        output_string = ''
        for pre, fill, node in RenderTree(self.program_node):
            output_string += "%s%s\n" % (pre, node.name)
        output_string = output_string[:-1]
        with open('./parse_tree.txt', 'w', encoding="utf-8") as f:
            f.write(output_string)

        output_string2 = self.get_error_messages()
        with open('./syntax_errors.txt', 'w', encoding="utf-8") as f:
            f.write(output_string2)
        print(self.codegen.symbol_table)

    def get_next(self):
        self.lookahead = self.scanner.get_next_token()
        while self.lookahead is None:
            self.lookahead = self.scanner.get_next_token()
        # print(self.lookahead)
        self.set_token(self.lookahead)
        self.set_char(self.lookahead)
        self.set_line_no(self.lookahead)
        if self.token == 'KEYWORD' or self.token == 'ID':
            self.codegen.symbol_table.append(self.codegen.symbol_table.append(Element(self.char, self.token, self.line_no)))

    def set_char(self, lk):
        if lk != '$':
            self.char = lk[0][1]
        else:
            self.char = '$'

    def set_line_no(self, lk):
        # if lk != '$':
        #     self.line_no = lk[1]
        # else:
        #     self.line_no = 0  # special case
        self.line_no = self.scanner.line_no

    def set_token(self, lk):
        if lk != '$':
            self.token = lk[0][0]
        else:
            self.token = '$'

    def missing_terminal_error_message(self, terminal):
        return 'missing ' + terminal

    def illegal_terminal_error_message(self, terminal):
        return 'illegal ' + terminal

    def match(self, terminal):
        if self.lookahead == '$':
            if self.reached_eof:
                return None
            self.add_error_message(self.unexpected_eof())
            self.reached_eof = True
            return None
            # todo what to return?
        self.early_stop = True
        if self.is_keyword(self.char) or self.is_symbol(self.char):
            if self.char == terminal:
                # print(terminal)
                # # build tree
                t = self.token_node()
                self.get_next()
                self.early_stop = False
                return t
            else:
                self.add_error_message(self.missing_terminal_error_message(terminal))
        else:
            if self.token == terminal:
                # print(terminal)
                # build tree
                t = self.token_node()
                self.get_next()
                self.early_stop = False
                return t
            else:
                self.add_error_message(self.missing_terminal_error_message(terminal))

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

    def missing_error_message(self, nt):
        if nt == 'Params' or nt == 'Declaration-prime':
            return 'missing ' + nt
        elif self.is_keyword(self.char) or self.is_symbol(self.char):
            return 'missing ' + self.char
        else:
            return 'missing ' + self.token

    def unexpected_eof(self):
        ln = self.line_no
        self.line_no = -1
        while ln != self.line_no:
            self.get_next()
            ln = self.line_no
        self.line_no = ln
        return 'Unexpected EOF'

    def non_terminal_panic_mode(self, non_terminal):
        # if self.check_char_in_follow(non_terminal):
        #     if self.check_epsilon_in_first(non_terminal):
        #         self.epsilon_in_tree(node)
        #         return True
        #     else:
        #         self.add_error_message(self.missing_error_message())
        #         return False  # No recursion
        # else:
        #     self.add_error_message(self.illegal_error_message())
        #     self.get_next()
        #     return False  # Recursion

        # if self.check_char_in_follow(non_terminal) and self.check_epsilon_in_first(non_terminal):
        #     self.add_error_message(self.missing_error_message())
        #     return True
        # else:
        #     self.add_error_message(self.illegal_error_message())
        #     self.get_next()
        #     return False
        if self.lookahead == '$':
            if self.reached_eof:
                return False
            if self.early_stop:
                self.add_error_message(self.unexpected_eof())
            self.reached_eof = True
            return False
        recurs = self.check_epsilon_in_first(non_terminal)
        self.early_stop = True
        if self.check_char_in_follow(non_terminal):
            self.early_stop = False
            if not recurs:
                self.add_error_message(self.missing_error_message(non_terminal))
            return False
        else:
            self.add_error_message(self.illegal_error_message())
            self.get_next()
            return recurs

    def epsilon_in_tree(self, parent):
        # child = Node('epsilon', parent)
        Node('epsilon', parent)

    def token_node(self):
        return Node('(' + self.token + ', ' + self.char + ')')

    def non_terminal_node(self, parent, name):
        Node(name, parent)

    def filter_none(self, ls):
        return list(filter(lambda item: item is not None, ls))

    # def build_tree_and_return_usage(self, parent, child_name, function):
    #     child = Node(child_name, parent)
    #     if not self.apply_function(function, child):
    #         child = None
    #         return False
    #     return True
    #
    # def build_tree_for_terminals(self, parent, match_parameter):
    #     child = Node('(' + self.token + ', ' + self.char + ')', parent)
    #     if not self.apply_function(self.match, match_parameter):
    #         child = None
    #         return False
    #     return True

    def program(self):
        if self.check_char_in_first('Declaration-list') or self.check_all2_go_to_epsilon('Program', 'Declaration-list'):
            return Node('Program', children=self.filter_none([self.codegen.choose_action('initialize', self.lookahead)
                                                                 , self.declaration_list()]))
        else:
            self.non_terminal_panic_mode('Program')
            return Node('')

    def declaration_list(self):
        if self.check_char_in_first('Declaration') or self.check_for_second_scenario('Declaration', 'Declaration-list') \
                or self.check_all2_go_to_epsilon('Declaration', 'Declaration-list'):
            return Node('Declaration-list', children=self.filter_none([
                self.declaration(),
                self.declaration_list(),
            ]))
        else:
            if self.non_terminal_panic_mode('Declaration-list'):
                return self.declaration_list()
            else:
                if not self.early_stop:
                    return Node('Declaration-list', children=self.filter_none([Node('epsilon')]))

    def declaration(self):
        if self.check_char_in_first('Declaration-initial') \
                or self.check_all3_go_to_epsilon('Declaration-initial', 'Declaration-prime', 'Declaration-prime'):
            return Node('Declaration', children=self.filter_none([
                self.declaration_initial(),
                self.declaration_prime()]))
        else:
            self.non_terminal_panic_mode('Declaration')

    def declaration_initial(self):
        if self.check_char_in_first('Type-specifier'):
            return Node('Declaration-initial', children=self.filter_none(
                [self.type_specifier(),
                 self.codegen.choose_action('pid', self.lookahead),
                 self.match('ID')]
            ))
        else:
            self.non_terminal_panic_mode('Declaration-initial')

    def declaration_prime(self):
        if self.check_char_in_first('Fun-declaration-prime') \
                or self.check_all2_go_to_epsilon('Fun-declaration-prime', 'Declaration-prime'):
            return Node('Declaration-prime',
                        children=self.filter_none([self.codegen.choose_action('first_jp', self.lookahead),
                                                   self.fun_declaration_prime()]))
        elif self.check_char_in_first('Var-declaration-prime') \
                or self.check_all2_go_to_epsilon('Var-declaration-prime', 'Declaration-prime'):
            return Node('Declaration-prime', children=self.filter_none([self.var_declaration_prime()]))
        else:
            self.non_terminal_panic_mode('Declaration-prime')
            # self.declaration_prime()

    def var_declaration_prime(self):
        if self.char == ';':
            return Node('Var-declaration-prime', children=self.filter_none([self.codegen.choose_action('var_dec',self.lookahead),
                                                                            self.match(';')]))
        elif self.char == '[':
            return Node('Var-declaration-prime', children=self.filter_none([
                self.match('['),
                self.codegen.choose_action('array_dec', self.lookahead),
                self.match('NUM'),
                self.match(']'),
                self.match(';')
            ]))
        else:
            self.non_terminal_panic_mode('Var-declaration-prime')

            # self.var_declaration_prime()

    def fun_declaration_prime(self):
        if self.char == '(':
            a, b = self.match('('), self.params()
            if b is None:
                self.add_error_message(self.missing_error_message('Params'))
            return Node('Fun-declaration-prime',
                        children=self.filter_none(
                            [a, b,
                             self.match(')'),
                             self.compound_stmt()]
                        ))
        else:
            self.non_terminal_panic_mode('Fun-declaration-prime')

            # self.fun_declaration_prime()

    def type_specifier(self):
        if self.char == 'int':
            return Node('Type-specifier', children=self.filter_none([self.codegen.choose_action('ptype', self.lookahead)
                                                                        , self.match('int')]))
        elif self.char == 'void':
            return Node('Type-specifier', children=self.filter_none([self.codegen.choose_action('ptype', self.lookahead)
                                                                        , self.match('void')]))
        else:
            self.non_terminal_panic_mode('Type-specifier')

            # self.type_specifier()

    def params(self):
        if self.char == 'int':
            return Node('Params',
                        children=self.filter_none(
                            [self.codegen.choose_action('ptype', self.lookahead),
                             self.match('int'),
                             self.match('ID'),
                             self.param_prime(),
                             self.codegen.choose_action('var_dec', self.lookahead),
                             self.param_list()]
                        ))
        elif self.char == 'void':
            return Node('Params', children=self.filter_none([self.match('void')]))
        else:
            self.non_terminal_panic_mode('Params')

            # self.params()

    def param_list(self):
        if self.char == ',':
            return Node('Param-list',
                        children=self.filter_none(
                            [self.match(','),
                             self.param(),
                             self.param_list()]
                        ))
        else:
            if self.non_terminal_panic_mode('Param-list'):
                return self.param_list()
            else:
                if not self.early_stop:
                    return Node('Param-list',
                                children=self.filter_none(
                                    [Node('epsilon')]))

            # self.param_list()

    def param(self):
        if self.check_char_in_first('Declaration-initial') \
                or self.check_all3_go_to_epsilon('Param', 'Declaration-initial', 'Param-prime'):
            return Node('Param',
                        children=self.filter_none(
                            [self.declaration_initial(),
                             self.param_prime()]
                        ))
        else:
            self.non_terminal_panic_mode('Param')

            # self.param()

    def param_prime(self):
        if self.char == '[':
            return Node('Param-prime',
                        children=self.filter_none(
                            [self.match('['),
                             self.match(']')]
                        ))
        else:
            if self.non_terminal_panic_mode('Param-prime'):
                return self.param_prime()
            else:
                if not self.early_stop:
                    return Node('Param-prime',
                                children=self.filter_none(
                                    [Node('epsilon')]))
            # self.param_prime(node)

    def compound_stmt(self):
        if self.char == '{':
            return Node('Compound-stmt',
                        children=self.filter_none(
                            [
                                self.match('{'),
                                self.declaration_list(),
                                self.statement_list(),
                                self.match('}')]
                        ))
        else:
            self.non_terminal_panic_mode('Compound-stmt')

            # self.compound_stmt()

    def statement_list(self):
        if self.check_char_in_first('Statement') or self.check_all2_go_to_epsilon('Statement', 'Statement-list'):
            return Node('Statement-list',
                        children=self.filter_none(
                            [self.statement(),
                             self.statement_list()]
                        ))
        else:
            if self.non_terminal_panic_mode('Statement-list'):
                return self.statement_list()
            else:
                if not self.early_stop:
                    return Node('Statement-list',
                                children=self.filter_none(
                                    [Node('epsilon')]))

            # self.statement_list()

    def statement(self):
        if self.check_char_in_first('Expression-stmt') or self.check_all2_go_to_epsilon('Statement', 'Expression-stmt'):
            return Node('Statement', children=self.filter_none([self.expression_stmt()]))
        elif self.check_char_in_first('Compound-stmt') or self.check_all2_go_to_epsilon('Statement', 'Compound-stmt'):
            return Node('Statement', children=self.filter_none([self.compound_stmt()]))
        elif self.check_char_in_first('Selection-stmt') or self.check_all2_go_to_epsilon('Statement', 'Selection-stmt'):
            return Node('Statement', children=self.filter_none([self.selection_stmt()]))
        elif self.check_char_in_first('Iteration-stmt') or self.check_all2_go_to_epsilon('Statement', 'Iteration-stmt'):
            return Node('Statement', children=self.filter_none([self.iteration_stmt()]))
        elif self.check_char_in_first('Return-stmt') or self.check_all2_go_to_epsilon('Statement', 'Return-stmt'):
            return Node('Statement', children=self.filter_none([self.return_stmt()]))
        else:
            self.non_terminal_panic_mode('Statement')

            # self.statement()

    def expression_stmt(self):
        if self.check_char_in_first('Expression'):
            return Node('Expression-stmt', children=self.filter_none([self.expression(), self.match(';')]))
        elif self.char == 'break':
            return Node('Expression-stmt', children=self.filter_none([self.match('break'),
                                                                      self.codegen.choose_action('break_jump',
                                                                                                 self.lookahead)
                                                                         , self.match(';')]))
        elif self.char == ';':
            return Node('Expression-stmt', children=self.filter_none([self.match(';')]))
        else:
            self.non_terminal_panic_mode('Expression-stmt')

            # self.expression_stmt()

    def selection_stmt(self):
        if self.char == 'if':
            return Node('Selection-stmt', children=self.filter_none([
                self.match('if'),
                self.match('('),
                self.expression(),
                self.match(')'),
                self.codegen.choose_action('save', self.lookahead),
                self.statement(),
                self.codegen.choose_action('jpf_save', self.lookahead),
                self.match('else'),
                self.statement(),
                self.codegen.choose_action('jp_save', self.lookahead)
            ]))
        else:
            self.non_terminal_panic_mode('Selection-stmt')

            # self.selection_stmt()

    def iteration_stmt(self):
        if self.char == 'repeat':
            return Node('Iteration-stmt',
                        children=self.filter_none([
                            self.match('repeat'),
                            self.codegen.choose_action('jp_until', self.lookahead),
                            self.statement(),
                            self.match('until'),
                            self.match('('),
                            self.expression(),
                            self.codegen.choose_action('until', self.lookahead),
                            self.match(')')
                        ]))
        else:
            self.non_terminal_panic_mode('Iteration-stmt')

            # self.iteration_stmt()

    def return_stmt(self):
        if self.char == 'return':
            return Node('Return-stmt', children=self.filter_none([
                self.match('return'),
                self.return_stmt_prime()
            ]))
        else:
            self.non_terminal_panic_mode('Return-stmt')

            # self.return_stmt()

    def return_stmt_prime(self):
        if self.char == ';':
            return Node('Return-stmt-prime', children=self.filter_none([
                self.match(';')
            ]))
        elif self.check_char_in_first('Expression'):
            return Node('Return-stmt-prime', children=self.filter_none([
                self.expression(),
                self.match(';')
            ]))
        else:
            self.non_terminal_panic_mode('Return-stmt-prime')

            # self.return_stmt_prime()

    def expression(self):
        if self.check_char_in_first('Simple-expression-zegond') \
                or self.check_all2_go_to_epsilon('Simple-expression-zegond', 'Expression'):
            return Node('Expression', children=self.filter_none([
                self.simple_expression_zegond()
            ]))
        elif self.token == 'ID':  # token no char
            return Node('Expression', children=self.filter_none([
                self.codegen.choose_action('pid', self.lookahead),
                self.match('ID'),
                self.b()
            ]))
        else:
            self.non_terminal_panic_mode('Expression')

            # self.expression()

    def b(self):
        if self.char == '=':
            return Node('B', children=self.filter_none([
                self.match('='),
                self.expression()
            ]))
        elif self.char == '[':
            return Node('B', children=self.filter_none([
                self.match('['),
                self.expression(),
                self.match(']'),
                self.h()
            ]))
        elif self.check_char_in_first('Simple-expression-prime') \
                or self.check_all2_go_to_epsilon('B', 'Simple-expression-prime'):
            return Node('B', children=self.filter_none([
                self.simple_expression_prime()
            ]))
        else:
            self.non_terminal_panic_mode('B')

            # self.b()

    def h(self):
        if self.char == '=':
            return Node('H', children=self.filter_none([
                self.match('='),
                self.expression()
            ]))
        elif self.check_char_in_first('G') or self.check_for_second_scenario('G', 'D') \
                or (self.check_all3_go_to_epsilon('H', 'G', 'D') and self.check_epsilon_in_first('C')):
            return Node('H', children=self.filter_none([
                self.g(),
                self.d(),
                self.c()
            ]))
        else:
            self.non_terminal_panic_mode('H')

            # self.h()

    def simple_expression_zegond(self):
        if self.check_char_in_first('Additive-expression-zegond') \
                or self.check_all3_go_to_epsilon('Simple-expression-zegond', 'Additive-expression-zegond', 'C'):
            return Node('Simple-expression-zegond', children=self.filter_none([
                self.additive_expression_zegond(),
                self.c()
            ]))
        else:
            self.non_terminal_panic_mode('Simple-expression-zegond')

            # self.simple_expression_zegond()

    def simple_expression_prime(self):
        if self.check_char_in_first('Additive-expression-prime') or \
                self.check_for_second_scenario('Additive-expression-prime', 'C') \
                or self.check_all3_go_to_epsilon('Simple-expression-prime', 'Additive-expression-prime', 'C'):
            return Node('Simple-expression-prime', children=self.filter_none([
                self.additive_expression_prime(),
                self.c()
            ]))
        else:
            self.non_terminal_panic_mode('Simple-expression-prime')

            # self.simple_expression_prime()

    def c(self):
        if self.check_char_in_first('Relop') or self.check_all3_go_to_epsilon('C', 'Relop', 'Additive-expression'):
            return Node('C', children=self.filter_none([
                self.relop(),
                self.additive_expression()
            ]))
            # if not (True )
            #     child = ('epsilon' , node)
            # return True
        else:
            if self.non_terminal_panic_mode('C'):
                return self.c()
            else:
                if not self.early_stop:
                    return Node('C', children=self.filter_none([Node('epsilon')]))

            # self.c()

    def relop(self):
        if self.char == '<':
            return Node('Relop', children=self.filter_none([self.match('<')]))
        elif self.char == '==':
            return Node('Relop', children=self.filter_none([self.match('==')]))
        else:
            self.non_terminal_panic_mode('Relop')

            # self.relop()

    def additive_expression(self):
        if self.check_char_in_first('Term') or self.check_all3_go_to_epsilon('Additive-expression', 'Term', 'D'):
            return Node('Additive-expression', children=self.filter_none([
                self.term(),
                self.d()
            ]))
        else:
            self.non_terminal_panic_mode('Additive-expression')

            # self.additive_expression()

    def additive_expression_prime(self):
        if self.check_char_in_first('Term-prime') or self.check_for_second_scenario('Term-prime', 'D') \
                or self.check_all3_go_to_epsilon('Additive-expression-prime', 'Term-prime', 'D'):
            return Node('Additive-expression-prime', children=self.filter_none([
                self.term_prime(),
                self.d()
            ]))
        else:
            self.non_terminal_panic_mode('Additive-expression-prime')

            # self.additive_expression_prime()

    def additive_expression_zegond(self):
        if self.check_char_in_first('Term-zegond') \
                or self.check_all3_go_to_epsilon('Additive-expression-zegond', 'Term-zegond', 'D'):
            return Node('Additive-expression-zegond', children=self.filter_none([
                self.term_zegond(),
                self.d()
            ]))
        else:
            self.non_terminal_panic_mode('Additive-expression-zegond')

            # self.additive_expression_zegond()

    def d(self):
        if self.check_char_in_first('Addop') or self.check_all3_go_to_epsilon('Addop', 'Term', 'D'):
            return Node('D', children=self.filter_none([
                self.addop(),
                self.term(),
                self.d()
            ]))
        else:
            if self.non_terminal_panic_mode('D'):
                return self.d()
            else:
                if not self.early_stop:
                    return Node('D', children=self.filter_none([Node('epsilon')]))

            # self.d()

    def addop(self):
        if self.char == '+':
            return Node('Addop', children=self.filter_none([self.match('+')]))
        elif self.char == '-':
            return Node('Addop', children=self.filter_none([self.match('-')]))
        else:
            self.non_terminal_panic_mode('Addop')

            # self.addop()

    def term(self):
        if self.check_char_in_first('Factor') or self.check_all3_go_to_epsilon('Factor', 'G', 'Term'):
            return Node('Term', children=self.filter_none([
                self.factor(),
                self.g()
            ]))
        else:
            self.non_terminal_panic_mode('Term')

            # self.term()

    def term_prime(self):
        if self.check_char_in_first('Factor-prime') or self.check_for_second_scenario('Factor-prime', 'G') \
                or self.check_all3_go_to_epsilon('Term-prime', 'Factor-prime', 'G'):
            return Node('Term-prime', children=self.filter_none([
                self.factor_prime(),
                self.g()
            ]))
        else:
            self.non_terminal_panic_mode('Term-prime')

            # self.term_prime()

    def term_zegond(self):
        if self.check_char_in_first('Factor-zegond') \
                or self.check_all3_go_to_epsilon('Term-zegond', 'G', 'Factor-zegond'):
            return Node('Term-zegond', children=self.filter_none([
                self.factor_zegond(),
                self.g()
            ]))
        else:
            self.non_terminal_panic_mode('Term-zegond')

            # self.term_zegond()

    def g(self):
        if self.char == '*':
            return Node('G', children=self.filter_none([
                self.match('*'),
                self.factor(),
                self.g()
            ]))
        else:
            if self.non_terminal_panic_mode('G'):
                return self.g()
            else:
                if not self.early_stop:
                    return Node('G', children=self.filter_none([Node('epsilon')]))

            # self.g()

    def factor(self):
        if self.char == '(':
            return Node('Factor', children=self.filter_none([
                self.match('('),
                self.expression(),
                self.match(')')
            ]))
        elif self.token == 'ID':  # token not char
            return Node('Factor', children=self.filter_none([
                self.match('ID'),
                self.var_call_prime()
            ]))
        elif self.token == 'NUM':  # token not char
            return Node('Factor', children=self.filter_none([
                self.match('NUM')
            ]))
        else:
            self.non_terminal_panic_mode('Factor')

            # self.factor()

    def var_call_prime(self):
        if self.char == '(':
            return Node('Var-call-prime', children=self.filter_none([
                self.match('('),
                self.args(),
                self.match(')')
            ]))
        elif self.check_char_in_first('Var-prime') or self.check_all2_go_to_epsilon('Var-call-prime', 'Var-prime'):
            return Node('Var-call-prime', children=self.filter_none([
                self.var_prime()
            ]))
        else:
            self.non_terminal_panic_mode('Var-call-prime')

            # self.var_call_prime()

    def var_prime(self):
        if self.char == '[':
            return Node('Var-prime', children=self.filter_none([
                self.match('['),
                self.expression(),
                self.match(']')
            ]))
        else:
            if self.non_terminal_panic_mode('Var-prime'):
                return self.var_prime()
            else:
                if not self.early_stop:
                    return Node('Var-prime', children=self.filter_none([Node('epsilon')]))

            # self.var_prime()

    def factor_prime(self):
        if self.char == '(':
            return Node('Factor-prime', children=self.filter_none([
                self.match('('),
                self.args(),
                self.match(')')
            ]))
        else:
            if self.non_terminal_panic_mode('Factor-prime'):
                return self.factor_prime()
            else:
                if not self.early_stop:
                    return Node('Factor-prime', children=self.filter_none([Node('epsilon')]))

            # self.factor_prime()

    def factor_zegond(self):
        if self.char == '(':
            return Node('Factor-zegond', children=self.filter_none([
                self.match('('),
                self.expression(),
                self.match(')')
            ]))
        elif self.token == 'NUM':  # token not char
            return Node('Factor-zegond', children=self.filter_none([
                self.match('NUM')
            ]))
        else:
            self.non_terminal_panic_mode('Factor-zegond')

            # self.factor_zegond()

    def args(self):
        if self.check_char_in_first('Arg-list') or self.check_all2_go_to_epsilon('Args', 'Arg-list'):
            return Node('Args', children=self.filter_none([
                self.arg_list()
            ]))
        else:
            if self.non_terminal_panic_mode('Args'):
                return self.args()
            else:
                if not self.early_stop:
                    return Node('Args', children=self.filter_none([Node('epsilon')]))

            # self.args()

    def arg_list(self):
        if self.check_char_in_first('Expression') \
                or self.check_all3_go_to_epsilon('Arg-list', 'Expression', 'Arg-list-prime'):
            return Node('Arg-list', children=self.filter_none([
                self.expression(),
                self.arg_list_prime()
            ]))
        else:
            self.non_terminal_panic_mode('Arg-list')

            # self.arg_list()

    def arg_list_prime(self):
        if self.char == ',':
            return Node('Arg-list-prime', children=self.filter_none([
                self.match(','),
                self.expression(),
                self.arg_list_prime()
            ]))
        else:
            if self.non_terminal_panic_mode('Arg-list-prime'):
                return self.arg_list_prime()
            else:
                if not self.early_stop:
                    return Node('Arg-list-prime', children=self.filter_none([Node('epsilon')]))

            # self.arg_list_prime()
