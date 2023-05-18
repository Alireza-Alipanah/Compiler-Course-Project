from scanner import Scanner
from utils.scanneroutput import *

if __name__ == '__main__':
    input_file_path = "./input.txt"
    token_file_path = "./tokens.txt"
    lexical_error_file_path = "./lexical_errors.txt"
    symbol_table_file_path = "./symbol_table.txt"

    scanner = Scanner(input_file_path)

    while scanner.get_next_token() != '$':
        pass

    write_tokens(token_file_path, scanner.tokens)
    write_lexical_errors(lexical_error_file_path, scanner.error_messages)
    write_symbol_table(symbol_table_file_path, scanner.symbol_table)
