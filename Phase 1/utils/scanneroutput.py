def tuple_to_string(tokens, i, index):
    if index == len(tokens) - 1:
        return '(' + ', '.join(i) + ') '
    return '(' + ', '.join(i) + ')'


def write_tokens(path, tokens: dict):
    with open(path, mode='w') as file_:
        file_.write(
            '\n'.join(
                [str(line_no) + '.\t' + ' '.join(
                    tuple_to_string(tokens[line_no], i, index) for index, i in enumerate(tokens[line_no])) for
                 line_no in
                 sorted(tokens.keys())]
            ) + '\n'
        )


def write_lexical_errors(path, errors: dict):
    with open(path, mode='w') as file_:
        if len(errors) > 0:
            file_.write(
                '\n'.join(
                    [str(line_no) + '.\t' + ' '.join(
                        tuple_to_string(errors[line_no], i, index) for index, i in enumerate(errors[line_no])) for
                     line_no in
                     sorted(errors.keys())]
                ) + '\n'
            )
        else:
            file_.write('There is no lexical error.')


def write_symbol_table(path, symbols: list):
    with open(path, mode='w') as symbols_file:
        symbols_file.write(
            '\n'.join(
                [str(line_no + 1) + '.\t' + symbols[line_no] for line_no in range(len(symbols))]
            )+ '\n'
        )
