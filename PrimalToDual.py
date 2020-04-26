# if LP is maximizing the OF, then the symbol for duality is <=, which in terms of this program is -1 and 1 for >= if LP is minimizing the OF
def identify_MinMax(MinMax):
    if MinMax == [1]:
        duality_constrain_symbol = -1
        return duality_constrain_symbol
    else:
        duality_constrain_symbol = 1
        return duality_constrain_symbol

# multiply the constrains not in the right form by -1
def convert_constrain(A, b, Eqin, dcs):
    for m in range(len(A)):
        if dcs != Eqin[m]:
            A[m] = [A[m][k] * (-1) for k in range(len(A[m]))]
            b[m] = b[m] * (-1)
            Eqin[m] = Eqin[m] * (-1)

# create dual LP file
def dual_file(dual_LP_lines):
    with open('dual.txt', 'w') as f5:
        f5.writelines(dual_LP_lines)

# this is where the magic happens
def primal_to_dual_conversion(A, b, c, Eqin, MinMax):
    dual_LP_lines = []
    dcs = identify_MinMax(MinMax)

    zeros_index_list = []
    factors = []
    if there_is_equal_sign_in_constrains(Eqin):
        zeros_index_list = find_zeros_in_constrains(Eqin)
        factors = break_equality(A, b, Eqin, zeros_index_list)

    convert_constrain(A, b, Eqin, dcs)

    simplified_OF_part = ""
    simplified_con_part = []
    if factors:
        simplified_OF_part, simplified_con_part = simplification_after_breaking_equality(zeros_index_list, factors, A)

    # dual LP problem
    if MinMax == [1]:
        dual_LP_lines.append("min\n")
    else:
        dual_LP_lines.append("max\n")

    # dual LP OF
    k = len(A) - (len(zeros_index_list) * 2)
    s1 = "z ="
    if sum(b) != 0 or b[1] != 0:
        for i in range(k):
            if b[i] != 0 and i == 0:
                s1 = s1 + f" {b[i]}w{i + 1}"
            if b[i] > 0 and i != 0:
                s1 = s1 + f" +{b[i]}w{i + 1}"
            if b[i] < 0 and i != 0:
                s1 = s1 + f" {b[i]}w{i + 1}"
    else:
        s1 = s1 + " 0"
    s1 = s1 + simplified_OF_part
    dual_LP_lines.append(s1)

    # dual LP st
    dual_LP_lines.append("\nst\n")

    # dual LP constrains
    for m in range(len(A[0])):
        s2 = ""
        for n in range(k):
            if A[n][m] != 0 and n == 0:
                s2 = s2 + f" {A[n][m]}w{n + 1}"
            if A[n][m] > 0 and n != 0:
                s2 = s2 + f" +{A[n][m]}w{n + 1}"
            if A[n][m] < 0 and n != 0:
                s2 = s2 + f" {A[n][m]}w{n + 1}"
            if s2 == "":
                s2 = s2 + " 0"
        if s2 != " 0":
            s2 = s2 + simplified_con_part[m]
        if MinMax == [1]:
            s2 = s2 + f" >= {c[m]},\n"
        else:
            s2 = s2 + f" <= {c[m]},\n"
        if m == len(A[0]) - 1:
            s2 = s2.replace(",","")
        dual_LP_lines.append(s2)

    # dual LP end
    dual_LP_lines.append("end\n")

    # add remaining constrains
    add_physical_constrains(dual_LP_lines, zeros_index_list, factors, A)

    # create dual LP file
    dual_file(dual_LP_lines)

#-----------------------------------------------------------------------------------------------------------------------
# HANDLE EQUALITY

def there_is_equal_sign_in_constrains(Eqin):
    if 0 in Eqin:
        return True
    else:
        return False

# detect and find equality
def find_zeros_in_constrains(Eqin):
    zeros_index_list = []
    for index in range(len(Eqin)):
        if 0 == Eqin[index]:
            zeros_index_list.append(index)
    return zeros_index_list

# break = t0 <= and >=
def break_equality(A, b, Eqin, zeros_index_list):
    factors = []
    for i in zeros_index_list:
        A.append(A[i][:])
        b.append(b[i])
        Eqin.append(-1)
        A.append(A[i])
        b.append(b[i])
        Eqin.append(1)
        factors.append(b[i])

    i = 0
    while i < len(Eqin):
        if 0 == Eqin[i]:
            del A[i]
            del b[i]
            del Eqin[i]
            i = i - 1
        i = i + 1

    return factors

# return the factoring
def simplification_after_breaking_equality(zeros_index_list, factor, A):

    # simplify dual OF
    simplified_OF_part = ""
    for i in range(len(zeros_index_list)):
        if factor[i] > 0:
            simplified_OF_part = simplified_OF_part + f" +{factor[i]}a{i + 1}"
        if factor[i] < 0:
            simplified_OF_part = simplified_OF_part + f" {factor[i]}a{i + 1}"

    # simplify dual constrains
    simplified_con_part = []
    for j in range(len(A[0])):
        con_part = ""
        e = 0
        i = len(A) - (len(zeros_index_list) * 2)
        while i < len(A):
            if A[i][j] != 0 and i == 0:
                con_part = con_part + f" {A[i][j]}a{e + 1}"
            if A[i][j] > 0 and i != 0:
                con_part = con_part + f" +{A[i][j]}a{e + 1}"
            if A[i][j] < 0 and i != 0:
                con_part = con_part + f" {A[i][j]}a{e + 1}"
            i = i + 2
            e = e + 1
        simplified_con_part.append(con_part)

    return simplified_OF_part, simplified_con_part


def add_physical_constrains(dual_LP_lines, zeros_index_list, factor, A):
    s3 = "wk >= 0, (k = "
    for i in range(len(A)):
        s3 = s3 + f"{i + 1},"
    s3 = s3 + ")\n"
    dual_LP_lines.append(s3)

    if zeros_index_list:
        s4 = "al >= 0, (l = "
        for i in range(len(zeros_index_list)):
            s4 = s4 + f"{i + 1},"
        s4 = s4 + ")"
        dual_LP_lines.append(s4)

        k = len(A) - (len(zeros_index_list) * 2)
        s5 = " where:"
        j = 0
        for i in range(len(zeros_index_list)):
            if factor[i] > 0:
                s5 = s5 + f" a{i+1} = w{k + j + 1} - w{k + j + 2},"
            if factor[i] < 0:
                s5 = s5 + f" a{i+1} = w{k + j + 2} - w{k + j + 1},"
            j = j + 2
        dual_LP_lines.append(s5)