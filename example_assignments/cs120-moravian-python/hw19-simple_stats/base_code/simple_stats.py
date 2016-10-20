# Here is my solution for homework 13. Your task is to rewrite the code so that
# the number list is stored in a class called SimpleStats, and the min, max,
# sum, and average are obtained through the class's methods.
#
# Here is a UML diagram for SimpleStats:
#
#   +-----------------------------------+
#   |            SimpleStats            |
#   +-----------------------------------+
#   | get_min(): float or int           |
#   | get_max(): float or int           |
#   | get_sum(): float or int           |
#   | get_average(): float              |
#   | add_value(value: float)           |
#   +-----------------------------------+
#   | number_list: list of strings      |
#   +-----------------------------------+
#
# The constructor for SimpleStats simply needs to initialize self.number_list
# as an empty list.
#
# get_min() will return min(self.number_list), get_max() will return
# max(self.number_list), etc.
#
# In place of creating a list to put the number into, create a new SimpleStats
# object like so:  stats = SimpleStats()
#
# Then you can add each new number by calling stats.add_value(eval(new_number))
#
# You'll print each stat by calling stats.get_min(), etc.
#
# To get full credit your tests will have to pass and you need to use an object
# from the SimpleStats class, which I will check manually.


# Define the SimpleStats class here, and change the code below to use it.


number_list = []

new_number = input('Enter a number for the list: ')

while new_number != '':
    number_list.append(eval(new_number))
    new_number = input('Enter a number for the list: ')

print('The smallest number is', min(number_list))
print('The largest number is', max(number_list))
print('The sum of the list is', sum(number_list))
print('The average of the list is', sum(number_list) / len(number_list))
