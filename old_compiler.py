import re

memoryAddress = 5000
tRegister = 0
sRegister = 0
vars = dict()
stringLiterals = []  # Store string literals for data section
SubRLabels = 0
currentSubRLabels = []
label_map = dict()  # Track current active labels
expressions = []
strs = 0


end_command = """finish:
li $v0, 10          
syscall
"""


def getNewSubRLabel():
    global SubRLabels
    label = f"def{SubRLabels}"
    SubRLabels += 1
    currentSubRLabels.append(label)
    return label


def setVariableRegister(varName, tRegister):
    global vars
    vars[varName] = tRegister
    

def getVariableRegister(varName):
    global vars,tRegister
    if varName in vars:
        return vars[varName]
        
    else:
        # print(vars)
        # Initialize the variable if it doesn't exist
        tRegisterName = f"$t{tRegister}"
        setVariableRegister(varName, tRegisterName)
        tRegister +=1
        return tRegisterName

def getAssignmentLinesImmediateValue(val, varName):
    global tRegister
    reg = getVariableRegister(varName)
    outputText = f"""li {reg}, {val}"""
    tRegister += 1
    return outputText


def handleCondition(condition):
    global tRegister, strs
    outputText = ""
    
    # Handle modulus comparison (e.g., i % 15 == 0)
    if "%" in condition and "==" in condition:
        left, right = condition.split("==")
        left = left.strip()
        right = right.strip()
        
        numer, denom = left.split("%")
        denom = denom.strip()
        numer = numer.strip()
        # print(vars)
        # print(numer, " % ", denom)
        outputText += f"""div {vars[numer]}, {vars[denom]}
mfhi $s{++sRegister}\n
beq $s{sRegister}, $zero, def{strs}
"""
        
    
    return outputText


def handlePrintf(line, the_funcs):
    global stringLiterals, tRegister,strs
    outputText = ""
    
   
    # Extract the printf argument
    if 'printf(' in line:
        # Get content between parentheses
        content = line.split('printf(')[1].split(')')[0].strip()
        # Handle string literals
        if content.startswith('"') and content.endswith('"'):
            # Remove quotes and escape sequences
            string = content[1:-1].replace('\\n', '')  # Remove newline
            # Add to string literals if not already present
            if string not in stringLiterals:
                pass
    
            s = strs
            strs += 1
            the_funcs += f"""def{s}:
li $v0, 1
move $a0, $t0
syscall

li $v0, 4
la $a0, str_{s}
syscall
j next
"""

    
    return outputText, the_funcs

def parseIntDeclaration(line):
    # Remove 'int' and semicolon
    line = line.replace('int', '').strip().rstrip(';')
    
    # Skip main function declaration
    if 'main()' in line:
        return None, None
    
    # Handle initialization
    if '=' in line:
        var_name, value = line.split('=')
        var_name = var_name.strip()
        value = value.strip()
        return var_name, value
    else:
        # Just declaration without initialization
        return line.strip(), None

def handleForLoop(line):
    global tRegister
    outputText = ""
    # Map operators to their MIPS comparison instructions
    
    # Extract for loop components
    # Format: for(init; condition; increment)
    components = line.split("for")[1].strip().strip("()").split(";")
    init = components[0].strip()
    condition = components[1].strip()
    increment = components[2].strip()
    # Remove any characters after the closing parenthesis in increment
    increment = increment.split(")")[0]

    # Generate labels for loop control
    start_label = getNewSubRLabel()
    end_label = "finish\n"
    
    # opp_name = 
    # Generate initialization code
    if "=" in init:
        varName, val = init.split("=")
        varName = varName.strip()
        val = val.strip()
        

    # Add start label
    outputText += f"{start_label}:\n"
    
    # Generate condition check
    if "<=" in condition:
        left, right = condition.split("<=")
        left = left.strip()
        right = right.strip()
        
        # Get register for comparison
        reg = getVariableRegister(left)
        
        # Direct comparison with value
        outputText += f"bgt {reg}, {right}, {end_label}\n"
    
    return outputText, start_label, end_label

def remove_quoted_string(arg_string):
    # Replace anything inside "..." including the quotes
    return re.sub(r'"[^"]*"', '', arg_string).strip().strip(',').strip()


