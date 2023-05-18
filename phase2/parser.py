import json

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

    def __init__(self, scanner_location, predictset_location):

        self.scanner = Scanner(scanner_location)
        with open(predictset_location) as f:
            self.data = json.load(f)

    def parse(self):
        while True:
            self.lookahead = self.scanner.get_next_token()
            if self.lookahead == '$':
                print(self.error_messages)
                break
            if self.lookahead is not None:
                self.lookahead = str(self.lookahead)
                self.set_token(self.lookahead)
                self.set_char(self.lookahead)
                self.set_line_no(self.lookahead)
                self.program()

    def get_next(self):
        self.lookahead = self.scanner.get_next_token()
        while self.lookahead is None:
            self.lookahead = self.scanner.get_next_token()
        self.lookahead = str(self.lookahead)
        self.set_token(self.lookahead)
        self.set_char(self.lookahead)
        self.set_line_no(self.lookahead)

    def set_char(self, lk):
        lk = lk[3:]
        lk = lk.split(', ')
        lk = lk[1]
        lk = lk[:-2]
        self.char = lk[1:]
        print(self.char)

    def set_line_no(self, lk):
        lk = lk[3:]
        lk = lk[:-1]
        lk = lk.split(', ')
        self.line_no = int(lk[2])

    def set_token(self, lk):
        lk = lk[3:]
        lk = lk.split(', ')
        lk = lk[0]
        lk = lk[:-1]
        self.token = lk

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
        else: return 'illegal ' + self.token

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
        pass

    def compound_stmt(self):
        pass

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
