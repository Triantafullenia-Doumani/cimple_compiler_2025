import re
import os

###################################### SYMBOL TABLE CLASSES #########################################
class Entity:
    def __init__(self, name):
        self.name = name

class Variable(Entity):
    def __init__(self, name, datatype, offset):
        super().__init__(name)
        self.datatype = datatype
        self.offset = offset

# Temporary variables are similar to variables.
class TemporaryVariable(Variable):
    def __init__(self, name, datatype="int", offset=0):
        super().__init__(name, datatype, offset)

class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.entities = {}         # Maps names to Entity instances
        self.offset_counter = 0    # For allocating memory offsets

    def add_entity(self, entity):
        if entity.name in self.entities:
            raise ValueError(f"Duplicate declaration: {entity.name}")
        self.entities[entity.name] = entity

    def find_entity(self, name):
        if name in self.entities:
            return self.entities[name]
        elif self.parent:
            return self.parent.find_entity(name)
        return None

class SymbolTable:
    def __init__(self):
        self.scopes = []

    def open_scope(self):
        parent = self.scopes[-1] if self.scopes else None
        new_scope = Scope(parent)
        self.scopes.append(new_scope)
        print("new scope added")

    def close_scope(self):
        return self.scopes.pop()

    def current_scope(self):
        return self.scopes[-1] if self.scopes else None

    def declare(self, entity):
        self.current_scope().add_entity(entity)

    def lookup(self, name):
        return self.current_scope().find_entity(name)

    def allocate_offset(self):
        offset = self.current_scope().offset_counter
        self.current_scope().offset_counter += 4
        return offset

    def print_table(self):
        print("\n=== Symbol Table ===")
        def print_scope(scope, level=0):
            indent = "  " * level
            for name, entity in scope.entities.items():
                print(f"{indent}{type(entity).__name__}: {vars(entity)}")
            if scope.parent:
                print_scope(scope.parent, level + 1)
        if self.scopes:
            print_scope(self.current_scope())

###################################### LEXICAL ANALYSIS #########################################
class Token:
    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number

    def __repr__(self):
        return f"Token({self.recognized_string}, {self.family}, line {self.line_number})"

