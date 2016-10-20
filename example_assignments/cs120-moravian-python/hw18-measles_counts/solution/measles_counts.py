# Write a program that prints out the name of each country from measles.txt
# that has never had a vaccination rate of above 90%.
#
# Here is a pseudo-code structure for your program:
#
# initialize an empty dictionary
# for each line in measles.txt:
#     extract the country and percentage from the line
#     if the country is not in the dictionary, add it with a value of 0
#     if the country's vaccination percentage is above 90, increment its value
# for each country in the dictionary:
#     if its value is 0, the country
#
# See the example code from class and in the book for further help.

f_in = open('measles.txt')

above_90_counts = {}

for line in f_in:
    country = line[:50].strip()
    percentage = int(line[59:61].strip())

    if country not in above_90_counts:
        above_90_counts[country] = 0

    if percentage > 90:
        above_90_counts[country] += 1
    
for country, count in above_90_counts.items():
    if count == 0:
        print(country)
