from math import ceil

amount = eval(input('Enter an amount of money: '))

bill_count = ceil(amount / 20)

print('You need', bill_count, 'twenty dollar bills.')