class LexerFSM:
    KEYWORDS = {"program", "declare", "if", "else", "while", "switchcase", "forcase", "incase",
                "case", "default", "not", "and", "or", "function", "procedure", "call", "return",
                "in", "inout", "input", "print"}
    OPERATORS = {"+", "-", "*", "/", "=", "<=", ">=", ">", "<", "<>", ":="}
    SYMBOLS = {";", ",", ":", "(", ")", "{", "}", "[", "]", "."}
    
    START, IDENTIFIER, NUMBER, OPERATOR, COMMENT = range(5)

    def __init__(self, file_path):
        self.file_path = file_path
        self.tokens = []
        self.current_line = 1

    def tokenize(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        state = self.START
        i = 0
        lexeme = ""
        while i < len(text):
            char = text[i]
            if state == self.START:
                if char in " \t\r":
                    i += 1
                    continue
                if char == "\n":
                    self.current_line += 1
                    i += 1
                    continue
                if char == "#":
                    state = self.COMMENT
                    i += 1
                    continue
                if char.isalpha():
                    state = self.IDENTIFIER
                    lexeme = char
                    i += 1
                    continue
                if char.isdigit():
                    state = self.NUMBER
                    lexeme = char
                    i += 1
                    continue
                if any(char == op[0] for op in self.OPERATORS):
                    state = self.OPERATOR
                    lexeme = char
                    i += 1
                    continue
                if char in self.SYMBOLS:
                    self.tokens.append(Token(char, "SYMBOL", self.current_line))
                    i += 1
                    continue
                else:
                    raise ValueError(f"Error on line {self.current_line}: Unknown character '{char}'")
            elif state == self.IDENTIFIER:
                if i < len(text) and text[i].isalnum():
                    lexeme += text[i]
                    i += 1
                else:
                    token_type = "KEYWORD" if lexeme in self.KEYWORDS else "IDENTIFIER"
                    self.tokens.append(Token(lexeme, token_type, self.current_line))
                    lexeme = ""
                    state = self.START
                continue
            elif state == self.NUMBER:
                if i < len(text) and text[i].isdigit():
                    lexeme += text[i]
                    i += 1
                else:
                    self.tokens.append(Token(lexeme, "NUMBER", self.current_line))
                    lexeme = ""
                    state = self.START
                continue
            elif state == self.OPERATOR:
                if i < len(text):
                    two_char = lexeme + text[i]
                    if two_char in self.OPERATORS:
                        self.tokens.append(Token(two_char, "OPERATOR", self.current_line))
                        lexeme = ""
                        state = self.START
                        i += 1
                        continue
                if lexeme in self.OPERATORS:
                    self.tokens.append(Token(lexeme, "OPERATOR", self.current_line))
                else:
                    raise ValueError(f"Error on line {self.current_line}: Unknown operator '{lexeme}'")
                lexeme = ""
                state = self.START
                continue
            elif state == self.COMMENT:
                if char == "#":
                    state = self.START
                i += 1
                continue
        if state == self.IDENTIFIER:
            token_type = "KEYWORD" if lexeme in self.KEYWORDS else "IDENTIFIER"
            self.tokens.append(Token(lexeme, token_type, self.current_line))
        elif state == self.NUMBER:
            self.tokens.append(Token(lexeme, "NUMBER", self.current_line))
        elif state == self.OPERATOR:
            if lexeme in self.OPERATORS:
                self.tokens.append(Token(lexeme, "OPERATOR", self.current_line))
            else:
                raise ValueError(f"Error on line {self.current_line}: Unknown operator '{lexeme}'")
        return self.tokens

###################################### SYNTAX ANALYSIS #########################################
class Parser:
    def __init__(self, tokens, intermediate):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index] if self.tokens else None
        self.intermediate = intermediate  
        self.symbol_table = SymbolTable()
        # Open the global (outermost) scope.
        self.symbol_table.open_scope()

    # Helper: Create and declare a temporary variable.
    def new_temp(self):
        temp_name = self.intermediate.newtemp()  # e.g., T_1, T_2, etc.
        offset = self.symbol_table.allocate_offset()
        self.symbol_table.declare(TemporaryVariable(temp_name, "int", offset))
        return temp_name

    def match(self, expected_family, expected_value=None):
        if self.current_token is None:
            raise SyntaxError("Unexpected end of input.")
        if self.current_token.family == expected_family and (expected_value is None or self.current_token.recognized_string == expected_value):
            self.current_token_index += 1
            if self.current_token_index < len(self.tokens):
                self.current_token = self.tokens[self.current_token_index]
            else:
                self.current_token = None
        else:
            exp = expected_value if expected_value is not None else expected_family
            raise SyntaxError(f"Syntax error at line {self.current_token.line_number}: Expected '{exp}', found '{self.current_token.recognized_string}'.")

    # program : program ID block .
    def program(self):
        self.match("KEYWORD", "program")
        prog_name = self.current_token.recognized_string
        self.match("IDENTIFIER")
        self.declarations()
        self.subprograms()
        self.intermediate.genquad("begin_block", prog_name, "_", "_")
        self.statements()
        self.intermediate.genquad("halt", "_", "_", "_")
        self.intermediate.genquad("end_block", prog_name, "_", "_")
        self.match("SYMBOL", ".")
        # Print the symbol table; should include global variables and any temporaries.
        self.symbol_table.print_table()

    # block : declarations subprograms statements
    def block(self):
        self.declarations()
        self.subprograms()
        self.statements()

    # declarations : ( declare varlist ; )*
    def declarations(self):
        while self.current_token and self.current_token.recognized_string == "declare":
            self.match("KEYWORD", "declare")
            self.varlist()
            self.match("SYMBOL", ";")

    # varlist : ID ( , ID )*
    def varlist(self):
        if self.current_token and self.current_token.family == "IDENTIFIER":
            var_name = self.current_token.recognized_string
            self.match("IDENTIFIER")
            offset = self.symbol_table.allocate_offset()
            self.symbol_table.declare(Variable(var_name, "int", offset))
            while self.current_token and self.current_token.recognized_string == ",":
                self.match("SYMBOL", ",")
                var_name = self.current_token.recognized_string
                self.match("IDENTIFIER")
                offset = self.symbol_table.allocate_offset()
                self.symbol_table.declare(Variable(var_name, "int", offset))

    # subprograms : ( subprogram )*
    def subprograms(self):
        while self.current_token and self.current_token.recognized_string in ("function", "procedure"):
            self.subprogram()

    # subprogram : function ID ( formalparlist ) block | procedure ID ( formalparlist ) block
    def subprogram(self):
        if self.current_token.recognized_string == "function":
            self.match("KEYWORD", "function")
            func_name = self.current_token.recognized_string
            self.match("IDENTIFIER")
            self.intermediate.genquad("begin_block", func_name, "_", "_")
            self.match("SYMBOL", "(")
            self.formalparlist()
            self.match("SYMBOL", ")")
            self.symbol_table.open_scope()  # Open new scope for function body.
            self.block()
            self.intermediate.genquad("end_block", func_name, "_", "_")
            self.symbol_table.close_scope()
        elif self.current_token.recognized_string == "procedure":
            self.match("KEYWORD", "procedure")
            proc_name = self.current_token.recognized_string
            self.match("IDENTIFIER")
            self.intermediate.genquad("begin_block", proc_name, "_", "_")
            self.match("SYMBOL", "(")
            self.formalparlist()
            self.match("SYMBOL", ")")
            self.symbol_table.open_scope()  # Open new scope for procedure body.
            self.block()
            self.intermediate.genquad("end_block", proc_name, "_", "_")
            self.symbol_table.close_scope()
        else:
            raise SyntaxError("Expected 'function' or 'procedure' in subprogram.")

    # formalparlist : formalparitem ( , formalparitem )* | ε
    def formalparlist(self):
        if self.current_token and self.current_token.recognized_string in ("in", "inout"):
            self.formalparitem()
            while self.current_token and self.current_token.recognized_string == ",":
                self.match("SYMBOL", ",")
                self.formalparitem()

    # formalparitem : in ID | inout ID
    def formalparitem(self):
        if self.current_token.recognized_string == "in":
            self.match("KEYWORD", "in")
            self.match("IDENTIFIER")
        elif self.current_token.recognized_string == "inout":
            self.match("KEYWORD", "inout")
            self.match("IDENTIFIER")
        else:
            raise SyntaxError("Expected formal parameter starting with 'in' or 'inout'.")

    # statements : statement ; | { statement ( ; statement )* }
    def statements(self):
        if self.current_token and self.current_token.recognized_string == "{":
            self.match("SYMBOL", "{")
            self.statement()
            while self.current_token and self.current_token.recognized_string == ";":
                self.match("SYMBOL", ";")
                self.statement()
            self.match("SYMBOL", "}")
        else:
            self.statement()
            self.match("SYMBOL", ";")

    def statement(self):
        if self.current_token is None:
            return
        if self.current_token.family == "IDENTIFIER":
            self.assignStat()
        elif self.current_token.recognized_string == "if":
            self.ifStat()
        elif self.current_token.recognized_string == "while":
            self.whileStat()
        elif self.current_token.recognized_string == "switchcase":
            self.switchcaseStat()
        elif self.current_token.recognized_string == "forcase":
            self.forcaseStat()
        elif self.current_token.recognized_string == "incase":
            self.incaseStat()
        elif self.current_token.recognized_string == "call":
            self.callStat()
        elif self.current_token.recognized_string == "return":
            self.returnStat()
        elif self.current_token.recognized_string == "input":
            self.inputStat()
        elif self.current_token.recognized_string == "print":
            self.printStat()
        else:
            pass

    # assignStat : ID := expression
    def assignStat(self):
        lhs = self.current_token.recognized_string
        self.match("IDENTIFIER")
        self.match("OPERATOR", ":=")
        result = self.expression()
        if result != lhs:
            self.intermediate.genquad(":=", result, "_", lhs)

    # returnStat : return( expression )
    def returnStat(self):
        self.match("KEYWORD", "return")
        self.match("SYMBOL", "(")
        ret_val = self.expression()
        self.intermediate.genquad("retv", ret_val, "_", "_")
        self.match("SYMBOL", ")")

    # printStat : print( expression )
    def printStat(self):
        self.match("KEYWORD", "print")
        self.match("SYMBOL", "(")
        print_value = self.expression()
        self.intermediate.genquad("out", print_value, "_", "_")
        self.match("SYMBOL", ")")

    # inputStat : input( ID )
    def inputStat(self):
        self.match("KEYWORD", "input")
        self.match("SYMBOL", "(")
        input_var = self.current_token.recognized_string
        self.match("IDENTIFIER")
        self.intermediate.genquad("inp", input_var, "_", "_")
        self.match("SYMBOL", ")")

    # callStat : call ID( actualparlist )
    def callStat(self):
        self.match("KEYWORD", "call")
        func_name = self.current_token.recognized_string
        self.match("IDENTIFIER")
        self.match("SYMBOL", "(")
        self.actualparlist()  # Parameters will be handled by generated 'par' quads.
        self.match("SYMBOL", ")")
        self.intermediate.genquad("call", func_name, "_", "_")

    # ifStat : if ( condition ) statements elsepart
    def ifStat(self):
        self.match("KEYWORD", "if")
        self.match("SYMBOL", "(")
        b = self.condition()
        self.match("SYMBOL", ")")
        self.intermediate.backpatch(b["true"], self.intermediate.nextquad())
        self.statements()
        jump_after_then = self.intermediate.genquad("jump", "_", "_", "_")
        self.intermediate.backpatch(b["false"], self.intermediate.nextquad())
        if self.current_token and self.current_token.recognized_string == "else":
            self.match("KEYWORD", "else")
            self.statements()
        self.intermediate.backpatch([jump_after_then], self.intermediate.nextquad())

    # whileStat : while ( condition ) statements
    def whileStat(self):
        M = self.intermediate.nextquad()
        self.match("KEYWORD", "while")
        self.match("SYMBOL", "(")
        b = self.condition()
        self.match("SYMBOL", ")")
        S = self.intermediate.nextquad()
        self.intermediate.backpatch(b["true"], S)
        self.statements()
        self.intermediate.genquad("jump", "_", "_", M)
        F = self.intermediate.nextquad()
        self.intermediate.backpatch(b["false"], F)

    def switchcaseStat(self):
        self.match("KEYWORD", "switchcase")
        exit_list = []  # Initialize exit list.
        while self.current_token and self.current_token.recognized_string == "case":
            self.match("KEYWORD", "case")
            if self.current_token.recognized_string == "(":
                self.match("SYMBOL", "(")
                cond = self.condition()
                self.match("SYMBOL", ")")
            else:
                cond = self.condition()
            self.intermediate.backpatch(cond["true"], self.intermediate.nextquad())
            self.statements()
            t = self.intermediate.makelist(self.intermediate.genquad("jump", "_", "_", "_"))
            exit_list = self.intermediate.merge(exit_list, t)
            self.intermediate.backpatch(cond["false"], self.intermediate.nextquad())
        self.match("KEYWORD", "default")
        self.statements()
        self.intermediate.backpatch(exit_list, self.intermediate.nextquad())

    def forcaseStat(self):
        self.match("KEYWORD", "forcase")
        firstCondQuad = self.intermediate.nextquad()  # Marker for case conditions.
        exit_jumps = []
        prev_false_list = None
        while self.current_token and self.current_token.recognized_string == "case":
            current_cond_quad = self.intermediate.nextquad()
            self.match("KEYWORD", "case")
            self.match("SYMBOL", "(")
            cond = self.condition()
            self.match("SYMBOL", ")")
            if prev_false_list is not None:
                self.intermediate.backpatch(prev_false_list, current_cond_quad)
            self.intermediate.backpatch(cond["true"], self.intermediate.nextquad())
            self.statements()
            exit_jumps.append(self.intermediate.genquad("jump", "_", "_", firstCondQuad))
            prev_false_list = cond["false"]
        self.match("KEYWORD", "default")
        self.intermediate.backpatch(prev_false_list, self.intermediate.nextquad())
        self.statements()

    def incaseStat(self):
        self.match("KEYWORD", "incase")
        flag = self.new_temp()
        firstCondQuad = self.intermediate.nextquad()
        self.intermediate.genquad(":=", 0, "_", flag)
        while self.current_token and self.current_token.recognized_string == "case":
            self.match("KEYWORD", "case")
            if self.current_token.recognized_string == "(":
                self.match("SYMBOL", "(")
                cond = self.condition()
                self.match("SYMBOL", ")")
            else:
                cond = self.condition()
            self.intermediate.backpatch(cond["true"], self.intermediate.nextquad())
            self.statements()
            self.intermediate.genquad(":=", 1, "_", flag)
            self.intermediate.backpatch(cond["false"], self.intermediate.nextquad())
        self.match("KEYWORD", "default")
        self.intermediate.genquad("=", 1, flag, firstCondQuad)
        self.statements()

    def actualparlist(self):
        params = []
        if self.current_token and self.current_token.recognized_string != ")":
            params.append(self.actualparitem())
            while self.current_token and self.current_token.recognized_string == ",":
                self.match("SYMBOL", ",")
                params.append(self.actualparitem())
        return params

    def actualparitem(self):
        if self.current_token.recognized_string == "in":
            self.match("KEYWORD", "in")
            value = self.expression()
            self.intermediate.genquad("par", value, "cv", "_")
            return ("in", value)
        elif self.current_token.recognized_string == "inout":
            self.match("KEYWORD", "inout")
            identifier = self.current_token.recognized_string
            self.match("IDENTIFIER")
            self.intermediate.genquad("par", identifier, "ref", "_")
            return ("inout", identifier)
        else:
            raise SyntaxError("Expected actual parameter starting with 'in' or 'inout'.")

    def condition(self):
        b = self.boolterm()
        while self.current_token and self.current_token.recognized_string == "or":
            self.match("KEYWORD", "or")
            marker = self.intermediate.nextquad()
            self.intermediate.backpatch(b["false"], marker)
            b2 = self.boolterm()
            b["true"] = self.intermediate.merge(b["true"], b2["true"])
            b["false"] = b2["false"]
        return b

    def boolterm(self):
        b = self.boolfactor()
        while self.current_token and self.current_token.recognized_string == "and":
            self.match("KEYWORD", "and")
            marker = self.intermediate.nextquad()
            self.intermediate.backpatch(b["true"], marker)
            b2 = self.boolfactor()
            b["false"] = self.intermediate.merge(b["false"], b2["false"])
            b["true"] = b2["true"]
        return b

    def boolfactor(self):
        if self.current_token and self.current_token.recognized_string == "not":
            self.match("KEYWORD", "not")
            self.match("SYMBOL", "[")
            b = self.condition()
            self.match("SYMBOL", "]")
            return {"true": b["false"], "false": b["true"]}
        elif self.current_token and self.current_token.recognized_string == "[":
            self.match("SYMBOL", "[")
            b = self.condition()
            self.match("SYMBOL", "]")
            return b
        else:
            left = self.expression()
            if (self.current_token and self.current_token.family == "OPERATOR" and
                self.current_token.recognized_string in ("=", "<=", ">=", ">", "<", "<>")):
                op = self.current_token.recognized_string
                self.match("OPERATOR", op)
            else:
                raise SyntaxError("Expected relational operator in boolean factor.")
            right = self.expression()
            q_true = self.intermediate.genquad(op, left, right, "_")
            true_list = self.intermediate.makelist(q_true)
            q_false = self.intermediate.genquad("jump", "_", "_", "_")
            false_list = self.intermediate.makelist(q_false)
            return {"true": true_list, "false": false_list}

    def expression(self):
        place = self.term()
        while (self.current_token and 
               self.current_token.family == "OPERATOR" and 
               self.current_token.recognized_string in ("+", "-")):
            op = self.current_token.recognized_string
            self.match("OPERATOR", op)
            right = self.term()
            temp = self.new_temp()
            self.intermediate.genquad(op, place, right, temp)
            place = temp
        return place

    def term(self):
        place = self.factor()
        while (self.current_token and 
               self.current_token.family == "OPERATOR" and 
               self.current_token.recognized_string in ("*", "/")):
            op = self.current_token.recognized_string
            self.match("OPERATOR", op)
            right = self.factor()
            temp = self.new_temp()
            self.intermediate.genquad(op, place, right, temp)
            place = temp
        return place

    def factor(self):
        unary = None
        if self.current_token and self.current_token.family == "OPERATOR" and self.current_token.recognized_string in ("+", "-"):
            unary = self.current_token.recognized_string
            self.match("OPERATOR", unary)
        if self.current_token.family == "IDENTIFIER":
            ident = self.current_token.recognized_string
            self.match("IDENTIFIER")
            if self.current_token and self.current_token.recognized_string == "(":
                self.match("SYMBOL", "(")
                self.actualparlist()
                self.match("SYMBOL", ")")
                temp = self.new_temp()
                self.intermediate.genquad("par", temp, "ret", "_")
                self.intermediate.genquad("call", ident, "_", "_")
                result = temp
            else:
                result = ident
        elif self.current_token.family == "NUMBER":
            value = self.current_token.recognized_string
            self.match("NUMBER")
            result = value
        elif self.current_token.recognized_string == "(":
            self.match("SYMBOL", "(")
            result = self.expression()
            self.match("SYMBOL", ")")
        else:
            raise SyntaxError("Unexpected token in factor")
        if unary == "-":
            temp = self.new_temp()
            self.intermediate.genquad("*", result, "-1", temp)
            result = temp
        return result

    def optionalSign(self):
        if self.current_token and self.current_token.family == "OPERATOR" and self.current_token.recognized_string in ("+", "-"):
            op = self.current_token.recognized_string
            self.match("OPERATOR", op)

