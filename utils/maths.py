def pow10(exponent):
    return 10 ** exponent

WAD = pow10(18)

def w_mul_down(x, y):
    return mul_div_down(x, y, WAD)

def w_div_down(x, y):
    return mul_div_down(x, WAD, y)

def w_div_up(x, y):
    return mul_div_up(x, WAD, y)

def mul_div_down(x, y, d):
    if d == 0:
        raise ZeroDivisionError("Attempt to divide by zero in mul_div_down function")
    return (x * y) // d

def mul_div_up(x, y, d):
    if d == 0:
        raise ZeroDivisionError("Attempt to divide by zero in mul_div_up function")
    return (x * y + (d - 1)) // d

def min_(a, b):
    return min(a, b)

def max_(a, b):
    return max(a, b)

def w_taylor_compounded(x, n):
    first_term = x * n
    second_term = mul_div_down(first_term, first_term, 2 * WAD)
    third_term = mul_div_down(second_term, first_term, 3 * WAD)
    return first_term + second_term + third_term
