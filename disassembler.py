import re

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

INSTRUCTION_MAP_REV = {v: k for k, v in INSTRUCTION_MAP.items()}
REGISTERS_REV = {v: k for k, v in REGISTERS.items()}

INPUT_FILE = 'assembleroutput2.txt'
OUTPUT_FILE = 'disassembleroutput3.asm'

def bin_to_ascii(binary_str):
    chars = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]
    out = ''
    for c in chars:
        if c == '00000000':
            break
        out += chr(int(c, 2))
    return out

def collect_label_addresses(lines):
    label_addr_map = {}
    label_counter = 1
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        opcode = line[:6]
        instr = INSTRUCTION_MAP_REV.get(opcode)
        if instr in ['JMP', 'J']:
            address = int(line[6:22], 2)
            if address not in label_addr_map:
                label_addr_map[address] = f'method_{label_counter}'
                label_counter += 1
        elif instr in ['BGT', 'BEQ', 'BREQ', 'BRNEQ']:
            offset = int(line[16:32], 2)
            if offset not in label_addr_map:
                label_addr_map[offset] = f'method_{label_counter}'
                label_counter += 1
        elif instr == 'LA':
            label_addr = int(line[11:27], 2)
            if label_addr not in label_addr_map:
                label_addr_map[label_addr] = f'method_{label_counter}'
                label_counter += 1
    return label_addr_map

def disassemble():
    with open(INPUT_FILE, 'r') as infile:
        lines = infile.readlines()
    label_addr_map = collect_label_addresses(lines)
    with open(OUTPUT_FILE, 'w') as outfile:
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                outfile.write(line + '\n')
                continue
            # Convert WCO format to binary
            line = line.replace('W', '1').replace('O', '0')
            opcode = line[:6]
            instr = INSTRUCTION_MAP_REV.get(opcode)
            if instr:
                asm = instr
                if instr in ['ADD', 'SUB', 'MUL', 'OR', 'AND', 'REM']:
                    rd = REGISTERS.get(line[6:11], '$zero')
                    rs = REGISTERS.get(line[11:16], '$zero')
                    rt = REGISTERS.get(line[16:21], '$zero')
                    asm += f' {rd}, {rs}, {rt}'
                elif instr in ['LI', 'ADDI']:
                    rd = REGISTERS.get(line[6:11], '$zero')
                    if instr == 'LI':
                        imm = int(line[11:27], 2)
                        asm += f' {rd}, {imm}'
                    else:
                        rs = REGISTERS.get(line[11:16], '$zero')
                        imm = int(line[16:32], 2)
                        asm += f' {rd}, {rs}, {imm}'
                elif instr in ['MOVE']:
                    rd = REGISTERS.get(line[6:11], '$zero')
                    rs = REGISTERS.get(line[11:16], '$zero')
                    asm += f' {rd}, {rs}'
                elif instr in ['BGT', 'BEQ', 'BREQ', 'BRNEQ']:
                    rs = REGISTERS.get(line[6:11], '$zero')
                    rt = REGISTERS.get(line[11:16], '$zero')
                    offset = int(line[16:32], 2)
                    label = label_addr_map.get(offset, offset)
                    asm += f' {rs}, {rt}, {label}'
                elif instr in ['JMP', 'J']:
                    address = int(line[6:22], 2)
                    label = label_addr_map.get(address, address)
                    asm += f' {label}'
                elif instr in ['LOAD', 'STORE', 'KYAN']:
                    rt = REGISTERS.get(line[6:11], '$zero')
                    offset = int(line[11:27], 2)
                    rs = REGISTERS.get(line[27:32], '$zero')
                    asm += f' {rt}, {offset}({rs})'
                elif instr == 'ENZO':
                    r3 = REGISTERS.get(line[6:11], '$zero')
                    r2 = REGISTERS.get(line[11:16], '$zero')
                    r1 = REGISTERS.get(line[16:21], '$zero')
                    asm += f' {r3}, {r2}, {r1}'
                elif instr == 'TAIKI':
                    r1 = REGISTERS.get(line[6:11], '$zero')
                    asm += f' {r1}'
                elif instr == 'MAXX':
                    r1 = REGISTERS.get(line[6:11], '$zero')
                    asm += f' {r1}'
                elif instr in ['LA']:
                    rd = REGISTERS.get(line[6:11], '$zero')
                    label_addr = int(line[11:27], 2)
                    label = label_addr_map.get(label_addr, label_addr)
                    asm += f' {rd}, {label}'
                elif instr in ['SYSCALL']:
                    asm += ''
                else:
                    asm += ''
                outfile.write(asm + '\n')
            else:
                ascii_str = bin_to_ascii(line)
                if ascii_str:
                    outfile.write(f'.asciiz "{ascii_str}"\n')
                else:
                    outfile.write(f'# Unknown binary: {line}\n')

if __name__ == '__main__':
    disassemble()
