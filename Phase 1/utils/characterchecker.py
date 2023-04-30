import re

digits = set([str(i) for i in range(0, 10)])
alphabets = set(list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"))
keywords = ['break', 'else', 'if', 'int', 'repeat', 'return', 'until', 'void']
keywords_set = set(keywords)
symbols = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<', '/', '*', '='}  # except '*' and '='


def is_digit(v):
    return v in digits


def is_alphabet(v):
    return v in alphabets


def is_keyword(v):
    return v in keywords_set


def is_symbol(v):
    return v in symbols


def is_whitespace(v):
    return re.match("^\\s$", v)


def id_state_other(v):
    return is_symbol(v) or is_whitespace(v) or is_symbol(v) or v == ''


def is_alphanum(v):
    return is_digit(v) or is_alphabet(v)


def assignment_state_other(v):
    return is_alphanum(v) or is_whitespace(v) or is_symbol(v) or v == ''


def comment_start_other(v):
    return is_alphanum(v) or is_whitespace(v) or is_symbol(v) or v == ''


def multiply_other(v):
    return is_alphanum(v) or is_whitespace(v) or is_symbol(v) or v == ''
