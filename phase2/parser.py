import json

from phase1.scanner import Scanner


def get_pure_token(token):
    token = token[1:]
    token = token[:-1]
    token = token.split(', ')
    # print(token)
    return token


class Parser:

    scanner = None
    data = None

    def __init__(self, scanner_location, predictset_location):
        self.scanner = Scanner(scanner_location)
        with open(predictset_location) as f:
            self.data = json.load(f)

    def parse(self):
        while True:
            lookahead = self.scanner.get_next_token()
            if lookahead == '$':
                break
            self.parse_token(lookahead)

    def parse_token(self, lookahead):
        token = get_pure_token(lookahead)
        # predict_set = json.loads(first[])
        # if token in
        # pass
