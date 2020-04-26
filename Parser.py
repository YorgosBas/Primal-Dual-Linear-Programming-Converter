import re
from PrimalToDual import primal_to_dual_conversion
#-----------------------------------------------------------------------------------------------------------------------

# Read file
def read_file():
    with open("Primal.txt", "r", encoding='utf-8-sig') as f:
        # Read and append each raw line into a list
        lines = f.read().splitlines()
    # Merge the raw list into a string
    line = "".join(lines)
    # Split each character in the string and remove special characters such as tabs, newlines and spaces
    line = line.split()
    # Merge the list into a string of lowercase letters
    line = "".join(line).lower()
    return line


# Check if max or min, subject to and commas exist and then modify the string
def modify_file(line):
    if "max" in line:
        line = line.replace("max", "max\n")
    elif "min" in line:
        line = line.replace("min", "min\n")
    else:
        print("max or min is missing from the linear problem")
    # Check if st or s.t. or subject exist and then modify the string
    if "st" in line:
        line = line.replace("st", "\nst\n")
    elif "s.t." in line:
        line = line.replace("s.t.", "\ns.t.\n")
    elif "subject" in line:
        line = line.replace("subject to", "\nsubject to\n")
    else:
        print("subject to is missing from the linear problem")
    # Check the end of the linear problem and modify the string
    if "end" in line:
        line = line.replace("end", "\nend")
    # Check commas and modify the string
    if "," in line:
        line = line.replace(",", "\n")
    return line

#-----------------------------------------------------------------------------------------------------------------------

# Check if max or min is before the objective function
def MinMax_before_OF(modified_lines):
    if ("max" in modified_lines[0]) or ("min" in modified_lines[0]) and is_of(modified_lines):
        return True
    else:
        print("max or min is not before the objective function or does not exist")
        return False

# Check if it is an objective function
# If range is empty then it is not an objective function
def is_of(modified_lines):
    return bool(objective_function_range(modified_lines))

# Get the range of the objective function in terms of variables
def objective_function_range(modified_lines):
    of_range = []
    if bool(re.match("^[a-z]", modified_lines[1])):
        if bool(re.match("^[a-z]=", modified_lines[1])):
            if not bool(re.match("^[a-z]==", modified_lines[1])):
                of_range = re.findall("x(\d+)", modified_lines[1][2:])
                if not of_range:
                    print("Objective Function is equal to a number")
            else:
                print("Objective Function is not declared properly")
        else:
            print("Objective Function is missing the equal (=) sign or there is more than one declaration variable")
    else:
        print("Objective Function is missing declaration variable")
    return of_range


# Check if subject to is before constrains
def st_before_constrains(modified_lines):
    if ("st" in modified_lines[2]) or ("s.t." in modified_lines[2]) or ("subject to" in modified_lines[2]) and is_constrain(modified_lines):
        return True
    else:
        print("subject to is not before the constrains")
        return False

# Check if it is a constrain
# If range is 0 then there are no variables. This means it is not a constrain
def is_constrain(modified_lines):
    return bool(constrain_range(modified_lines, 3))

def constrain_range(modified_lines, index):
    if bool(re.findall("x(\d+)", modified_lines[index])):
        con_range = re.findall("x(\d+)", modified_lines[index])
    else:
        print("constrain is not declared properly")
        con_range = []
    return con_range


# Check if signs are missing from the objective function
def signs_missing_from_of(modified_lines):
    error = False
    matched = False
    of_range = objective_function_range(modified_lines)
    next_group_index = 2
    temp_group = modified_lines[1][next_group_index:]
    for variables in range(len(of_range)):
        if variables == 0:
            matched = re.match("^([-+]?)((\d+(\.\d+)?)?)(\*?)x(\d+)", temp_group)
        else:
            if temp_group[0] == "+":
                matched = re.match("^\+((\d+(\.\d+)?)?)(\*?)x(\d+)", temp_group)
            elif temp_group[0] == "-":
                matched = re.match("^-((\d+(\.\d+)?)?)(\*?)x(\d+)", temp_group)
            else:
                print(f"Sign of variable x{of_range[variables]} is missing ")
                error = True
        if bool(matched):
            next_group_index = modified_lines[1].find(f"x{of_range[variables]}") + len(of_range[variables]) + 1
            temp_group = modified_lines[1][next_group_index:]
            matched = False
        else:
            next_group_index = modified_lines[1].find(f"x{of_range[variables]}") + len(of_range[variables]) + 1
            temp_group = modified_lines[1][next_group_index:]
    return error


