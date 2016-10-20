## HW 20 - Rolling Dice

For this assignment you will write a Die class similar to the one we used in
class. However, instead of being restricted to only 6 sides, this class's
constructor should have the number of sides of the die as a parameter, and
store the number of sides as an instance variable. So your constructor's header
should look like this:

    def __init__(self, num_sides):

When you make a new Die object, you will pass the number of sides to the
constructor as an argument. For example, to make a 10 sided die you would do
this:

    d = Die(10)

Your class should have these two methods as well:
* `roll()` - A mutator method which rolls the die and changes the current value
of the die.
* `get_value()` - A query method which returns the current value of the die.

Create this class in `roll_dice.py`. Write a program that uses the class and
does the following:
1. Ask the user to input a number of dice.
2. Ask the user to input the number of sides that each die has.
3. Create a list of Die objects from your Die class.
4. Roll each die.
5. Print the value of each die.
6. Print the sum of all the dice.

Here is an example run:

    Enter a number of dice: 3
    Enter the number of sides: 8
    You rolled 3 8 6
    The total is 17
