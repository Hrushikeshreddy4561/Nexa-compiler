"""
Nexa Compiler - Code Generator
Team Member: Rajesh
"""

from parser import (
    ProgramNode, AssignNode, ShowNode, WhenNode, RepeatNode,
    BinOpNode, ConditionNode, NumberNode, IdentifierNode
)

class TACGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.instructions.append(instruction)

    def generate(self, node):
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.generate(stmt)
        elif isinstance(node, AssignNode):
            result = self.generate_expr(node.expression)
            self.emit(f"{node.name} = {result}")
        elif isinstance(node, ShowNode):
            result = self.generate_expr(node.expression)
            self.emit(f"PRINT {result}")
        elif isinstance(node, WhenNode):
            cond_result = self.generate_condition(node.condition)
            else_label = self.new_label()
            end_label = self.new_label()
            self.emit(f"IF_FALSE {cond_result} GOTO {else_label}")
            for s in node.if_body:
                self.generate(s)
            self.emit(f"GOTO {end_label}")
            self.emit(f"{else_label}:")
            for s in node.else_body:
                self.generate(s)
            self.emit(f"{end_label}:")
        elif isinstance(node, RepeatNode):
            start_label = self.new_label()
            end_label = self.new_label()
            self.emit(f"{start_label}:")
            cond_result = self.generate_condition(node.condition)
            self.emit(f"IF_FALSE {cond_result} GOTO {end_label}")
            for s in node.body:
                self.generate(s)
            self.emit(f"GOTO {start_label}")
            self.emit(f"{end_label}:")
            
        return self.instructions

    def generate_expr(self, node):
        if isinstance(node, NumberNode):
            return str(node.value)
        elif isinstance(node, IdentifierNode):
            return node.name
        elif isinstance(node, BinOpNode):
            left = self.generate_expr(node.left)
            right = self.generate_expr(node.right)
            temp = self.new_temp()
            self.emit(f"{temp} = {left} {node.op} {right}")
            return temp

    def generate_condition(self, node):
        left = self.generate_expr(node.left)
        right = self.generate_expr(node.right)
        temp = self.new_temp()
        self.emit(f"{temp} = {left} {node.op} {right}")
        return temp


class Optimizer:
    def optimize(self, tac_list):
        optimized = []
        constants = {}

        for instr in tac_list:
            if instr.endswith(":") or instr.startswith("GOTO") or instr.startswith("IF_FALSE"):
                optimized.append(instr)
                continue

            if instr.startswith("PRINT "):
                arg = instr.split(" ", 1)[1]
                if arg in constants:
                    optimized.append(f"PRINT {constants[arg]}")
                else:
                    optimized.append(instr)
                continue

            if " = " in instr:
                parts = instr.split(" = ", 1)
                dest = parts[0].strip()
                expr = parts[1].strip()
                tokens = expr.split()

                if len(tokens) == 1:
                    val = tokens[0]
                    if val.lstrip('-').isdigit():
                        constants[dest] = int(val)
                        optimized.append(instr)
                    elif val in constants:
                        constants[dest] = constants[val]
                        optimized.append(f"{dest} = {constants[val]}")
                    else:
                        constants.pop(dest, None)
                        optimized.append(instr)
                elif len(tokens) == 3:
                    left_str, op, right_str = tokens
                    left_val = constants.get(left_str) if not left_str.lstrip('-').isdigit() else int(left_str)
                    right_val = constants.get(right_str) if not right_str.lstrip('-').isdigit() else int(right_str)

                    if left_val is not None and right_val is not None and op in ('+', '-', '*', '/'):
                        if op == '+': result = left_val + right_val
                        elif op == '-': result = left_val - right_val
                        elif op == '*': result = left_val * right_val
                        elif op == '/': result = left_val // right_val if right_val != 0 else 0
                        constants[dest] = result
                        optimized.append(f"{dest} = {result}")
                    else:
                        new_left = str(constants[left_str]) if left_str in constants else left_str
                        new_right = str(constants[right_str]) if right_str in constants else right_str
                        constants.pop(dest, None)
                        optimized.append(f"{dest} = {new_left} {op} {new_right}")
                else:
                    constants.pop(dest, None)
                    optimized.append(instr)
            else:
                optimized.append(instr)

        return optimized


class TargetCodeGenerator:
    def __init__(self):
        self.target = []
        self.reg_count = 0
        self.var_to_reg = {}

    def get_reg(self, var):
        if var not in self.var_to_reg:
            reg = f"R{self.reg_count % 10}"
            self.var_to_reg[var] = reg
            self.reg_count += 1
        return self.var_to_reg[var]

    def generate(self, optimized_tac):
        for instr in optimized_tac:
            if instr.endswith(":"):
                self.target.append(instr)
                continue

            if instr.startswith("GOTO "):
                label = instr.split(" ", 1)[1]
                self.target.append(f"  JMP {label}")
                continue

            if instr.startswith("IF_FALSE "):
                parts = instr.split()
                cond = parts[1]
                label = parts[3]
                reg = self.get_reg(cond)
                self.target.append(f"  CMP {reg}, 0")
                self.target.append(f"  JE {label}")
                continue

            if instr.startswith("PRINT "):
                arg = instr.split(" ", 1)[1]
                if arg.lstrip('-').isdigit():
                    self.target.append(f"  OUT {arg}")
                else:
                    reg = self.get_reg(arg)
                    self.target.append(f"  OUT {reg}")
                continue

            if " = " in instr:
                parts = instr.split(" = ", 1)
                dest = parts[0].strip()
                expr = parts[1].strip()
                tokens = expr.split()
                dest_reg = self.get_reg(dest)

                if len(tokens) == 1:
                    val = tokens[0]
                    if val.lstrip('-').isdigit():
                        self.target.append(f"  MOV {dest_reg}, {val}")
                    else:
                        src_reg = self.get_reg(val)
                        self.target.append(f"  MOV {dest_reg}, {src_reg}")
                elif len(tokens) == 3:
                    left, op, right = tokens
                    if left.lstrip('-').isdigit():
                        self.target.append(f"  MOV {dest_reg}, {left}")
                    else:
                        src = self.get_reg(left)
                        self.target.append(f"  MOV {dest_reg}, {src}")
                    
                    op_map = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
                              '<': 'LT', '>': 'GT', '<=': 'LE', '>=': 'GE',
                              '==': 'EQ', '!=': 'NE'}
                    asm_op = op_map.get(op, op)
                    if right.lstrip('-').isdigit():
                        self.target.append(f"  {asm_op} {dest_reg}, {right}")
                    else:
                        src = self.get_reg(right)
                        self.target.append(f"  {asm_op} {dest_reg}, {src}")

        return self.target
