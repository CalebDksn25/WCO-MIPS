import sys
import re
import os

# WCO INSTRUCTIONS
INSTRUCTION_MAP = {
    'ADD': '100000',
    'SUB': '100010',
    'MUL': '100100',
    'OR': '101010',
    'AND': '100101',
    'LOAD': '101111',
    'STORE': '101110',
    'JMP': '110000',
    'BREQ': '110001',
    'BRNEQ': '110010',
    'ADAM': '111000',
    'DOM': '111100',
    'BRAYDON': '111110',
    'ENZO': '111111',
    'CALEB': '011111',
    'TAIKI': '001111',
    'ADDIB': '000111',
    'KYAN': '000011',
    'MAXX': '000001',
    'LUKE': '000000',
    'LI': '100011',      
    'BGT': '100110',  
    'REM': '100111',       
    'BEQ': '101000',      
    'ADDI': '101001',      
    'MOVE': '101010',     
    'LA': '101011',        
    'SYSCALL': '101100',   
    'J': '110000',
}

REGISTERS = {
    "00000": "$zero",
    "01001": "$t1",
    "01010": "$t2",
    "01011": "$t3",
    "01100": "$t4",
    "01101": "$t5",
    "01110": "$t6",
    "01111": "$t7",
    "10000": "$s0",
    "10001": "$s1",
    "10010": "$s2",
    "10011": "$s3",
    "10100": "$s4",
    "10101": "$s5",
    "10110": "$s6",
    "10111": "$s7",
}

# Reverse register map for lookup by name
REGISTERS_REV = {v: k for k, v in REGISTERS.items()}

INPUT_FILE = 'input.wco'
OUTPUT_FILE = 'assembleroutput1.txt'

def parse_register(reg):
    reg = reg.strip()
    return REGISTERS_REV.get(reg, '00000')  # Default to $zero if not found

def parse_immediate(imm):
    try:
        return format(int(imm), '016b')  # 16-bit immediate
    except ValueError:
        return '0' * 16