# Check if signs are missing from the constrains
def signs_missing_from_con(modified_lines):
    error = False
    for m in range(3, len(modified_lines) - 1):
        matched = False
        con_range = constrain_range(modified_lines, m)
        variables = 0
        next_group_index = 0
        temp_group = modified_lines[m][next_group_index:]
        while variables < len(con_range):
            if variables == 0:
                matched = re.match("^([-+]?)((\d+(\.\d+)?)?)(\*?)x(\d+)", temp_group)
            if variables != 0:
                if temp_group[0] == "+":
                    matched = re.match("^\+((\d+(\.\d+)?)?)(\*?)x(\d+)", temp_group)
                elif temp_group[0] == "-":
                    matched = re.match("^-((\d+(\.\d+)?)?)(\*?)x(\d+)", temp_group)
                else:
                    print(f"Sign of variable x{con_range[variables]} is missing ")
                    error = True
            if bool(matched):
                next_group_index = modified_lines[m].find(f"x{con_range[variables]}") + len(con_range[variables]) + 1
                temp_group = modified_lines[m][next_group_index:]
                matched = False
            else:
                next_group_index = modified_lines[m].find(f"x{con_range[variables]}") + len(con_range[variables]) + 1
                temp_group = modified_lines[m][next_group_index:]
            variables = variables + 1
    return error

# Check if symbols are missing from constrains
def symbol_missing_from_con(modified_lines):
    error = False
    for m in range(3, len(modified_lines) - 1):
        if not((">=" in modified_lines[m]) or ("=" in modified_lines[m]) or ("<=" in modified_lines[m])):
            print(f"symbol is missing from constrain {modified_lines[m]}")
            error = True
    return error

# Check if right part is missing from constrains
def right_part_missing_from_con(modified_lines):
    error = False
    for m in range(3, len(modified_lines) - 1):
        if re.findall(">=", modified_lines[m]):
            index = modified_lines[m].find("=")
        elif re.findall("=", modified_lines[m]):
            index = modified_lines[m].find("=")
        elif re.findall("<=", modified_lines[m]):
            index = modified_lines[m].find("=")
        else:
            print(f"can not find right part at {modified_lines[m]}. Symbol is required")
            break
        right_part = modified_lines[m][index + 1:]
        if not re.findall("\d", right_part):
            print(f"right part is missing from constrain {modified_lines[m]}")
            error = True
    return error

# Find the maximum variable
def global_range(modified_lines):
    max = 0
    for m in range(3, len(modified_lines) - 1):
        con_range = constrain_range(modified_lines, m)
        if max < int(con_range[-1]):
            max = int(con_range[-1])
    of_range = objective_function_range(modified_lines)
    if int(of_range[-1]) > max:
        max = of_range[-1]
    return max

#-----------------------------------------------------------------------------------------------------------------------

# Check if the equation is Maximizing or Minimizing the linear problem
def extract_MinMax(modified_lines):
    if "max" in modified_lines[0]:
        return [1]
    elif "min" in modified_lines[0]:
        return [-1]

# Extract coefficients from the constrains
def extract_constrain_coefficients(modified_lines, range1):
    list = []
    for m in range(3, len(modified_lines) - 1):
        con_range = constrain_range(modified_lines, m)
        matched = []
        variables = 0
        next_group_index = 0
        temp_group = modified_lines[m][next_group_index:]
        index = 0
        while variables < int(range1):
            try:
                if f"x{con_range[index]}" == f"x{variables+1}":
                    if temp_group[0] == "x":
                        matched.insert(variables, +1)
                    if temp_group[0] == "-" and temp_group[1] == "x":
                        matched.insert(variables, -1)
                    if temp_group[0] == "+" and temp_group[1] == "x":
                        matched.insert(variables, +1)
                    temp_matched = re.findall("^[+-]?\d*\.?\d+", temp_group)
                    if bool(temp_matched):
                        matched.append(int(temp_matched[0]))
                        next_group_index = modified_lines[m].find(f"x{con_range[index]}") + len(con_range[index]) + 1
                        temp_group = modified_lines[m][next_group_index:]
                    else:
                        next_group_index = modified_lines[m].find(f"x{con_range[index]}") + len(con_range[index]) + 1
                        temp_group = modified_lines[m][next_group_index:]
                    index = index + 1
                else:
                    matched.append(0)
            except IndexError:
                matched.append(0)
            variables = variables + 1
        list.append(matched)
    return list


