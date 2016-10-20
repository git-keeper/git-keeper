## CSCI 121 - Computer Science II
### Homework 11 - Stats List

For this assignment you will write a class called `StatsList` which extends
`ArrayList<Double>`. The `src` directory contains an empty file named
`StatsList.java`. Place your class in there.

`StatsList` should add the following methods:
 
* `sum()` - Returns the sum of all the numbers in the list.
* `average()` - Returns the average of all the numbers in the list.
* `min()` - Returns the minimum value in the list.
* `max()` - Returns the maximum value in the list.
 
#### Hints

I showed you `sum()` in class. See the `Class Code/Inheritance` folder on
Google Drive for that example.

`Double.MIN_VALUE` works differently than `Integer.MIN_VALUE`.
`Double.MIN_VALUE` is the smallest *positive* value that a `double` can store.
In other words, the positive value closest to 0 that a `double` can store. To
get the most negative value of a `double`, use `-1.0 * Double.MAX_VALUE`.

#### Submission

Push your submission to the grader.
