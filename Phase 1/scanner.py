from utils.inputgetter import InputGetter
from utils.characterchecker import *


class Scanner:
    input_getter = None
    tokens = dict()
    error_messages = dict()
    symbol_table = keywords.copy()
    line_no = 0

    def __init__(self, file_path):
        self.input_getter = InputGetter(file_path)

    def add_token(self, token, line_no):
        if line_no not in self.tokens:
            self.tokens[line_no] = []
        self.tokens[line_no].append(token)

    def add_error_message(self, error_message, line_no):
        if line_no not in self.error_messages:
            self.error_messages[line_no] = []
        self.error_messages[line_no].append(error_message)

    def get_next_token(self):
        self.input_getter.read_next_character()
        last_char = self.input_getter.get_last_character()
        self.line_no = self.input_getter.get_line_number()
        if is_digit(last_char):
            self.digits_state()
        elif is_alphabet(last_char):
            self.keyword_or_id_state()
        elif last_char == '=':
            self.equal_and_assign_states()
        elif last_char == '*':
            self.multiply_and_unmatched_comment_states()
        elif last_char == '/':
            self.comment_start()
        elif is_symbol(last_char):
            self.symbols_state()
        elif is_whitespace(last_char):
            self.whitespace_state()
        elif last_char == '':
            raise EOFError
        else:
            self.unknown_character()

    def digits_state(self):
        while is_digit(self.input_getter.get_last_character()):
            self.input_getter.read_next_character()
        if is_alphabet(self.input_getter.get_last_character()):
            self.add_error_message((self.input_getter.get_token_content(), "Invalid number"), self.line_no)
        else:
            self.input_getter.set_lookahead(True)
            self.add_token(("NUM", ''.join(self.input_getter.get_token_content())), self.line_no)

    def keyword_or_id_state(self):
        while is_alphanum(self.input_getter.get_last_character()):
            self.input_getter.read_next_character()
        else:
            if id_state_other(self.input_getter.get_last_character()):
                self.input_getter.set_lookahead(True)
                token_content = self.input_getter.get_token_content()
                token_ = "KEYWORD" if is_keyword(token_content) else "ID"
                if token_content not in self.symbol_table:
                    self.symbol_table.append(token_content)
                self.add_token((token_, token_content), self.line_no)
            else:
                self.add_error_message((self.input_getter.get_token_content(), "Invalid input"), self.line_no)

    def equal_and_assign_states(self):
        self.input_getter.read_next_character()
        if self.input_getter.get_last_character() != '=':
            if assignment_state_other(self.input_getter.get_last_character()):
                self.input_getter.set_lookahead(True)
            else:
                self.add_error_message((self.input_getter.get_token_content(), 'Invalid input'), self.line_no)
                return
        self.add_token(("SYMBOL", self.input_getter.get_token_content()), self.line_no)

    def multiply_and_unmatched_comment_states(self):
        self.input_getter.read_next_character()
        if self.input_getter.get_last_character() == '/':
            self.add_error_message((self.input_getter.get_token_content(), "Unmatched comment"), self.line_no)
        elif multiply_other(self.input_getter.get_last_character()):
            self.input_getter.set_lookahead(True)
            self.add_token(("SYMBOL", self.input_getter.get_token_content()), self.line_no)
        else:
            self.add_error_message((self.input_getter.get_token_content(), 'Invalid input'), self.line_no)

    def symbols_state(self):
        self.add_token(("SYMBOL", self.input_getter.get_token_content()), self.line_no)

    def comment_start(self):
        self.input_getter.read_next_character()
        if self.input_getter.get_last_character() != '*':
            if comment_start_other(self.input_getter.get_last_character()):
                self.input_getter.set_lookahead(True)
            self.add_error_message((self.input_getter.get_token_content(), 'Invalid input'), self.line_no)
        else:
            self.input_getter.read_next_character()
            self.comment_state(self.line_no)

    def comment_state(self, line_no):
        while self.input_getter.get_last_character() != '*' and self.input_getter.get_last_character() != '':
            self.input_getter.read_next_character()
        self.input_getter.read_next_character()
        if self.input_getter.get_last_character() == '':
            self.unclosed_comment(line_no)
        elif self.input_getter.get_last_character() != '/':
            self.comment_state(line_no)

    def unclosed_comment(self, line_no):
        t = self.input_getter.get_token_content()[:7] + '...'
        self.add_error_message((t, 'Unclosed comment'), line_no)

    def whitespace_state(self):
        while is_whitespace(self.input_getter.get_last_character()):
            self.input_getter.read_next_character()
        self.input_getter.set_lookahead(True)
        self.input_getter.get_token_content()

    def unknown_character(self):
        self.add_error_message((self.input_getter.get_token_content(), 'Invalid input'), self.line_no)
