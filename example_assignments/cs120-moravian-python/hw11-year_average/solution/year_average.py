user_year = input('Enter a year: ')

f_in = open('measles.txt')

percentages = []

for line in f_in:
    year = line[88:92].strip()
    if user_year == year:
        percentage = int(line[59:61].strip())
        percentages.append(percentage)

if len(percentages) == 0:
    print('No countries from that year')
else:
    print('There are', len(percentages), 'countries with data from that year.')
    print('The worldwide average is', sum(percentages) / len(percentages))
