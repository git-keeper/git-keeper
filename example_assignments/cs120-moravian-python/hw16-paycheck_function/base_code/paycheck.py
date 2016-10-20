# Below is my solution for homework 8, which asked you to calculate the amount
# of a weekly paycheck, taking into account that any hours over 40 pay time and
# a half.
#
# Restructure the program so that the amount of pay is calculated in a
# function. To get full credit for this homework your code will have to pass
# the tests and the pay calculation must happen within a function. I will
# manually check that you are using a function.
#
# The contract of the function is as follows:
#
# calculate_pay(hours, rate)
# Purpose - Calculates the amount of pay for one week
# Parameters:
#   hours - the number of hours worked (positive float)
#   rate  - the normal hourly pay rate (positive float)
# Return value - the amount of pay (positive float)

hours = eval(input("hours: "))
rate = eval(input("rate: "))

if hours > 40:
    extra_hours = hours - 40
    pay = 40 * rate + extra_hours * (1.5 * rate)
else:
    pay = hours * rate

print(pay)