###################################### INTERMEDIATE CODE GENERATOR #########################################
class IntermediateCodeGenerator:
    def __init__(self):
        self.quads = []
        self.temp_count = 0
        self.next_quad_index = 1  # Quads numbered from 1

    def nextquad(self):
        return self.next_quad_index

    def genquad(self, op, x, y, z):
        quad = (self.next_quad_index, op, x, y, z)
        self.quads.append(quad)
        self.next_quad_index += 1
        return quad[0]

    def newtemp(self):
        self.temp_count += 1
        return f"T_{self.temp_count}"

    def makelist(self, index):
        return [index]

    def merge(self, list1, list2):
        return list1 + list2

    def backpatch(self, lst, z):
        for index in lst:
            for i, quad in enumerate(self.quads):
                if quad[0] == index:
                    self.quads[i] = (quad[0], quad[1], quad[2], quad[3], z)
                    break

    def print_quads(self):
        for quad in self.quads:
            print(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}")

###################################### WRITE INTERMEDIATE CODE TO FILE #########################################
def write_int_file(intermediate, input_path):
    base_name = os.path.basename(input_path)
    name_without_ext = os.path.splitext(base_name)[0]
    output_filename = f"{name_without_ext}.int"
    output_folder = "int"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        for quad in intermediate.quads:
            f.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
    print(f"Intermediate code written to {output_path}")

