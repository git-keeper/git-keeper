last_country = ''

f_in = open('measles.txt')
for line in f_in:
    country = line[:50].strip()
    if country != last_country:
        print(country)
        last_country = country

