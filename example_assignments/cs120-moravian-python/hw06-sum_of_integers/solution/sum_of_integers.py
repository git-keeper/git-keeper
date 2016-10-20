# Write a program that asks the user for a positive integer n, and then
# calculates and prints the sum of all the positive integers up to and
# including n.
#
# For example, if the user enters 5, the program calculates 1 + 2 + 3 + 4 + 5
# and prints 15.

n = eval(input('Enter n: '))

the_sum = 0

for x in range(n + 1):
    the_sum += x

print(the_sum)
