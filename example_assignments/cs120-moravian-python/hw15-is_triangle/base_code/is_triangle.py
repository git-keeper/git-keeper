# In a triangle, the some of the lengths of any pair of sides must be longer
# than the length of the third side.
#
# Complete the code for the function is_triangle(a, b, c). The function must
# return True if a, b, and c are valid side lengths for a triangle, and return
# False otherwise. Do not change any of the rest of the code!

def is_triangle(a, b, c):
    # complete the code for this function here


user_input = input('Enter a b c: ').split()

a = eval(user_input[0])
b = eval(user_input[1])
c = eval(user_input[2])

if is_triangle(a, b, c):
    print(a, b, c, 'forms a triangle')
else:
    print(a, b, c, 'does not form a triangle')
