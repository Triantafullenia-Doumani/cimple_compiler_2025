def execute_intermediate_code(file_path):
    memory = {}             # Stores variable values
    instructions = []       # List of instructions as tuples: (line_num, op, arg1, arg2, arg3)
    label_to_index = {}     # Maps a line number (label) to its index in the instructions list

    # Read the intermediate code from the file.
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Expecting each line to have the format: "line_num: op, arg1, arg2, arg3"
            parts = line.split(",")
            if len(parts) < 4:
                continue

            # Split the first part to extract the line number and operator.
            first_part = parts[0].strip()
            if ":" in first_part:
                num_str, op = first_part.split(":", 1)
                line_num = int(num_str.strip())
                op = op.strip()
            else:
                # Fallback if no colon is present.
                line_num = len(instructions)
                op = first_part.strip()
            
            arg1 = parts[1].strip()
            arg2 = parts[2].strip()
            arg3 = parts[3].strip()
            instructions.append((line_num, op, arg1, arg2, arg3))
            label_to_index[line_num] = len(instructions) - 1

    pc = 0  # Program counter
    while pc < len(instructions):
        line_num, op, arg1, arg2, arg3 = instructions[pc]

        # Debug: Uncomment the next line to print current instruction details.
        # print(f"PC: {pc} | Executing: {line_num}: {op}, {arg1}, {arg2}, {arg3}")

        if op in {"begin_block", "end_block"}:
            # Markers for block boundaries; no operation needed.
            pass

        elif op == "inp":
            # Read an integer input for the variable (arg1).
            memory[arg1] = int(input(f"Enter value for {arg1}: "))

        elif op == ":=":
            # Assignment: assign the value of arg1 to the variable given in arg3.
            try:
                # Try converting to integer first.
                value = int(arg1)
            except ValueError:
                try:
                    # Try converting to float if needed.
                    value = float(arg1)
                except ValueError:
                    # Otherwise, assume it is a variable name.
                    value = memory.get(arg1, 0)
            memory[arg3] = value

        elif op in {"+", "-", "*", "/"}:
            # Evaluate arithmetic operations.
            def get_value(s):
                try:
                    return int(s)
                except ValueError:
                    try:
                        return float(s)
                    except ValueError:
                        return memory.get(s, 0)
            x = get_value(arg1)
            y = get_value(arg2)
            if op == "+":
                result = x + y
            elif op == "-":
                result = x - y
            elif op == "*":
                result = x * y
            elif op == "/":
                # Use integer division for digit counting.
                result = get_value(arg1) // get_value(arg2)
            memory[arg3] = result

        elif op in {"<=", ">=", "<", ">", "=", "<>", "==", "!="}:
            # Handle relational operators.
            # Map "=" to "==" and "<>" to "!=" for Python evaluation.
            cmp_op = op
            if cmp_op == "=":
                cmp_op = "=="
            elif cmp_op == "<>":
                cmp_op = "!="

            def get_value(s):
                try:
                    return int(s)
                except ValueError:
                    try:
                        return float(s)
                    except ValueError:
                        return memory.get(s, 0)
            x = get_value(arg1)
            y = get_value(arg2)
            condition = eval(f"{x} {cmp_op} {y}")
            # If the condition is true, perform the jump.
            if condition:
                target_line = int(arg3)
                pc = label_to_index[target_line]
                continue  # Skip the usual pc increment

        elif op == "jump":
            # Unconditional jump: set program counter to the target line.
            target_line = int(arg3)
            pc = label_to_index[target_line]
            continue

        elif op == "out":
            # Output: print the value of arg1.
            try:
                output_value = int(arg1)
            except ValueError:
                try:
                    output_value = float(arg1)
                except ValueError:
                    output_value = memory.get(arg1, 0)
            print(output_value)

        elif op == "halt":
            break

        else:
            print(f"Unknown operator: {op}")

        pc += 1  # Move to the next instruction

if __name__ == "__main__":
    # Hardcoded file path to the intermediate code file
    file_path = "tests/int/exp_countDigits.int"
    execute_intermediate_code(file_path)