def main():
    global tRegister
    
    try:
        f = open("final_project/otherBuzz.c", "r")
        lines = f.readlines()
        outputText = ""
        the_funcs = "\n"
        current_loop_start = None
        current_loop_end = None
        
        # First pass: collect all string literals and variables
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
                
            # Collect variables from int declarations
            if line.startswith("int "):
                var_name, _ = parseIntDeclaration(line)
                if var_name:  # Only process if not main function
                    getVariableRegister(var_name)  # Initialize variable
            
            # Collect string literals from printf
            if 'printf(' in line:
                content = line.split('printf(')[1].split(')')[0].strip().replace("\\n","")
                # print("print content is: ",content)
                if content not in stringLiterals:
                        arg = content
                        var = remove_quoted_string(arg)
                       
                        if not vars.get(var): # Output: i
                            # print("adding ", arg)
                            stringLiterals.append(content)
                        getNewSubRLabel()
                        # print(currentSubRLabels)
                        
        
        # Add data section with string literals and newline
        outputText = ".data\n"
        outputText += "newline: .asciiz \"\\n\"\n"  # Add hard-coded newline string\
        # print("Strings ", stringLiterals)
        for i, string in enumerate(stringLiterals):
            outputText += f"str_{i}: .asciiz {string}\n"
        outputText += "\n.text\n"
        
        # Second pass: generate code
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):  # Skip empty lines and comments
                continue
                
            if line.startswith("int main() {"):
                outputText += "main:\n"
            elif line.startswith("for "):
                # Handle for loop
                loop_code, start_label, end_label = handleForLoop(line)
                current_loop_start = start_label
                current_loop_end = end_label
                outputText += loop_code
                
            elif line.startswith("if ") or line.startswith("} else if "):
                print(line)
                # Extract condition
                if line.startswith("if "):
                    condition = line.split("if")[1].strip().strip("()")
                else:  # else if
                    condition = line.split("else if")[1].strip().strip("()")
                
                # Generate label for else/end
                # else_label = getNewSubRLabel()
                # end_label = getNewSubRLabel()
                
                # Generate condition check
                
                outputText += handleCondition(condition)
                
              
                
            elif line.startswith("@"): #used to be }
                # Check if this is the end of a for loop
                if i > 0 and "++" in lines[i - 1]:
                    # This is the end of a for loop, add increment and jump back
                    increment_line = lines[i - 1].strip()
                    var = increment_line.split("++")[0].strip()
                    outputText += f"addi {getVariableRegister(var)}, {getVariableRegister(var)}, 1\n"
                    outputText += f"j {current_loop_start}\n"
                    outputText += f"{current_loop_end}:\n"
                else:
                    # This is the end of an if statement
                    outputText += f"j {end_label}\n"
                    outputText += f"{else_label}:\n"
                outputText += "\n"  # Add newline after each block
            # int declarations
            elif line.startswith("int "):
                var_name, value = parseIntDeclaration(line)
                if var_name:  # Only process if not main function
                    # outputText += getInstructionLine(var_name) + "\n"
                    if value is not None:
                        if value.isdigit():
                            outputText += getAssignmentLinesImmediateValue(value, var_name) + "\n"
                            pass
                        else:
                             pass
                            # outputText += getAssignmentLinesVariable(value, var_name) + "\n"
                        outputText += "\n"  # Add newline after variable declaration
            # assignments
            elif "@" in line:
                print(line)
                varName, _, val = line.partition("=")
                varName = varName.strip()
                val = val.strip().rstrip(';')
                print(val)
                # Check for modulus operation
                if "%" in val:
                    left, right = val.split("%")
                    left = left.strip()
                    right = right.strip()
                    # print( left, " % ", right)
                    # outputText += handleModulusOperation(left, right, varName) + "\n"
                elif val.isdigit():
                    # immediately value assignments
                    outputText += getAssignmentLinesImmediateValue(val, varName) + "\n"
                    pass
                else:
                    pass
                    # variable assignments
                    # outputText += getAssignmentLinesVariable(val, varName) + "\n"
                outputText += "\n"  # Add newline after assignment
            # printf statements
            elif "printf" in line:
                outputText_new, the_funcs_new = handlePrintf(line,the_funcs) 
                outputText+= outputText_new + "\n"
                the_funcs = the_funcs_new + "\n"
                outputText += "\n"  # Add newline after printf
            else:
                pass
        outputText += f"""li $v0, 1
move $a0, $t0
syscall\n
j next\n\n"""
        outputText += the_funcs
        outputText +=f"""next:
addi $t0, $t0, 1    

li $v0, 4
la $a0, newline
syscall
j {currentSubRLabels[-1]}\n\n"""
        


        outputText += end_command
        outputFile = open("output1.asm", "w")
        outputFile.write(outputText)
        outputFile.close()
        f.close()
        # print(vars)
        # print(currentSubRLabels)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if 'f' in locals():
            f.close()
        if 'outputFile' in locals():
            outputFile.close()

if __name__ == "__main__":
    main()