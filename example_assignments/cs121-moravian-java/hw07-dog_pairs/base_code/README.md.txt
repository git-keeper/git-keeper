# CSCI 121 - Computer Science II
## Homework 7 - Dog Pairs

The purpose of this assignment is to give you more experience with the following:

* Static methods
* Nested for loops
* Arrays of references

### Structure

You are given three classes: `Main`, `Dog`, and `DogPairPrinter`. 

`Main` contains a `main()` method for you to use to test out the code.

`Dog` is a very simple class that stores a name as a String, and provides the method `getName()`. Do not modify this class.

`DogPairPrinter` is a class with a static method that you are to implement. This method takes an array of `Dog` references as input, and prints out each pair of `Dog` names separated by the string `" and "`.

For example, this method could be used like so:

```
Dog[] dogs = {new Dog("Juanita"), new Dog("Jorge"), new Dog("Martin")};
DogPairPrinter.printDogPairs(dogs);
```

The above code should print out the following:

```
Juanita and Jorge
Juanita and Martin
Jorge and Martin
```

No dog should be paired with itself, and no two dogs should be paired together more than once. 

See the class code for reference.

### Submission

Implement the `printDogPairs()` method so that it behaves as expected. My code will test only your method, it does not matter what code you put into `main()`.
