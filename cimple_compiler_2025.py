import re
import os

###################################### LEXICAL ANALYSIS #########################################
class Token:
    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number

    def __repr__(self):
        return f"Token({self.recognized_string}, {self.family}, line {self.line_number})"

class LexerFSM:
    # Keywords as given by the grammar and earlier code:
    KEYWORDS = {"program", "declare", "if", "else", "while", "switchcase", "forcase", "incase",
                "case", "default", "not", "and", "or", "function", "procedure", "call", "return",
                "in", "inout", "input", "print"}
    # Operators: note that ":=" is two characters and also relational operators.
    OPERATORS = {"+", "-", "*", "/", "=", "<=", ">=", ">", "<", "<>", ":="}
    # Symbols include separators and grouping symbols
    SYMBOLS = {";", ",", ":", "(", ")", "{", "}", "[", "]", "."}
    
    # Lexer states
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
                # Look ahead to try to form a two-character operator.
                if i < len(text):
                    two_char = lexeme + text[i]
                    if two_char in self.OPERATORS:
                        self.tokens.append(Token(two_char, "OPERATOR", self.current_line))
                        lexeme = ""
                        state = self.START
                        i += 1
                        continue
                # If not a two-char operator, output the one-char operator.
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

        # In case a lexeme was being built and the text ended.
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

    # Grammar production: program : program ID block .
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

    # varlist : ID ( , ID )* | ε
    def varlist(self):
        if self.current_token and self.current_token.family == "IDENTIFIER":
            self.match("IDENTIFIER")
            while self.current_token and self.current_token.recognized_string == ",":
                self.match("SYMBOL", ",")
                self.match("IDENTIFIER")

    # subprograms : ( subprogram )*
    def subprograms(self):
        while self.current_token and self.current_token.recognized_string in ("function", "procedure"):
            self.subprogram()

    # subprogram : function ID ( formalparlist ) block
    #            | procedure ID ( formalparlist ) block
    def subprogram(self):
        if self.current_token.recognized_string == "function":
            self.match("KEYWORD", "function")
            func_name = self.current_token.recognized_string
            self.match("IDENTIFIER")
            self.intermediate.genquad("begin_block", func_name, "_", "_")
            self.match("SYMBOL", "(")
            self.formalparlist()
            self.match("SYMBOL", ")")
            self.block()
            self.intermediate.genquad("end_block", func_name, "_", "_")
        elif self.current_token.recognized_string == "procedure":
            self.match("KEYWORD", "procedure")
            proc_name = self.current_token.recognized_string
            self.match("IDENTIFIER")
            self.intermediate.genquad("begin_block", proc_name, "_", "_")
            self.match("SYMBOL", "(")
            self.formalparlist()
            self.match("SYMBOL", ")")
            self.block()
            self.intermediate.genquad("end_block", proc_name, "_", "_")
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

    # statement : one of several alternatives (or ε)
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
        # The assignment quad is generated after the entire expression (including any call quads)
        # has been processed—so the ":=" quad comes after the "call" quad.
        if result != lhs:
            self.intermediate.genquad(":=", result, "_", lhs)

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

    # switchcaseStat : switchcase ( case ( condition ) statements )* default statements )
    def switchcaseStat(self):
        self.match("KEYWORD", "switchcase")
        self.match("SYMBOL", "(")
        while self.current_token and self.current_token.recognized_string == "case":
            self.match("KEYWORD", "case")
            self.match("SYMBOL", "(")
            self.condition()
            self.match("SYMBOL", ")")
            self.statements()
        self.match("KEYWORD", "default")
        self.statements()
        self.match("SYMBOL", ")")

    # forcaseStat : forcase ( case ( condition ) statements )* default statements )
    def forcaseStat(self):
        self.match("KEYWORD", "forcase")
        self.match("SYMBOL", "(")
        while self.current_token and self.current_token.recognized_string == "case":
            self.match("KEYWORD", "case")
            self.match("SYMBOL", "(")
            self.condition()
            self.match("SYMBOL", ")")
            self.statements()
        self.match("KEYWORD", "default")
        self.statements()
        self.match("SYMBOL", ")")

    # incaseStat : incase ( case ( condition ) statements )* )
    def incaseStat(self):
        self.match("KEYWORD", "incase")
        self.match("SYMBOL", "(")
        while self.current_token and self.current_token.recognized_string == "case":
            self.match("KEYWORD", "case")
            self.match("SYMBOL", "(")
            self.condition()
            self.match("SYMBOL", ")")
            self.statements()
        self.match("SYMBOL", ")")

    # returnStat : return( expression )
    def returnStat(self):
        self.match("KEYWORD", "return")
        self.match("SYMBOL", "(")
        return_value = self.expression()
        self.intermediate.genquad("retv", return_value, "_", "_")
        self.match("SYMBOL", ")")

    # callStat : call ID( actualparlist )
    def callStat(self):
        self.match("KEYWORD", "call")
        proc_name = self.current_token.recognized_string
        self.match("IDENTIFIER")
        self.match("SYMBOL", "(")
        params = self.actualparlist()  # Returns a list of (mode, value)
        self.match("SYMBOL", ")")
        for param in params:
            mode = "cv" if param[0] == "in" else "ref"
            self.intermediate.genquad("par", param[1], mode, "_")
        self.intermediate.genquad("call", proc_name, "_", "_")

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

    # actualparlist : actualparitem ( , actualparitem )* | ε
    def actualparlist(self):
        params = []
        if self.current_token and self.current_token.recognized_string != ")":
            params.append(self.actualparitem())
            while self.current_token and self.current_token.recognized_string == ",":
                self.match("SYMBOL", ",")
                params.append(self.actualparitem())
        return params

    # actualparitem : in expression | inout ID
    def actualparitem(self):
        if self.current_token.recognized_string == "in":
            self.match("KEYWORD", "in")
            value = self.expression()
            return ("in", value)
        elif self.current_token.recognized_string == "inout":
            self.match("KEYWORD", "inout")
            identifier = self.current_token.recognized_string
            self.match("IDENTIFIER")
            return ("inout", identifier)
        else:
            raise SyntaxError("Expected actual parameter starting with 'in' or 'inout'.")

    # condition : boolterm ( or boolterm )*
    def condition(self):
        b = self.boolterm()
        while self.current_token and self.current_token.recognized_string == "or":
            self.match("KEYWORD", "or")
            marker = self.intermediate.nextquad()
            self.intermediate.genquad("jump", "_", "_", "_")
            self.intermediate.backpatch(b["false"], marker)
            b2 = self.boolterm()
            b["true"] = self.intermediate.merge(b["true"], b2["true"])
            b["false"] = b2["false"]
        return b

    # boolterm : boolfactor ( and boolfactor )*
    def boolterm(self):
        b = self.boolfactor()
        while self.current_token and self.current_token.recognized_string == "and":
            self.match("KEYWORD", "and")
            marker = self.intermediate.nextquad()
            self.intermediate.genquad("jump", "_", "_", "_")
            self.intermediate.backpatch(b["true"], marker)
            b2 = self.boolfactor()
            b["false"] = self.intermediate.merge(b["false"], b2["false"])
            b["true"] = b2["true"]
        return b

    # boolfactor : not [ condition ] | [ condition ] | expression REL_OP expression
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
            temp = self.intermediate.newtemp()
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
            temp = self.intermediate.newtemp()
            self.intermediate.genquad(op, place, right, temp)
            place = temp
        return place

    def factor(self):
        if self.current_token.family == "IDENTIFIER":
            ident = self.current_token.recognized_string
            self.match("IDENTIFIER")
            # Check for a function call (identifier followed by "(")
            if self.current_token and self.current_token.recognized_string == "(":
                self.match("SYMBOL", "(")
                params = self.actualparlist()  # Collect list of (mode, value)
                self.match("SYMBOL", ")")
                for param in params:
                    mode = "cv" if param[0] == "in" else "ref"
                    self.intermediate.genquad("par", param[1], mode, "_")
                temp = self.intermediate.newtemp()
                self.intermediate.genquad("par", temp, "ret", "_")
                self.intermediate.genquad("call", ident, "_", "_")
                return temp
            else:
                return ident
        elif self.current_token.family == "NUMBER":
            value = self.current_token.recognized_string
            self.match("NUMBER")
            return value
        elif self.current_token.recognized_string == "(":
            self.match("SYMBOL", "(")
            place = self.expression()
            self.match("SYMBOL", ")")
            return place
        else:
            raise SyntaxError("Unexpected token in factor")

    def optionalSign(self):
        if self.current_token and self.current_token.family == "OPERATOR" and self.current_token.recognized_string in ("+", "-"):
            op = self.current_token.recognized_string
            self.match("OPERATOR", op)

###################################### INTERMEDIATE CODE GENERATOR #########################################
class IntermediateCodeGenerator:
    def __init__(self):
        self.quads = []
        self.temp_count = 0
        self.next_quad_index = 1  # Start numbering quads from 1

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

if __name__ == "__main__":
    input_path = "tests/ci/fibonacci.ci"
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
