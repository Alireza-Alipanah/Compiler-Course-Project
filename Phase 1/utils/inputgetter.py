class InputGetter:

    last_character = ''
    stored_characters = []
    line_number = 1
    lookahead = False
    file = None
    EOF_reached = False

    def __init__(self, file_path):
        self.file = open(file_path)

    def read_next_character(self):
        if self.EOF_reached and not self.lookahead:
            self.last_character = ''
        elif self.lookahead:
            self.lookahead = False
        else:
            self.last_character = self.file.read(1)
            if self.last_character == '':
                self.EOF_reached = True
            else:
                self.stored_characters.append(self.last_character)
            if self.last_character == '\n':
                self.line_number += 1
        return self.last_character

    def close_file(self):
        self.file.close()

    def set_lookahead(self, lookahead):
        self.lookahead = lookahead
        if lookahead and not self.EOF_reached:
            self.stored_characters = self.stored_characters[:-1]

    def empty_stored_characters(self):
        self.stored_characters.clear()

    def get_token_content(self):
        temp = ''.join(self.stored_characters)
        self.empty_stored_characters()
        if self.lookahead:
            self.stored_characters.append(self.last_character)
        return temp

    def get_line_number(self):
        return self.line_number

    def get_last_character(self):
        return self.last_character
