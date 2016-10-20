from math import floor

total_days = eval(input('Enter a number of days: '))

weeks = floor(total_days / 7)

days = total_days % 7

print('That is', weeks, 'weeks and', days, 'days.')
