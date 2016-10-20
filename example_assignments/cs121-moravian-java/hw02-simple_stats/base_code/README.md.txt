## CSCI 121 - Computer Science II
### Homework 2 - Simple Stats

The `SimpleStats.java` file that came with this assignment contains the same
code that we wrote for the `Average` class in class. For this assignment you
will add two methods to the class: `getMin()` and `getMax()`. `getMin()` should
return the smallest number seen so far, and `getMax()` should return the
largest.

The UML now looks like this:

![SimpleStats UML diagram](SimpleStats.png)

In order to see the above UML diagram you need to view this file in "HTML
Preview" mode which requires the MultiMarkdown plugin. You should have
installed this plugin during lab. If you do not have the plugin installed, go
to Preferences -> Plugins -> Browse Repositories, search for multimarkdown, and
install the plugin when it comes up.

#### Minimum and Maximum Behavior

There is more than one way we could implement the minimum and maximum
behavior. The main issue is, what are the values of `min` and `max` before we
add any values to the object?

Here we will define the initial `min` and `max` values to be 0.0. This means
that `min` and `max` should be initialized to be 0.0 when they are
defined. When the first value is added, both should be set to that value. For
each subsequent value that is added, check to see if the new value is greater
than `max` or less than `min` and update `min` or `max` if need be. This means
that when a value is added you need to check to see if it is the first value or
not, since that is a special case. Use the `count` instance variable to
accomplish this.

#### Test Drive Class

When you have added the `getMin()` and `getMax()` methods, create a new class
called `SimpleStatsTestDrive` by right clicking (control + click in OS X) and
selecting New -> Java Class. This class should have a `main()` method that
creates a `SimpleStats` object and calls its methods to test it. Make sure that
`getMin()`, `getMax()`, and `getAverage()` all return 0.0 when no values have
been added to the object, and that they return the correct values after multiple
values have been added.

See the `AverageTestDrive` class in the Class Code folder on drive for
reference.

#### Submission

Push your submission to the grader. My tests will test your `SimpleStats` class
directly, so you must make sure that all the methods are named correctly and
that they all work correctly.

If all of my tests pass you should see output like this in the email:

```
    JUnit version 4.12
    ...
    Time: 0.003
    
    OK (3 tests)
```

If any of my tests fail you may see some messy output! If the tests are failing
make sure you are testing your class properly in `SimpleStatsTestDrive`.

