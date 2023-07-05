class CodeGen:
    symbol_table = []
    ss = []
    program_block = []
    program_block_counter = 0
    lookahead = None
    temp_addr = 500

    def __init__(self):
        pass

    def choose_action(self, action, lookahead):
        self.lookahead = lookahead
        if action == 'pid':
            self.pid()
        elif action == 'ptype':
            self.ptype()
        elif action == 'var_dec':
            self.var_declaration()
        elif action == 'array_dec':
            self.array_dec()
        elif action == 'initialize':
            self.initialize()
        elif action == 'first_jp':
            self.first_jp()
        elif action == 'break_jump':
            self.break_jump()
        elif action == 'save':
            self.save()
        elif action == 'jp_save':
            self.jp_save()
        elif action == 'jpf_save':
            self.jpf_save()
        elif action == 'jp_until':
            self.jp_until()
        elif action == 'until':
            self.until()
        elif action == 'label':
            self.label()

    def pid(self):
        if self.get_lk_char() != 'output':  # and self.get_char() != 'main'
            self.ss.append(self.lookahead)

    def ptype(self):
        if self.get_lk_char() != 'output':  # and self.get_char() != 'main'
            self.ss.append(self.lookahead)

    def initialize(self):
        self.code_gen_two_arg('ASSIGN', '#4', '0')

    def first_jp(self):
        self.code_gen_one_arg('JP', self.program_block_counter + 1)

    def var_declaration(self):
        var = self.ss.pop()
        self.set_type_of_element(self, var[0][1], var[0][0])
        self.set_temp(self,  var[0][1])
        self.code_gen_two_arg('ASSIGN', '#0', self.temp_addr)
        #semantic_stack.append(identifier)  # for semantic check
        self.update_temp_addr(1)



    def array_dec(self):
        size_of_array = int(self.get_lk_char())
        self.update_temp_addr(size_of_array)
        pass

    def break_jump(self):
        self.code_gen_one_arg('JP', self.ss[-2])

    def save(self):
        self.ss.append(self.program_block_counter)
        self.program_block_counter += 1

    def jpf_save(self):
        i = self.ss.pop()
        self.manual_code_gen_two_arg('JPF', self.ss.pop, self.program_block_counter + 1, i)
        # save()
        self.ss.append(self.program_block_counter)
        self.program_block_counter += 1

    def jp_save(self):
        self.manual_code_gen_one_arg('JP', self.program_block_counter, self.ss.pop())
        self.ss.pop()

    def jp_until(self):
        self.code_gen_one_arg('JP', self.program_block_counter + 2)
        # save()
        self.ss.append(self.program_block_counter)
        self.program_block_counter += 1
        # label()
        self.ss.append(self.program_block_counter)

    def until(self):
        self.code_gen_two_arg('JPF', self.ss.pop(), self.ss.pop())
        self.manual_code_gen_one_arg('JP', self.program_block_counter, self.ss.pop())

    def label(self):
        self.ss.append(self.program_block_counter)

    def get_lk_char(self):
        return self.lookahead[0][1]

    def get_lk_type(self):
        return self.lookahead[0][0]

    def update_temp_addr(self, offset):
        self.temp_addr = self.temp_addr + offset * 4

    def set_type_of_element(self, lex, t):
        for idx in self.symbol_table:
            if idx.lexeme == lex:
                idx.type_of_var = t

    def set_temp(self, var):
        for idx in self.symbol_table:
            if idx.lexeme == var:
                idx.address = self.temp_addr

    def code_gen_one_arg(self, action, a):
        block = []
        block[0] = action
        block[1] = a
        block[2] = '   '
        block[3] = '   '
        self.program_block[self.program_block_counter] = block
        self.program_block_counter = self.program_block_counter + 1

    def manual_code_gen_one_arg(self, action, a, addr):
        block = []
        block[0] = action
        block[1] = a
        block[2] = '   '
        block[3] = '   '
        self.program_block[addr] = block

    def code_gen_two_arg(self, action, a, b):
        block = []
        block[0] = action
        block[1] = a
        block[2] = b
        block[3] = '   '
        self.program_block[self.program_block_counter] = block
        self.program_block_counter = self.program_block_counter + 1

    def manual_code_gen_two_arg(self, action, a, b, addr):
        block = []
        block[0] = action
        block[1] = a
        block[2] = b
        block[3] = '   '
        self.program_block[addr] = block

    def code_gen_three_arg(self, action, a, b, c):
        block = []
        block[0] = action
        block[1] = a
        block[2] = b
        block[3] = c
        self.program_block[self.program_block_counter] = block
        self.program_block_counter = self.program_block_counter + 1
