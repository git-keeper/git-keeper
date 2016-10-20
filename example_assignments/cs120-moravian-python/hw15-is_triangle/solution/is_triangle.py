# Complete the code for the function is_triangle(a, b, c). The function must
# return True if a, b, and c are valid side lengths for a triangle, and return
# False otherwise.

def is_triangle(a, b, c):
    return a + b > c and a + c > b and b + c > a


user_input = input('Enter a b c: ').split()

a = eval(user_input[0])
b = eval(user_input[1])
c = eval(user_input[2])

if is_triangle(a, b, c):
    print(a, b, c, 'forms a triangle')
else:
    print(a, b, c, 'does not form a triangle')
