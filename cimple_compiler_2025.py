
import re
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
    def __init__(self, tokens,intermidiate):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index] if self.tokens else None
        self.intermediate = intermidiate  


    def match(self, expected_family, expected_value=None):
        if self.current_token is None:
            raise SyntaxError("Unexpected end of input.")
        if self.current_token.family == expected_family and (expected_value is None or self.current_token.recognized_string == expected_value):
            # Uncomment the next line for debugging token consumption:
            # print("Matched:", self.current_token)
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
        # Get the program name from the ID token:
        prog_name = self.current_token.recognized_string
        self.match("IDENTIFIER")
    
        # Process declarations and subprograms before the main block.
        self.declarations()
        self.subprograms()
    
        # Generate a quad to mark the beginning of the main block.
        self.intermediate.genquad("begin_block", prog_name, "_", "_")
    
        # Parse the main block (statements).
        self.statements()
    
        # Generate a halt quad and an end_block quad.
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
        # Else: ε

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
        # Else: ε

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

    # statements : statement ; 
    #            | { statement ( ; statement )* }
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
            return  # ε production
        if self.current_token.family == "IDENTIFIER":
            # Assume assignStat if followed by ':='.
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
            # Allow an empty statement (ε)
            pass

    # assignStat : ID := expression
    def assignStat(self):
        lhs = self.current_token.recognized_string  # e.g., "c"
        self.match("IDENTIFIER")
        self.match("OPERATOR", ":=")
    
        # Evaluate the expression with the target variable provided.
        result = self.expression(target=lhs)
    
        # If the expression didn't directly store its result in lhs, assign it.
        if result != lhs:
            self.intermediate.genquad(":=", result, "_", lhs)


    # ifStat : if ( condition ) statements elsepart
    def ifStat(self):
        self.match("KEYWORD", "if")
        self.match("SYMBOL", "(")
        self.condition()
        self.match("SYMBOL", ")")
        self.statements()
        self.elsepart()

    # elsepart : else statements | ε
    def elsepart(self):
        if self.current_token and self.current_token.recognized_string == "else":
            self.match("KEYWORD", "else")
            self.statements()
        # Else: ε

    # whileStat : while ( condition ) statements
    def whileStat(self):
        self.match("KEYWORD", "while")
        self.match("SYMBOL", "(")
        self.condition()
        self.match("SYMBOL", ")")
        self.statements()

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
        self.match("IDENTIFIER")
        self.match("SYMBOL", "(")
        self.actualparlist()
        self.match("SYMBOL", ")")

    # printStat : print( expression )
    def printStat(self):
        self.match("KEYWORD", "print")
        self.match("SYMBOL", "(")
        self.expression()
        self.match("SYMBOL", ")")

    # inputStat : input( ID )
    def inputStat(self):
        self.match("KEYWORD", "input")
        self.match("SYMBOL", "(")
        self.match("IDENTIFIER")
        self.match("SYMBOL", ")")

    # actualparlist : actualparitem ( , actualparitem )* | ε
    def actualparlist(self):
        if self.current_token and self.current_token.recognized_string != ")":
            self.actualparitem()
            while self.current_token and self.current_token.recognized_string == ",":
                self.match("SYMBOL", ",")
                self.actualparitem()

    # actualparitem : in expression | inout ID
    def actualparitem(self):
        if self.current_token.recognized_string == "in":
            self.match("KEYWORD", "in")
            self.expression()
        elif self.current_token.recognized_string == "inout":
            self.match("KEYWORD", "inout")
            self.match("IDENTIFIER")
        else:
            raise SyntaxError("Expected actual parameter starting with 'in' or 'inout'.")

    # condition : boolterm ( or boolterm )*
    def condition(self):
        self.boolterm()
        while self.current_token and self.current_token.recognized_string == "or":
            self.match("KEYWORD", "or")
            self.boolterm()

    # boolterm : boolfactor ( and boolfactor )*
    def boolterm(self):
        self.boolfactor()
        while self.current_token and self.current_token.recognized_string == "and":
            self.match("KEYWORD", "and")
            self.boolfactor()

    # boolfactor : not [ condition ] | [ condition ] | expression REL_OP expression
    def boolfactor(self):
        if self.current_token and self.current_token.recognized_string == "not":
            self.match("KEYWORD", "not")
            self.match("SYMBOL", "[")
            self.condition()
            self.match("SYMBOL", "]")
        elif self.current_token and self.current_token.recognized_string == "[":
            self.match("SYMBOL", "[")
            self.condition()
            self.match("SYMBOL", "]")
        else:
            self.expression()
            # Now require a relational operator
            if (self.current_token and self.current_token.family == "OPERATOR" and 
                self.current_token.recognized_string in ("=", "<=", ">=", ">", "<", "<>")):
                op = self.current_token.recognized_string
                self.match("OPERATOR", op)
                self.expression()
            else:
                # Depending on design, one might allow an expression alone.
                # Here we follow the grammar strictly.
                raise SyntaxError("Expected relational operator in boolean factor.")

    # expression : optionalSign term ( ADD_OP term )*
    def expression(self, target=None):
        place = self.term(target=target)  # Forward target if possible.
    
        while (self.current_token and 
               self.current_token.family == "OPERATOR" and 
               self.current_token.recognized_string in ("+", "-")):
            op = self.current_token.recognized_string
            self.match("OPERATOR", op)
            right = self.term()  # For subsequent terms, you might not pass the target.
        
            # Check: if this is the last operation and a target is given, use it.
            if target is not None and not (self.current_token and 
                                            self.current_token.family == "OPERATOR" and 
                                            self.current_token.recognized_string in ("+", "-")):
                self.intermediate.genquad(op, place, right, target)
                place = target
            else:
                temp = self.intermediate.newtemp()
                self.intermediate.genquad(op, place, right, temp)
                place = temp
    
        return place

    def term(self, target=None):
        place = self.factor()
    
        while (self.current_token and 
               self.current_token.family == "OPERATOR" and 
               self.current_token.recognized_string in ("*", "/")):
            op = self.current_token.recognized_string
            self.match("OPERATOR", op)
            right = self.factor()
            if target is not None and not (self.current_token and 
                                            self.current_token.family == "OPERATOR" and 
                                            self.current_token.recognized_string in ("*", "/")):
                self.intermediate.genquad(op, place, right, target)
                place = target
            else:
                temp = self.intermediate.newtemp()
                self.intermediate.genquad(op, place, right, temp)
                place = temp
        return place

    def factor(self):
        # Simplest version for identifiers and numbers.
        if self.current_token.family in ("IDENTIFIER", "NUMBER"):
            value = self.current_token.recognized_string
            self.match(self.current_token.family)
            return value
        elif self.current_token.recognized_string == "(":
            self.match("SYMBOL", "(")
            place = self.expression()
            self.match("SYMBOL", ")")
            return place
        else:
            raise SyntaxError("Unexpected token in factor")
    # idtail : ( actualparlist ) | ε
    def idtail(self):
        if self.current_token and self.current_token.recognized_string == "(":
            self.match("SYMBOL", "(")
            self.actualparlist()
            self.match("SYMBOL", ")")

    # optionalSign : ADD_OP | ε
    def optionalSign(self):
        if self.current_token and self.current_token.family == "OPERATOR" and self.current_token.recognized_string in ("+", "-"):
            op = self.current_token.recognized_string
            self.match("OPERATOR", op)

