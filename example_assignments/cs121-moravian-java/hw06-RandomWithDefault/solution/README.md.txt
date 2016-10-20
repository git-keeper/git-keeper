# CSCI 121 - Computer Science II
## Homework 6

For this assignment you will figure out what is wrong with a class by writing tests for it, and then fix the problem.

### `RandomWithDefault`

You are given the class `RandomWithDefault`. The purpose of this class is to store a fixed sequence of random numbers, and these numbers can be accessed by index. The class also stores a default value which will be returned if someone tries to access a number with an out of bounds index. The class has a constructor and one method, as defined below:

* `RandomWithDefault(double min, double max, double theDefault, int count)` - constructs a `RandomWithDefault` object that contains `count` number of random numbers between `min` (inclusive) and `max` (exclusive). `theDefault` is a value that will be returned if someone tries to access a number with an index that is outside of the range of the sequence of random numbers generated.
* `getValue(int index)` - returns the random value at the corresponding `index`, or returns the default value if the `index` is out of bounds of the generated random numbers.

For example, here is a line of code which creates a new `RandomWithDefault` object:

```
RandomWithDefault rwd = new RandomWithDefault(10.0, 20.0, 20.0, 10);
```

This `RandomWithDefault` object stores 10 random numbers with a min of 10, a max of 20, and a default value of 20. For this instance, the indexes that should give you the random numbers when calling `getValue()` are indexes 0 through 9. Using an index outside of 0 through 9 should return `20.0`.

### Fixing the Problem

As it is implemented, the class does not quite work as it is described above. Write tests that ensure that the class has the behavior as described above. Fix the class so that your tests pass. Your tests must be in the file `tests/RandomWithDefaultTest.java` or the grader will not accept your submission. As we did in lab, you will need to create the `tests` directory and mark it as the test sources root before creating any tests. See the lab instructions if you forget how to create tests.

### Submission

When you push, my tests will be run against your code. Your grade will be based on two things:
 
* Your code passes my tests
* Your tests ensure that the code has the correct behavior
