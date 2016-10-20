number_list = []

new_number = input('Enter a number for the list: ')

while new_number != '':
    number_list.append(eval(new_number))
    new_number = input('Enter a number for the list: ')

print('The smallest number is', min(number_list))
print('The largest number is', max(number_list))
print('The sum of the list is', sum(number_list))
print('The average of the list is', sum(number_list) / len(number_list))
