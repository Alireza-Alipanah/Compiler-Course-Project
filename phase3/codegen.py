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
        elif action == 'push_assign':
            self.push_assign()
        elif action == 'assign':
            self.assign()
        elif action == 'arr_acc':
            pass # todo
        elif action == 'pushop':
            self.pushop()
        elif action == 'cmp':
            self.cmp()
        elif action == 'add_sub':
            self.add_sub()
        elif action == 'mul':
            self.mul()


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
        self.set_type_of_element(var[0][1], var[0][0])
        self.set_temp(var[0][1])
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

    def push_assign(self):
        self.ss.append(self.lookahead)

    def assign(self):
        value = self.ss.pop()
        var = self.ss.pop()
        self.code_gen_two_arg('ASSIGN', value, var)

    def pushop(self):
        self.ss.append(self.lookahead)

    def cmp(self):
        value = self.ss.pop()
        op = self.ss.pop()
        value1 = self.ss.pop()
        tmp = self.temp_addr
        self.update_temp_addr(1)
        self.ss.append(tmp)
        op = op[0][1]
        if op == '==':
            self.code_gen_three_arg('EQ', value, value1, tmp)
        else:
            self.code_gen_three_arg('LT', value1, value, tmp)

    def add_sub(self):
        value = self.ss.pop()
        op = self.ss.pop()
        value1 = self.ss.pop()
        tmp = self.temp_addr
        self.update_temp_addr(1)
        self.ss.append(tmp)
        op = op[0][1]
        if op == '+':
            self.code_gen_three_arg('add', value, value1, tmp)
        else:
            self.code_gen_three_arg('LT', value, value1, tmp)

    def mul(self):
        value = self.ss.pop()
        value1 = self.ss.pop()
        tmp = self.temp_addr
        self.update_temp_addr(1)
        self.ss.append(tmp)
        self.code_gen_three_arg('mult', value, value1, tmp)

    def pnum(self):
        tmp = self.temp_addr
        self.update_temp_addr(1)
        value = self.get_lk_char()
        self.code_gen_two_arg('ASSIGN', '#' + value,tmp)

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
        block = [None] * 4
        block[0] = action
        block[1] = a
        block[2] = '   '
        block[3] = '   '
        #self.program_block[self.program_block_counter] = block
        self.program_block.append(block)
        self.program_block_counter = self.program_block_counter + 1

    def manual_code_gen_one_arg(self, action, a, addr):
        block = [None] * 4
        block[0] = action
        block[1] = a
        block[2] = '   '
        block[3] = '   '
        self.program_block[addr] = block

    def code_gen_two_arg(self, action, a, b):
        block = [None] * 4
        block[0] = action
        block[1] = a
        block[2] = b
        block[3] = '   '
        #self.program_block[self.program_block_counter] = block
        self.program_block.append(block)
        self.program_block_counter = self.program_block_counter + 1

    def manual_code_gen_two_arg(self, action, a, b, addr):
        block = [None] * 4
        block[0] = action
        block[1] = a
        block[2] = b
        block[3] = '   '
        self.program_block[addr] = block

    def code_gen_three_arg(self, action, a, b, c):
        block = [None] * 4
        block[0] = action
        block[1] = a
        block[2] = b
        block[3] = c
        #self.program_block[self.program_block_counter] = block
        self.program_block.append(block)
        self.program_block_counter = self.program_block_counter + 1
