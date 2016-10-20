# CSCI 121 - Computer Science II
## Homework 10 - Gradebook

For this assignment you will add a method to an existing class which operates on an `ArrayList` that is stored as an instance variable.

### Structure

You are given two classes: `AssignmentGrade` and `Gradebook`. Together these classes implement a very simple gradebook to which you can add assignment grades and get the current average.

There are also tests in `GradebookTest` which test the existing methods, but will not test the method that you add.

### `AssignmentGrade`

`AssignmentGrade` is a simple class which stores a name as a string and a grade as a double. These are passed in through the constructor and cannot be changed once they are set. There are two methods, `getName()` and `getGrade()` which return the name and grade.

### `Gradebook`

The `Gradebook` class stores `AssignmentGrade` references in an `ArrayList<AssignmentGrade>`. The class has the following methods:

- `addAssignmentGrade(AssignmentGrade assgnGrade)` adds an `AssignmentGrade` to the gradebook.
- `getCount()` returns the number of assignments in the gradebook.
- `getAverage()` returns the average grade. Returns 0.0 if there are no assignments in the gradebook.

### Adding a Method

Add a method called `removeLowestGrade()`. This method removes the `AssignmentGrade` with the lowest grade from the gradebook, and returns nothing. If the gradebook is empty it does nothing.

In this method you are going to have to find the index of the `AssignmentGrade` which has the lowest grade. This is similar to just finding the min in a list, but you will also have to update a stored index each time you update the min. Create two variables, perhaps called `min` and `minI`. `min` should start at `Double.MAX_VALUE` and `minI` at 0. Loop over `grades` with an index-based `for` loop, checking the grade of each `AssignmentGrade`. If the grade is a new minimum, update `min` and `minI`. When the loop ends, `minI` should be the index that stores the lowest grade. You can then remove the grade using the `remove()` method of `grades`.

### Submission

Push your submission to the grader where it will be tested.