class Stack:

    def __init__(self, codegen, end_addr):
        self.codegen = codegen
        self.end_addr = self.addr = end_addr

    def push(self, addr):
        self.codegen.code_gen_two_arg('ASSIGN', str(self.addr), addr)
        self.addr -= 4

    def push_value(self, val):
        self.codegen.code_gen_two_arg('ASSIGN', str(self.addr), '#' + str(val))
        self.addr -= 4

    def pop(self, addr):
        self.codegen.code_gen_two_arg('ASSIGN', addr, str(self.addr))
        self.addr += 4
