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
    # Set of keywords in Cimple
    KEYWORDS = {
        "program", "declare", "if", "else", "while", "switchcase", "forcase", "incase",
        "case", "default", "not", "and", "or", "function", "procedure", "call", "return",
        "in", "inout", "input", "print"
    }

    # Operators and symbols
    OPERATORS = {"+", "-", "*", "/", "<", ">", "=", "<=", ">=", "<>", ":="}
    SEPARATORS = {";", ",", ":"}
    GROUPING_SYMBOLS = {"(", ")", "{", "}", "[", "]"}
    END_SYMBOL = "."

    # Define finite state machine (FSM) states
    START, IDENTIFIER, NUMBER, OPERATOR, SEPARATOR, COMMENT, ERROR = range(7)

    def __init__(self, file_path):
        """ Initializes the lexer with the given file path. """
        self.file_path = file_path
        self.tokens = []  # Stores recognized tokens
        self.current_line = 1  # Keeps track of line numbers

    def tokenize(self):
        """ Reads the input file and performs lexical analysis using an FSM. """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            text = file.read()  # Read full content

        state = self.START  # Begin in the START state
        i = 0  # Character index
        lexeme = ""  # Holds the current token being processed

        while i < len(text):  # Loop through all characters in the input file
            char = text[i]  # Get current character

            if state == self.START:
                """ START STATE: Determines the type of token and transitions accordingly. """
                if char in " \t\r":
                    # Ignore whitespace (stay in START state)
                    i += 1
                    continue
                if char == "\n":
                    # Track line numbers for better error reporting
                    self.current_line += 1
                    i += 1
                    continue
                if char.isalpha():
                    # Identifiers and keywords start with a letter
                    state = self.IDENTIFIER
                    lexeme = char  # Start capturing identifier/keyword
                elif char.isdigit():
                    # Numbers start with a digit
                    state = self.NUMBER
                    lexeme = char  # Start capturing number
                elif char in self.OPERATORS:
                    # Operators like +, -, *, /, etc.
                    state = self.OPERATOR
                    lexeme = char  # Start capturing operator
                elif char in self.SEPARATORS or char in self.GROUPING_SYMBOLS or char == self.END_SYMBOL:
                    # Separators and grouping symbols are standalone tokens
                    self.tokens.append(Token(char, "SYMBOL", self.current_line))
                    i += 1
                    continue  # Go to next character
                elif char == "#":
                    # Start of a comment
                    state = self.COMMENT
                else:
                    # If an unknown character is encountered, raise an error
                    raise ValueError(f"Error on line {self.current_line}: Unknown character '{char}'")

            elif state == self.IDENTIFIER:
                """ IDENTIFIER STATE: Builds up an identifier or keyword. """
                if char.isalnum():
                    # Continue building identifier (letters and digits allowed)
                    lexeme += char
                else:
                    # Identifier complete; check if it's a keyword
                    token_type = "KEYWORD" if lexeme in self.KEYWORDS else "IDENTIFIER"
                    self.tokens.append(Token(lexeme, token_type, self.current_line))
                    state = self.START  # Reset to START state
                    continue  # Reprocess the current character

            elif state == self.NUMBER:
                """ NUMBER STATE: Reads an integer token. """
                if char.isdigit():
                    # Continue building number
                    lexeme += char
                else:
                    # Number complete; add to tokens list
                    self.tokens.append(Token(lexeme, "NUMBER", self.current_line))
                    state = self.START  # Reset to START state
                    continue  # Reprocess the current character

            elif state == self.OPERATOR:
                """ OPERATOR STATE: Checks for multi-character operators. """
                two_char = lexeme + char  # Check if this is a two-character operator
                if two_char in self.OPERATORS:
                    # Multi-character operator recognized (like <=, >=, <>)
                    self.tokens.append(Token(two_char, "OPERATOR", self.current_line))
                    i += 1  # Move past the second character
                else:
                    # Single-character operator recognized
                    self.tokens.append(Token(lexeme, "OPERATOR", self.current_line))
                state = self.START  # Reset to START state
                continue  # Reprocess the current character

            elif state == self.COMMENT:
                """ COMMENT STATE: Skips everything inside #...# """
                if char == "#":
                    # End of comment
                    state = self.START
                i += 1  # Keep consuming characters within comment
                continue

            i += 1  # Move to the next character

        print("Lexical analysis completed successfully")
        return self.tokens  # Return the list of recognized tokens


# Example Usage
if __name__ == "__main__":
    lexer = LexerFSM("countDigits.ci")
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)
