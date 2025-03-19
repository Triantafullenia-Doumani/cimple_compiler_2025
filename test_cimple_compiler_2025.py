import unittest
import os
from cimple_compiler_2025 import LexerFSM, Parser, IntermediateCodeGenerator  # Replace with your actual module name

class TestCompiler(unittest.TestCase):
    
    def test_factorial_file(self):
        # Run the compiler on the factorial file.
        input_file = "tests/ci/factorial.ci"
        lexer = LexerFSM(input_file)
        tokens = lexer.tokenize()
        intermediate = IntermediateCodeGenerator()
        parser = Parser(tokens, intermediate)
        parser.program()
        
        # Write the generated quads to the .int file in the 'int/' folder.
        output_folder = "int"
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, "factorial.int")
        with open(output_filename, "w", encoding="utf-8") as file:
            for quad in intermediate.quads:
                file.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
        
        # Read the generated file.
        with open(output_filename, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # Read the expected output from the expected file.
        expected_filename = "tests/int/exp_factorial.int"
        with open(expected_filename, "r", encoding="utf-8") as file:
            expected_output = file.read()
        
        self.assertEqual(file_content, expected_output)

    def test_countDigits_file(self):
        # Run the compiler on the countDigits.ci"
        input_file = "tests/ci/countDigits.ci"
        lexer = LexerFSM(input_file) 
        lexer = LexerFSM(input_file)
        tokens = lexer.tokenize()
        intermediate = IntermediateCodeGenerator()
        parser = Parser(tokens, intermediate)
        parser.program()
        
        # Write the generated quads to the .int file in the 'int/' folder.
        output_folder = "int"
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, "countDigits.int")
        with open(output_filename, "w", encoding="utf-8") as file:
            for quad in intermediate.quads:
                file.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
        
        # Read the generated file.
        with open(output_filename, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # Read the expected output from the expected file.
        expected_filename = "tests/int/exp_countDigits.int"
        with open(expected_filename, "r", encoding="utf-8") as file:
            expected_output = file.read()
        
        self.assertEqual(file_content, expected_output)

    def test_testAddition_file(self):
        # Run the compiler on the testAddition.ci"
        input_file = "tests/ci/testAddition.ci"
        lexer = LexerFSM(input_file) 
        lexer = LexerFSM(input_file)
        tokens = lexer.tokenize()
        intermediate = IntermediateCodeGenerator()
        parser = Parser(tokens, intermediate)
        parser.program()
        
        # Write the generated quads to the .int file in the 'int/' folder.
        output_folder = "int"
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, "testAddition.int")
        with open(output_filename, "w", encoding="utf-8") as file:
            for quad in intermediate.quads:
                file.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
        
        # Read the generated file.
        with open(output_filename, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # Read the expected output from the expected file.
        expected_filename = "tests/int/exp_testAddition.int"
        with open(expected_filename, "r", encoding="utf-8") as file:
            expected_output = file.read()
        
        self.assertEqual(file_content, expected_output)


    def test_testFunction_file(self):
        # Run the compiler on the testFunction.ci"
        input_file = "tests/ci/testFunction.ci"
        lexer = LexerFSM(input_file) 
        lexer = LexerFSM(input_file)
        tokens = lexer.tokenize()
        intermediate = IntermediateCodeGenerator()
        parser = Parser(tokens, intermediate)
        parser.program()
        
        # Write the generated quads to the .int file in the 'int/' folder.
        output_folder = "int"
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, "testFunction.int")
        with open(output_filename, "w", encoding="utf-8") as file:
            for quad in intermediate.quads:
                file.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
        
        # Read the generated file.
        with open(output_filename, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # Read the expected output from the expected file.
        expected_filename = "tests/int/exp_testFunction.int"
        with open(expected_filename, "r", encoding="utf-8") as file:
            expected_output = file.read()
        
        self.assertEqual(file_content, expected_output)

    def test_testReturn_file(self):
        # Run the compiler on the testReturn.ci"
        input_file = "tests/ci/testReturn.ci"
        lexer = LexerFSM(input_file) 
        lexer = LexerFSM(input_file)
        tokens = lexer.tokenize()
        intermediate = IntermediateCodeGenerator()
        parser = Parser(tokens, intermediate)
        parser.program()
        
        # Write the generated quads to the .int file in the 'int/' folder.
        output_folder = "int"
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, "testReturn.int")
        with open(output_filename, "w", encoding="utf-8") as file:
            for quad in intermediate.quads:
                file.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
        
        # Read the generated file.
        with open(output_filename, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # Read the expected output from the expected file.
        expected_filename = "tests/int/exp_testReturn.int"
        with open(expected_filename, "r", encoding="utf-8") as file:
            expected_output = file.read()

    def test_testIf_file(self):
        # Run the compiler on the testIf.ci"
        input_file = "tests/ci/testIf.ci"
        lexer = LexerFSM(input_file) 
        lexer = LexerFSM(input_file)
        tokens = lexer.tokenize()
        intermediate = IntermediateCodeGenerator()
        parser = Parser(tokens, intermediate)
        parser.program()
        
        # Write the generated quads to the .int file in the 'int/' folder.
        output_folder = "int"
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, "testIf.int")
        with open(output_filename, "w", encoding="utf-8") as file:
            for quad in intermediate.quads:
                file.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
        
        # Read the generated file.
        with open(output_filename, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # Read the expected output from the expected file.
        expected_filename = "tests/int/exp_testIf.int"
        with open(expected_filename, "r", encoding="utf-8") as file:
            expected_output = file.read()

    def test_calculator(self):
        # Run the compiler on the calculator.ci"
        input_file = "tests/ci/calculator.ci"
        lexer = LexerFSM(input_file) 
        lexer = LexerFSM(input_file)
        tokens = lexer.tokenize()
        intermediate = IntermediateCodeGenerator()
        parser = Parser(tokens, intermediate)
        parser.program()
        
        # Write the generated quads to the .int file in the 'int/' folder.
        output_folder = "int"
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, "calculator.int")
        with open(output_filename, "w", encoding="utf-8") as file:
            for quad in intermediate.quads:
                file.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
        
        # Read the generated file.
        with open(output_filename, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # Read the expected output from the expected file.
        expected_filename = "tests/int/exp_calculator.int"
        with open(expected_filename, "r", encoding="utf-8") as file:
            expected_output = file.read()        
        self.assertEqual(file_content, expected_output)

    def test_fibonacci(self):
        # Run the compiler on the fibonacci.ci"
        input_file = "tests/ci/fibonacci.ci"
        lexer = LexerFSM(input_file) 
        lexer = LexerFSM(input_file)
        tokens = lexer.tokenize()
        intermediate = IntermediateCodeGenerator()
        parser = Parser(tokens, intermediate)
        parser.program()
        
        # Write the generated quads to the .int file in the 'int/' folder.
        output_folder = "int"
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, "fibonacci.int")
        with open(output_filename, "w", encoding="utf-8") as file:
            for quad in intermediate.quads:
                file.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
        
        # Read the generated file.
        with open(output_filename, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # Read the expected output from the expected file.
        expected_filename = "tests/int/exp_fibonacci.int"
        with open(expected_filename, "r", encoding="utf-8") as file:
            expected_output = file.read()        
        self.assertEqual(file_content, expected_output)


    def test_testCall(self):
        # Run the compiler on the testCall.ci"
        input_file = "tests/ci/testCall.ci"
        lexer = LexerFSM(input_file) 
        lexer = LexerFSM(input_file)
        tokens = lexer.tokenize()
        intermediate = IntermediateCodeGenerator()
        parser = Parser(tokens, intermediate)
        parser.program()
        
        # Write the generated quads to the .int file in the 'int/' folder.
        output_folder = "int"
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, "testCall.int")
        with open(output_filename, "w", encoding="utf-8") as file:
            for quad in intermediate.quads:
                file.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
        
        # Read the generated file.
        with open(output_filename, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # Read the expected output from the expected file.
        expected_filename = "tests/int/exp_testCall.int"
        with open(expected_filename, "r", encoding="utf-8") as file:
            expected_output = file.read()        
        self.assertEqual(file_content, expected_output)
if __name__ == "__main__":
    unittest.main()
