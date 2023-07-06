from phase2.parser import Parser


if __name__ == '__main__':
    i = 1
    input_file_path = f"/home/alireza/Desktop/Compiler_Course_Project/Fixed_TestCases_3/TestCases/T{i}/input.txt"

    parser = Parser(input_file_path, './utils/predictset.json')
    parser.parse()
    print(parser.error_messages)
    print(parser.codegen.program_block)
