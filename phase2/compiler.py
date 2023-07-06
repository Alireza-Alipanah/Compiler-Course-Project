from phase2.parser import Parser


if __name__ == '__main__':
    i = 1
    input_file_path = "../Fixed_TestCases_3/TestCases/T8/input.txt"

    parser = Parser(input_file_path, './utils/predictset.json')
    parser.parse()
    result = ""
    # print(parser.error_messages)
    for i, item in enumerate(parser.codegen.program_block, start=0):
        trans = str.maketrans('', '', "'")
        print("{}\t{}".format(i,str(item).translate(trans).replace('[', '(').replace(']', ')') ))
        # print(str(item).translate(trans).replace('[', '(').replace(']', ')'))
    # print(parser.codegen.program_block)
