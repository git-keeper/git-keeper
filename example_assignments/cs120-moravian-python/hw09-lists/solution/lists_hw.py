word_count = eval(input('Enter the number of numbers that will be in the list: '))

number_list = []

for i in range(word_count):
    new_number = eval(input('Enter a number for the list: '))
    number_list.append(new_number)

print('The smallest number is', min(number_list))
print('The largest number is', max(number_list))
print('The sum of the list is', sum(number_list))
print('The average of the list is', sum(number_list) / len(number_list))