###################################### INTERMEDIATE CODE GENERATOR #########################################
class IntermediateCodeGenerator:
    def __init__(self):
        # List to store quads; each quad is a tuple: (index, op, x, y, z)
        self.quads = []
        self.temp_count = 0
        self.next_quad_index = 0  # Start numbering from 100 (or 1 if preferred)

    def nextquad(self):
        """Returns the next available quad index."""
        return self.next_quad_index

    def genquad(self, op, x, y, z):
        """Creates a new quad with a unique index and appends it to the list."""
        quad = (self.next_quad_index, op, x, y, z)
        self.quads.append(quad)
        self.next_quad_index += 1  # Increase AFTER adding the quad
        return quad


    def newtemp(self):
        """Generates a new temporary variable in the form T_1, T_2, ..."""
        self.temp_count += 1
        return f"T_{self.temp_count}"

    def emptylist(self):
        """Returns an empty list used for backpatching."""
        return []

    def makelist(self, x):
        """Creates a list with a single quad index (used for backpatching)."""
        return [x]

    def merge(self, list1, list2):
        """Merges two lists of quad indices."""
        return list1 + list2

    def backpatch(self, lst, z):
        """Updates the fourth field (z) of each quad in the given list."""
        for index in lst:
            for i, quad in enumerate(self.quads):
                if quad[0] == index:
                    _, op, x, y, _ = quad
                    self.quads[i] = (index, op, x, y, z)
                    break  # Stop searching after finding the correct quad

    def print_quads(self):
        """Prints the list of quads in a structured format."""
        for quad in self.quads:
            print(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}")


if __name__ == "__main__":
    # Change "fibonacci.ci" to the path of your source file.
    lexer = LexerFSM("ci/testReturn.ci")
    print("Lexical analysis completed successfully.")
    tokens = lexer.tokenize()
    
    # Create an instance of the Intermediate Code Generator.
    intermediate = IntermediateCodeGenerator()
    
    # Pass the intermediate instance to the Parser.
    parser = Parser(tokens, intermediate)
    parser.program()
    print("Parsing completed successfully.")
    
    # Print out the generated quads.
    print("\nGenerated Intermediate Code (Quads):")
    intermediate.print_quads()

