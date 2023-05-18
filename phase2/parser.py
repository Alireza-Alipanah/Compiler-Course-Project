def get_pure_token(token):
    token = token[1:]
    token = token[:-1]
    token = token.split(', ')
    print(token)
    return token


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
        token = get_pure_token(lookahead)


