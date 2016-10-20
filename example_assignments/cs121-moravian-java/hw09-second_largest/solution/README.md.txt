# CSCI 121 - Computer Science II
## Homework 9 - ArrayLists

For this homework you will write a method which finds the second largest value of an ArrayList.

### Structure

Your method will go in the class `ArrayListMethods`. There is already a method called `maxElement()` in the class to give you an example to work from. `ArrayListMethodsTest` has some tests to show example use.

Note there is something new in this method: `Integer.MIN_VALUE` gives you the lowest possible value for an `int` in Java. This lets the method work with negative as well as positive integers.

### New Method

You are to implement this method:

`public static int secondLargest(ArrayList<Integer> ints)`

The method must return the second largest value in `ints`. If `ints` has 0 or 1 values in it, it must return `Integer.MIN_VALUE`. Treat repeat values as a single value. In other words, the lists `10, 3, 5` and `10, 3, 10, 5` both have a second largest value of `5`.

### Testing

You may add tests to `ArrayListMethodsTest` or create a class with a `main()` method to test your method. Make sure you test everything as specified above so you are sure it works in all situations!

### Submission

When you push it will run my tests against your `ArrayListMethods` class.