# Extract the right parts from the constrains
def extract_right_parts(modified_lines):
    list = []
    for m in range(3, len(modified_lines) - 1):
        index = modified_lines[m].find("=")
        right_part = modified_lines[m][index + 1:]
        list.append(int(right_part))
    return list


# Extract coefficients from objective function
def extract_of_coefficients(modified_lines, range1):
    of_range = objective_function_range(modified_lines)
    matched = []
    variables = 0
    next_group_index = 2
    temp_group = modified_lines[1][next_group_index:]
    index = 0
    while variables < int(range1):
        try:
            if f"x{of_range[index]}" == f"x{variables + 1}":
                if temp_group[0] == "x":
                    matched.insert(variables, +1)
                if temp_group[0] == "-" and temp_group[1] == "x":
                    matched.insert(variables, -1)
                if temp_group[0] == "+" and temp_group[1] == "x":
                    matched.insert(variables, +1)
                temp_matched = re.findall("^[+-]?\d*\.?\d+", temp_group)
                if bool(temp_matched):
                    matched.append(int(temp_matched[0]))
                    next_group_index = modified_lines[1].find(f"x{of_range[index]}") + len(of_range[index]) + 1
                    temp_group = modified_lines[1][next_group_index:]
                else:
                    next_group_index = modified_lines[1].find(f"x{of_range[index]}") + len(of_range[index]) + 1
                    temp_group = modified_lines[1][next_group_index:]
                index = index + 1
            else:
                matched.append(0)
        except IndexError:
            matched.append(0)
        variables = variables + 1
    return matched

# Extract the symbols from the constrains
def extract_constrain_symbols(modified_lines):
    list = []
    for m in range(3, len(modified_lines) - 1):
        if re.findall(">=", modified_lines[m]):
            list.append(1)
        elif re.findall("<=", modified_lines[m]):
            list.append(-1)
        elif re.findall("=", modified_lines[m]):
            list.append(0)
    return list

def write_parsed_file(A, b, c, Eqin, MinMax):
    A = '\n'.join('constraint {}: {}'.format(*k) for k in enumerate(A))
    b = '\n'.join('constraint {}: {}'.format(*k) for k in enumerate(b))
    Eqin = '\n'.join('constraint {}: {}'.format(*k) for k in enumerate(Eqin))
    with open('parsed_file.txt', 'w') as f3:
        f3.write(f"A=\n{A}\nb=\n{b}\nc=\n{c}\nEqin=\n{Eqin}\nMinMax=\n{MinMax}\n")

#-----------------------------------------------------------------------------------------------------------------------

def main():

    line = read_file()
    modified = modify_file(line)
    modified_lines = modified.splitlines()
    print(modified_lines)

    range = global_range(modified_lines)
    passed1 = MinMax_before_OF(modified_lines)
    passed2 = st_before_constrains(modified_lines)

    error1 = signs_missing_from_of(modified_lines)
    error2 = signs_missing_from_con(modified_lines)
    error3 = symbol_missing_from_con(modified_lines)
    error4 = right_part_missing_from_con(modified_lines)

    if passed1 and passed2 and not error1 and not error2 and not error3 and not error4:
        A = extract_constrain_coefficients(modified_lines, range)
        b = extract_right_parts(modified_lines)
        c = extract_of_coefficients(modified_lines, range)
        Eqin = extract_constrain_symbols(modified_lines)
        MinMax = extract_MinMax(modified_lines)
        write_parsed_file(A, b, c, Eqin, MinMax)

        primal_to_dual_conversion(A, b, c, Eqin, MinMax)



if __name__ == '__main__':
    main()