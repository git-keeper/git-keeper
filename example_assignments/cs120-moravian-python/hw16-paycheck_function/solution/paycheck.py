# Calculates the amount of pay for one week
# Parameters:
#   hours - the number of hours worked (positive float)
#   rate  - the normal hourly pay rate (positive float)
# Returns the amount of pay (positive float)
def calculate_pay(hours, rate):
    if hours > 40:
        extra = hours - 40
        pay = 40 * rate + extra * (1.5 * rate)
    else:
        pay = hours * rate

    return pay


hours = eval(input("hours: "))
rate = eval(input("rate: "))

pay = calculate_pay(hours, rate)

print(pay)
