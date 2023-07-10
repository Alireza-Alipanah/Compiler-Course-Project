from phase3.utils.stack import Stack

class CodeGen:
    symbol_table = dict()
    current_function = 'default_function'
    ss = []
    program_block = []
    program_block_counter = 0
    lookahead = None
    temp_addr = 500
    digits = set([str(i) for i in range(0, 10)])
    func_addr = dict()  # keep address of functions, so we know where to jump
    return_addr = 996
    returned_addr = 992
    num_of_params_of_functions = dict()
    collect_args = False
    collected_args = []
    previous_functions = []

    def __init__(self):
        self.program_stack = Stack(self, 1000000)

    def choose_action(self, action, lookahead):
        self.lookahead = lookahead
        # print(action)
        if action == 'pid':
            self.pid()
        elif action == 'ptype':
            self.ptype()
        elif action == 'pnum':
            self.pnum()
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
        elif action == 'arr_idx':
            self.array_idx()
        elif action == 'pushop':
            self.pushop()
        elif action == 'cmp':
            self.cmp()
        elif action == 'add_sub':
            self.add_sub()
        elif action == 'mul':
            self.mul()
        elif action == 'output':
            self.output()
        elif action == 'func_dec':
            self.func_dec()
        elif action == 'jp_back':
            self.jp_back()
        elif action == 'jp_to_func':
            self.jp_to_func()
        elif action == 'var_declaration_param':
            self.var_declaration_param()
        elif action == 'array_dec_param':
            self.array_dec_param()
        elif action == 'at_least_one_num_of_params':
            self.at_least_one_num_of_params()
        elif action == 'increase_num_of_params_by_one':
            self.increase_num_of_params_by_one()
        elif action == 'collect_args_flag':
            self.collect_args_flag()

    ################## phase 4
    def func_dec(self):
        name_of_function = self.ss.pop()
        self.previous_functions.append(self.current_function)
        self.current_function = name_of_function
        self.num_of_params_of_functions[name_of_function] = 0
        self.func_addr[name_of_function] = self.program_block_counter

    def jp_back(self):
        self.program_stack.pop(self.return_addr)
        self.code_gen_one_arg('JP', '@' + str(self.return_addr))

    def jp_to_func(self):
        name_of_function = self.ss.pop()
        addr_of_function = self.func_addr[name_of_function]
        self.program_stack.push_value(self.program_block_counter + 1)
        for i in self.collected_args:
            self.program_stack.push(self.get_var_char(i))
        self.current_function = name_of_function
        self.code_gen_one_arg('JP', addr_of_function)
        for i in reversed(range(self.num_of_params_of_functions[self.current_function])):
            self.program_stack.pop(self.symbol_table[name_of_function][i])

    def var_declaration_param(self):
        self.var_declaration()
        return
        var = self.ss.pop()
        self.set_type_of_element(self.get_var_char(var), self.get_var_type(var))
        self.set_temp(self.get_var_char(var))
        # self.code_gen_two_arg('ASSIGN', '#0', self.temp_addr) # todo: determine what to assign to variable
        self.update_temp_addr(1)

    def array_dec_param(self):
        self.array_dec()
        pass  # todo: determine the array that must be assigned

    def at_least_one_num_of_params(self):
        self.num_of_params_of_functions[self.current_function] = 1

    def increase_num_of_params_by_one(self):
        self.num_of_params_of_functions[self.current_function] += 1

    def collect_args_flag(self):
        if self.collect_args:
            self.collect_args = False
        else:
            self.collect_args = True
            self.collected_args = []

    ##################
    def pid(self):
        if self.collect_args:
            self.collected_args.append(self.lookahead[0][1])
        if self.get_lk_char() != 'output' and self.get_lk_char() != 'main':
            self.ss.append(self.lookahead)

    def ptype(self):
        if self.get_lk_char() != 'output':  # and self.get_lk_char() != 'main'
            self.ss.append(self.lookahead)

    def initialize(self):
        self.code_gen_two_arg('ASSIGN', '#4', '0')

    def first_jp(self):
        self.code_gen_one_arg('JP', self.program_block_counter + 1)

    def var_declaration(self):
        var = self.ss.pop()
        self.set_type_of_element(self.get_var_char(var), self.get_var_type(var))
        self.set_temp(self.get_var_char(var))
        self.code_gen_two_arg('ASSIGN', '#0', self.temp_addr)
        # semantic_stack.append(identifier)  # for semantic check
        self.update_temp_addr(1)

    def array_dec(self):
        size_of_array = int(self.get_lk_char())
        var = self.ss.pop()
        type_of_var = self.ss[-1]
        self.set_type_of_element(self.get_var_char(var), type_of_var)
        self.set_temp(self.get_var_char(var))
        self.code_gen_two_arg('ASSIGN', '#0', self.temp_addr)
        # semantic_stack.append(identifier)  # for semantic check
        self.update_temp_addr(size_of_array)

    def array_idx(self):
        idx = self.ss.pop()
        idx = self.get_var_char(idx)
        var = self.ss.pop()
        var = self.get_var_char(var)
        self.code_gen_three_arg('MULT', self.get_addr_of_var(idx), '#4', self.temp_addr)
        self.code_gen_three_arg('ADD', '#' + str(self.get_addr_of_var(var)), self.temp_addr, self.temp_addr)
        self.ss.append('@' + str(self.temp_addr))
        self.update_temp_addr(1)

    def break_jump(self):
        self.code_gen_one_arg('JP', self.ss[-2])

    def save(self):
        self.ss.append(self.program_block_counter)
        self.code_gen_one_arg('GAP', 584)  # GAP #584 is a fake number
        # self.program_block_counter += 1

    def jpf_save(self):
        i = self.ss.pop()
        i2 = self.ss.pop()
        self.manual_code_gen_two_arg('JPF', i2, self.program_block_counter + 1, i)
        # save()
        self.ss.append(self.program_block_counter)
        self.code_gen_one_arg('GAP', 584)  # GAP #584 is a fake number

    def jp_save(self):
        self.manual_code_gen_one_arg('JP', self.program_block_counter, self.ss.pop())
        # self.ss.pop()

    def jp_until(self):
        self.code_gen_one_arg('JP', self.program_block_counter + 2)
        # save()
        self.ss.append(self.program_block_counter)
        self.code_gen_one_arg('GAP', 584)  # GAP, it is gonna be filled in future  #584 is a fake number
        # self.program_block_counter += 1
        # label()
        self.ss.append(self.program_block_counter)

    def until(self):
        self.code_gen_two_arg('JPF', self.ss.pop(), self.ss.pop())
        self.manual_code_gen_one_arg('JP', self.program_block_counter, self.ss.pop())

    def label(self):
        self.ss.append(self.program_block_counter)

    def output(self):
        out = self.ss.pop()
        out = self.get_var_char(out)
        out = self.get_addr_of_var(out)
        self.code_gen_one_arg('PRINT', out)

    ###################
    def push_assign(self):
        if self.get_lk_char() != 'output':  # and self.get_char() != 'main'
            self.ss.append(self.lookahead)
        # self.ss.append(self.lookahead)

    def assign(self):
        value = self.ss.pop()
        self.ss.pop()
        var = self.ss.pop()
        value = self.get_var_char(value)
        var = self.get_var_char(var)
        self.code_gen_two_arg('ASSIGN', self.get_addr_of_var(value), self.get_addr_of_var(var))
        try:
            if self.ss[-1][0][1] == '=':
                self.ss.append((('', var), ''))
        except Exception:
            pass

    def get_var_char(self, val):
        if isinstance(val, int):
            return str(val)
        elif self.is_digit(val):
            return val
        elif str(val).startswith(('#', '@')):
            return val
        else:
            return val[0][1]

    def get_addr_of_var(self, var):
        if not self.is_digit(var):
            for i in self.symbol_table[self.current_function]:
                if i.lexeme == var:
                    return i.address
        return var

    def is_digit(self, v):
        return v in self.digits

    def pushop(self):
        if self.get_lk_char() != 'output':  # and self.get_char() != 'main'
            self.ss.append(self.lookahead)
        # self.ss.append(self.lookahead)

    def cmp(self):
        value = self.ss.pop()
        op = self.ss.pop()
        value1 = self.ss.pop()
        tmp = self.temp_addr
        self.update_temp_addr(1)
        self.ss.append(tmp)
        value = self.get_var_char(value)
        op = self.get_var_char(op)
        value1 = self.get_var_char(value1)
        if op == '==':
            self.code_gen_three_arg('EQ', self.get_addr_of_var(value1), self.get_addr_of_var(value), tmp)
        else:
            self.code_gen_three_arg('LT', self.get_addr_of_var(value1), self.get_addr_of_var(value), tmp)

    def add_sub(self):
        value = self.ss.pop()
        op = self.ss.pop()
        value1 = self.ss.pop()
        tmp = self.temp_addr
        self.update_temp_addr(1)
        self.ss.append(tmp)
        value = self.get_var_char(value)
        op = self.get_var_char(op)
        value1 = self.get_var_char(value1)
        if op == '+':
            self.code_gen_three_arg('ADD', self.get_addr_of_var(value1), self.get_addr_of_var(value), tmp)
        else:
            self.code_gen_three_arg('SUB', self.get_addr_of_var(value1), self.get_addr_of_var(value), tmp)

    def mul(self):
        # self.ss.append(self.temp_addr)
        t1 = self.ss.pop()
        t2 = self.ss.pop()
        t1 = self.get_var_char(t1)
        t2 = self.get_var_char(t2)
        t1 = self.get_addr_of_var(t1)
        t2 = self.get_addr_of_var(t2)
        self.code_gen_three_arg('MULT', t1, t2, self.temp_addr)
        self.ss.append(self.temp_addr)
        self.update_temp_addr(1)
        # value = self.ss.pop()
        # value1 = self.ss.pop()
        # tmp = self.temp_addr
        # self.update_temp_addr(1)
        # self.ss.append(tmp)
        # self.code_gen_three_arg('mult', value, value1, tmp)

    def pnum(self):
        if self.get_lk_char() != 'output':  # and self.get_char() != 'main'
            t = (self.lookahead[0][0], '#' + self.lookahead[0][1])
            t2 = (t, self.lookahead[1])
            self.ss.append(t2)
        # tmp = self.temp_addr
        # self.update_temp_addr(1)
        # value = self.get_lk_char()
        # self.code_gen_two_arg('ASSIGN', '#' + value,tmp)

    ############
    # def get_var_char(self, var):
    #     return var[0][1]

    def get_var_type(self, var):
        return var[0][0]

    def get_lk_char(self):
        return self.lookahead[0][1]

    def get_lk_type(self):
        return self.lookahead[0][0]

    def update_temp_addr(self, offset):
        self.temp_addr = self.temp_addr + offset * 4

    def set_type_of_element(self, lex, t):
        for idx in self.symbol_table[self.current_function]:
            if idx.lexeme == lex:
                idx.type_of_var = t

    def set_temp(self, var):
        for idx in self.symbol_table[self.current_function]:
            if idx.lexeme == var:
                idx.address = self.temp_addr

    def code_gen_one_arg(self, action, a):
        block = [None] * 4
        block[0] = action
        block[1] = a
        block[2] = ''
        block[3] = ''
        # self.program_block[self.program_block_counter] = block
        self.program_block.append(block)
        self.program_block_counter = self.program_block_counter + 1

    def manual_code_gen_one_arg(self, action, a, addr):
        block = [None] * 4
        block[0] = action
        block[1] = a
        block[2] = ''
        block[3] = ''
        self.program_block[addr] = block

    def code_gen_two_arg(self, action, a, b):
        block = [None] * 4
        block[0] = action
        block[1] = a
        block[2] = b
        block[3] = ''
        # self.program_block[self.program_block_counter] = block
        self.program_block.append(block)
        self.program_block_counter = self.program_block_counter + 1

    def manual_code_gen_two_arg(self, action, a, b, addr):
        block = [None] * 4
        block[0] = action
        block[1] = a
        block[2] = b
        block[3] = ''
        self.program_block[addr] = block

    def code_gen_three_arg(self, action, a, b, c):
        block = [None] * 4
        block[0] = action
        block[1] = a
        block[2] = b
        block[3] = c
        # self.program_block[self.program_block_counter] = block
        self.program_block.append(block)
        self.program_block_counter = self.program_block_counter + 1

    def check_var_type_error(self):
        t = self.ss.pop()[0][1]
        if self.ss.pop()[0][1] == 'void':
            print("Illegal type of void for '")

    def check_scoping_error(self):
        pass