###################################### ASSEMBLY CODE GENERATION #########################################
def get_offset(symbol_table, name):
    # Search all scopes for the entity's offset.
    for scope in symbol_table.scopes:
        if name in scope.entities:
            return scope.entities[name].offset
    return 0

def write_asm_file(intermediate, symbol_table, input_path):
    base_name = os.path.basename(input_path)
    name_without_ext = os.path.splitext(base_name)[0]
    output_filename = f"{name_without_ext}.asm"
    output_folder = "asm"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, output_filename)

    asm_lines = []
    # Prologue: branch to main and save return address.
    asm_lines.append("L0: b Lmain")
    asm_lines.append("L1: sw $ra,-0($sp)")

    for quad in intermediate.quads:
        index, op, x, y, z = quad
        if op == "+":
            offset_x = get_offset(symbol_table, x)
            offset_z = get_offset(symbol_table, z)
            asm_lines.append(f"L{index}: lw $t1,-{offset_x}($sp)")
            asm_lines.append(f"    li $t2,{y}")
            asm_lines.append(f"    add $t1,$t1,$t2")
            asm_lines.append(f"    sw $t1,-{offset_z}($sp)")
        elif op == "-":
            offset_x = get_offset(symbol_table, x)
            offset_z = get_offset(symbol_table, z)
            asm_lines.append(f"L{index}: lw $t1,-{offset_x}($sp)")
            asm_lines.append(f"    li $t2,{y}")
            asm_lines.append(f"    sub $t1,$t1,$t2")
            asm_lines.append(f"    sw $t1,-{offset_z}($sp)")
        elif op == "*":
            offset_x = get_offset(symbol_table, x)
            offset_y = get_offset(symbol_table, y) if not y.isdigit() else None
            offset_z = get_offset(symbol_table, z)
            asm_lines.append(f"L{index}: lw $t1,-{offset_x}($sp)")
            if y.isdigit():
                asm_lines.append(f"    li $t2,{y}")
            else:
                asm_lines.append(f"    lw $t2,-{offset_y}($sp)")
            asm_lines.append(f"    mul $t1,$t1,$t2")
            asm_lines.append(f"    sw $t1,-{offset_z}($sp)")
        elif op == "/":
            offset_x = get_offset(symbol_table, x)
            offset_y = get_offset(symbol_table, y) if not y.isdigit() else None
            offset_z = get_offset(symbol_table, z)
            asm_lines.append(f"L{index}: lw $t1,-{offset_x}($sp)")
            if y.isdigit():
                asm_lines.append(f"    li $t2,{y}")
            else:
                asm_lines.append(f"    lw $t2,-{offset_y}($sp)")
            asm_lines.append("    div $t1,$t2")
            asm_lines.append("    mflo $t1")
            asm_lines.append(f"    sw $t1,-{offset_z}($sp)")
        elif op == ":=":
            offset_z = get_offset(symbol_table, z)
            if x.isdigit() or (x.startswith("-") and x[1:].isdigit()):
                asm_lines.append(f"L{index}: li $t1,{x}")
                asm_lines.append(f"    sw $t1,-{offset_z}($sp)")
            else:
                offset_x = get_offset(symbol_table, x)
                asm_lines.append(f"L{index}: lw $t1,-{offset_x}($sp)")
                asm_lines.append(f"    lw $t0,-{offset_z}($sp)")
                asm_lines.append(f"    sw $t1,($t0)")
        elif op == "par":
            # Parameter passing: mode is in y ("cv", "ref", or "ret")
            # For simplicity, assume a fixed parameter slot at offset 100 on the stack.
            if y == "cv":
                offset_x = get_offset(symbol_table, x)
                asm_lines.append(f"L{index}: lw $t1,-{offset_x}($sp)   // par cv")
                asm_lines.append("    sw $t1,-100($sp)   // store parameter value")
            elif y == "ref":
                offset_x = get_offset(symbol_table, x)
                asm_lines.append(f"L{index}: la $t1,-{offset_x}($sp)   // par ref")
                asm_lines.append("    sw $t1,-100($sp)   // store reference")
            elif y == "ret":
                offset_x = get_offset(symbol_table, x)
                asm_lines.append(f"L{index}: lw $t1,-{offset_x}($sp)   // par ret")
                asm_lines.append("    sw $t1,-104($sp)   // store return value")
            else:
                asm_lines.append(f"L{index}: // Unhandled par mode: {y}")
        elif op == "call":
            # Function call: jump and link to function label.
            asm_lines.append(f"L{index}: jal {x}")
        elif op == "inp":
            offset_x = get_offset(symbol_table, x)
            asm_lines.append(f"L{index}: jal read_int")
            asm_lines.append(f"    sw $v0,-{offset_x}($sp)")
        elif op == "out":
            offset_x = get_offset(symbol_table, x)
            asm_lines.append(f"L{index}: lw $t1,-{offset_x}($sp)")
            asm_lines.append("    move $a0,$t1")
            asm_lines.append("    jal print_int")
        elif op == "retv":
            offset_x = get_offset(symbol_table, x)
            asm_lines.append(f"L{index}: lw $t0,-{offset_x}($sp)")
            asm_lines.append("    lw $t1,($t0)")
            asm_lines.append("    lw $t0,-8($sp)")
            asm_lines.append("    sw $t1,($t0)")
        elif op == "begin_block":
            asm_lines.append(f"L{index}: // begin_block for {x}")
        elif op == "end_block":
            asm_lines.append(f"L{index}: lw $ra,-0($sp)")
            asm_lines.append("    jr $ra")
        elif op == "halt":
            asm_lines.append(f"L{index}: // halt")
        elif op == "jump":
            asm_lines.append(f"L{index}: j {z}")
        else:
            asm_lines.append(f"L{index}: // Unhandled op: {op} {x} {y} {z}")

    with open(output_path, "w", encoding="utf-8") as f:
        for line in asm_lines:
            f.write(line + "\n")
    print(f"Assembly code written to {output_path}")

###################################### MAIN #########################################
if __name__ == "__main__":
    input_path = "tests/ci/factorial.ci"
    lexer = LexerFSM(input_path)
    print("Lexical analysis completed successfully.")
    tokens = lexer.tokenize()
    intermediate = IntermediateCodeGenerator()
    parser = Parser(tokens, intermediate)
    parser.program()
    print("Parsing completed successfully.")
    print("\nGenerated Intermediate Code (Quads):")
    intermediate.print_quads()
    write_int_file(intermediate, input_path)
    write_asm_file(intermediate, parser.symbol_table, input_path)
