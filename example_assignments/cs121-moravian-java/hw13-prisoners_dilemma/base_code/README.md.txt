## CSCI 121: Computer Science II
### HW 13 - Prisoner's Dilemma

#### Overview

In game theory, prisoner's dilemma is a two-player game in which the best situation globally occurs when both players cooperate, but each player could improve their situation by not cooperating.

It is often presented like this:

Two prisoners, A and B, are interrogated separately with no way to communicate with each other. They are both offered a chance to testify against the other, resulting in a sentence reduction. Each prisoner will either stay silent (cooperate) or agree to testify (defect). We will use the following sentence times in our simulation:

* If A and B both cooperate, both will serve half a year in prison.
* If A and B both defect, both will serve 5 years in prison.
* If A cooperates and B defects, A serves 10 years in prison and B goes free.
* If B cooperates and A defects, B serves 10 years in prison and A goes free.

If the goal is to reduce the sum of the two players' sentence times, then they should both cooperate. However, an individual player's best outcome occurs if they defect and the other cooperates.

#### Iterated Prisoner's Dilemma

The game can also be played repeatedly between the same two players. In this version of the game, the goal of each player is to have the lowest total sentence time after a number of rounds. Each player knows the result of the previous round.

In this iterated version, players can use knowledge of the opponent's past plays to shape the strategy going forward.

#### Our simulation

Each of you will write a Java class which implements a strategy for iterated prisoner's dilemma. An interface called `Strategy` has been provided for you. Your strategy must implement this interface so that it can be used in the code that runs the simulation. You *must not* modify the `Strategy` interface itself. If you do, your code will not work with mine.

The methods of `Strategy` are as follows:

- `char play()` - Returns the play for the current round. Must return either 'c' for cooperate or 'd' for defect.
- `void report(char opponentChoice)` - This method is called after a round to inform the player of the opponent's choice in the previous round.
- `void reset()` - This is called at the beginning of each game (not each round). Use this method to reset any bookkeeping variables you have.
- `public String getName()` - Returns the name of the strategy. Must be a
unique name so that your strategy can be identified.

Make sure that you test your class. At the very least you should make sure that you can create an instance of your class and call all of its methods.

Once the submissions are in, I will run a program that uses all of the submitted classes and pairs each strategy against each other strategy. After all the games, the strategy with the lowest average per-round sentence time wins.

Four competitions will be run. One for each class section, one for both class sections combined, and one that combines everyone from this year with everyone from two years ago.

#### `AlwaysDefect`

An example strategy, `AlwaysDefect`, has been provided for you. Your strategy should do something different. I will place the following strategies in the game, so you must implement something other than these 3:

- always defect
- always cooperate
- tit for tat (do the same thing your opponent did last round)

#### Submission

To get full credit for this assignment, you must submit at least 1 class that implements `Strategy` correctly. You may submit more classes if you wish.

The winner of each of the 4 competitions will receive 1 homework bonus point. These will stack if you win more than one, so it is possible for 1 student to earn 3 bonus points.

When you push you will get an email that your submission was received, but no tests will be run at that time.

To be in the competition, your class(es) must be submitted by 7:30 AM Monday morning so that I can assemble them all before the morning's class.

