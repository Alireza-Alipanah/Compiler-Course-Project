from phase2.parser import Parser


if __name__ == '__main__':
    input_file_path = "../tests/T08/input.txt"

    parser = Parser(input_file_path, './utils/predictset.json')
    parser.parse()
    print(parser.error_messages)