def assemble():
    label_positions = {}
    label_method_map = {}
    instructions = []  # List of (original_line, instruction_line)
    asciiz_data = []   # List of (label, binary_string)
    method_counter = 1
    with open(INPUT_FILE, 'r') as infile:
        instruction_index = 0
        for line in infile:
            original_line = line.rstrip('\n')
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Handle .asciiz
            if '.asciiz' in line:
                parts = line.split('.asciiz')
                label = parts[0].split(':')[0].strip() if ':' in parts[0] else ''
                string_part = parts[1].strip()
                if string_part.startswith('"') and string_part.endswith('"'):
                    string_content = string_part[1:-1]
                else:
                    string_content = string_part
                string_content = bytes(string_content, "utf-8").decode("unicode_escape")
                binary_string = ''.join([format(ord(c), '08b') for c in string_content])
                binary_string += '00000000'  # Null terminator
                asciiz_data.append((label, binary_string))
                continue
            if line.startswith('.'):
                continue
            if line.endswith(':'):
                label = line[:-1]
                label_positions[label] = instruction_index
                label_method_map[label] = f'method_{method_counter}'
                method_counter += 1
                continue
            instructions.append((original_line, line))
            instruction_index += 1

    # Reverse map: method label to method number (for binary encoding)
    method_label_to_num = {v: i+1 for i, v in enumerate(label_method_map.values())}
    label_to_method_num = {label: method_label_to_num[mlabel] for label, mlabel in label_method_map.items()}

    # Second pass: assemble instructions
    with open(OUTPUT_FILE, 'w') as outfile:
        # Write asciiz data first
        for label, binary_string in asciiz_data:
            if label:
                outfile.write(f'# {label} (asciiz)\n')
            # Replace 0's with O's and 1's with W's for ascii data
            binary_string = binary_string.replace('0', 'O').replace('1', 'W')
            outfile.write(binary_string + '\n')
        for idx, (original_line, line) in enumerate(instructions):
            tokens = re.split(r'[\s,]+', line)
            print(f"Processing: {tokens}")
            instr = tokens[0].upper()
            opcode = INSTRUCTION_MAP.get(instr)
            if not opcode:
                outfile.write(f'# Unknown instruction: {original_line}\n')
                continue
            binary = opcode
            if instr in ['ADD', 'SUB', 'MUL', 'OR', 'AND', 'REM']:
                rd = parse_register(tokens[1])
                rs = parse_register(tokens[2])
                rt = parse_register(tokens[3])
                binary += rd + rs + rt
            elif instr in ['LI', 'ADDI']:
                rd = parse_register(tokens[1])
                if len(tokens) == 3:
                    imm = parse_immediate(tokens[2])
                    binary += rd + imm
                else:
                    rs = parse_register(tokens[2])
                    imm = parse_immediate(tokens[3])
                    binary += rd + rs + imm
            elif instr in ['MOVE']:
                rd = parse_register(tokens[1])
                rs = parse_register(tokens[2])
                binary += rd + rs
            elif instr in ['BGT', 'BEQ', 'BREQ', 'BRNEQ']:
                rs = parse_register(tokens[1])
                rt = parse_register(tokens[2])
                offset_token = tokens[3] if len(tokens) > 3 else '0'
                if offset_token in label_to_method_num:
                    offset = format(label_to_method_num[offset_token], '016b')
                elif offset_token in label_positions:
                    offset = format(label_positions[offset_token], '016b')
                else:
                    offset = parse_immediate(offset_token)
                binary += rs + rt + offset
            elif instr in ['JMP', 'J']:
                address_token = tokens[1] if len(tokens) > 1 else '0'
                if address_token in label_to_method_num:
                    address = format(label_to_method_num[address_token], '016b')
                elif address_token in label_positions:
                    address = format(label_positions[address_token], '016b')
                else:
                    address = parse_immediate(address_token)
                binary += address
            elif instr in ['LOAD', 'STORE', 'KYAN']:
                rt = parse_register(tokens[1])
                match = re.match(r'(-?\d+)\((\$\w+)\)', tokens[2])
                if match:
                    offset = parse_immediate(match.group(1))
                    rs = parse_register(match.group(2))
                else:
                    offset = '0' * 16
                    rs = '00000'
                binary += rt + offset + rs
            elif instr == 'BRAYDON':
                # BRAYDON duration (immediate)
                duration = parse_immediate(tokens[1])
                binary += duration
            elif instr == 'ENZO':
                # ENZO $r3, $r2, $r1
                r3 = parse_register(tokens[1])
                r2 = parse_register(tokens[2])
                r1 = parse_register(tokens[3])
                binary += r3 + r2 + r1
            elif instr == 'TAIKI':
                # TAIKI $r1
                r1 = parse_register(tokens[1])
                binary += r1
            elif instr == 'MAXX':
                # MAXX $r1
                r1 = parse_register(tokens[1])
                binary += r1
            elif instr == 'LUKE':
                # LUKE (no operands)
                pass  # Only opcode
            elif instr == 'LA':
                rd = parse_register(tokens[1])
                label = tokens[2] if len(tokens) > 2 else '0'
                if label in label_to_method_num:
                    label_bin = format(label_to_method_num[label], '016b')
                elif label in label_positions:
                    label_bin = format(label_positions[label], '016b')
                else:
                    label_bin = parse_immediate(label)
                binary += rd + label_bin
            elif instr == 'SYSCALL':
                binary += '0' * 21
            else:
                binary += '0' * 21
            binary = binary.ljust(32, '0')[:32]
            # Replace 0's with O's and 1's with W's
            binary = binary.replace('0', 'O').replace('1', 'W')
            outfile.write(binary + '\n')

if __name__ == '__main__':
    assemble()
