class Parser:

    scanner = None

    def __init__(self, scanner):
        self.scanner = scanner

    def parse(self):
        while True:
            lookahead = self.scanner.get_next_token()
            if lookahead == '$':
                break
            self.parse_token(lookahead)

    def parse_token(self, lookahead):
        # todo: write and call individual functions
        pass
