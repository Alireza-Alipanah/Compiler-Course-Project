class Element:  # used for elements of symbol table
    lexeme = None
    type_of_element = None
    type_of_var = None
    number_of_args = None
    line_no = 0
    address = 0

    def __init__(self, lexeme, type_of_element, line_no):
        self.lexeme = lexeme
        self.type_of_element = type_of_element
        self.line_no = line_no
        self.address = 0
        self.type_of_var = ""
        self.numberOfArgument = 0
