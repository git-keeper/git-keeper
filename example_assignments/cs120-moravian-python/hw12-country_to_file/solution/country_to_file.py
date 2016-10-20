# Write a program which asks the user for a country and a filename to write.
# Read in measles.txt and write to the the filename that the user
# supplied. Make sure you don't write to measles.txt or you will overwrite it!
# For each line in measles.txt that contains the country that the user
# supplied, write a line in the output file with this format:
# country,year,percentage
#
# Make sure you strip off all surrounding whitespace. For example, if the user
# enters Viet Nam for the country and viet_nam.txt for the filename, then
# after your program runs the first few lines of viet_nam.txt should look like
# this:
#
# Viet Nam,1980,0
# Viet Nam,1981,0
# Viet Nam,1982,1
# Viet Nam,1983,3
# Viet Nam,1984,4
# Viet Nam,1985,19
# Viet Nam,1986,39
# ...

user_country = input('Enter a country: ')
filename = input('Enter a filename: ')

f_in = open('measles.txt')
f_out = open(filename, 'w')

for line in f_in:
    country = line[:50].strip()
    year = line[88:92].strip()
    percentage = line[59:61].strip()

    if country == user_country:
        line_out = country + ',' + year + ',' + percentage
        print(line_out, file=f_out)

f_in.close()
f_out.close()
