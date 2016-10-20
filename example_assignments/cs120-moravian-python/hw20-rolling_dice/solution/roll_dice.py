import random

class Die:
    def __init__(self, num_sides):
        self.num_sides = num_sides
        self.roll()

    def roll(self):
        self.value = random.randint(1, self.num_sides)

    def get_value(self):
        return self.value


num_dice = eval(input('Enter a number of dice: '))
num_sides = eval(input('Enter the number of sides: '))

dice = []

for i in range(num_dice):
    dice.append(Die(num_sides))

total = 0

print('You rolled ', end='')

for die in dice:
    die.roll()
    total += die.get_value()
    print(die.get_value(), end=' ')

print('The total is', total)
