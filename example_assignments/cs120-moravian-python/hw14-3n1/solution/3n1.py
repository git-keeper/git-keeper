val = eval(input("Enter a starting number: "))

length = 1

while(val != 1):
    print(val)
    if val % 2 == 1:
        val = 3 * val + 1
    else:
        val //= 2
    length += 1

# print the last value
print(1)
