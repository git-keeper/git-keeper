# CSCI 121 - Computer Science II
## Homework 5 - Histogram

Included with this assignment is the Histogram class we wrote in class. Your task is to add a method called `prettyPrint()` to the class which prints out a text visualization of the Histogram.

Each line of `prettyPrint()`'s output should print asterisks to indicate the relative frequency of a tallied number. That is, the higher a number's count, the more asterisks it should have. The number with the highest count should have 10 asterisks, and the number of asterisks for the other numbers should be scaled relative to the max.

Here are some example scenarios with corresponding output:

As we did in class, a Histogram with 1 one and 2 twos:
```
Histogram hist = new Histogram(3);

hist.tally(1);
hist.tally(2);
hist.tally(2);

hist.prettyPrint();
```

That code should produce this output:
```
0: 
1: *****
2: **********
3: 
```

3 zeros, 2 threes, and 1 two:
```
Histogram hist = new Histogram(3);

hist.tally(0);
hist.tally(0);
hist.tally(0);
hist.tally(2);
hist.tally(3);
hist.tally(3);

hist.prettyPrint();
```

should print:
```
0: **********
1: 
2: ***
3: ******
```

When calculating the number of asterisks you should always round down. This is easy to do by casting to an int.

Here are some blocks of pseudocode to help you out:

To find the maximum value you will need to loop:
```
Set a variable storing the maximum value to 0
For each number from zero to the largest value stored in the Histogram:
    If the count for this number is larger than the max so far, update the max
```

To print out each line you need to use nested loops. The outer loop gives you each line, the inner loop gives you each asterisk:
```
For each number from zero to the largest value stored in the Histogram:
    Print the number followed by a colon and a space, with no newline
    Figure out the number of asterisks you need to print
    Loop once for each asterisk:
        Print an asterisk, with no newline
    Print a newline
```

Try out your `prettyPrint()` method in the `HistogramTestDrive` class.

The grader will not run your `main()` method but will instead run some tests against your `Histogram` class to make sure it works properly. 

Recall that you can use a `for` loop like we talked about in class. The general `for` loop syntax is:
```
for (<declaration and initialization>; <condition>; <increment>) {
   ...
}
```

So say you wanted a loop that gives you the numbers 0 through 5:
```
for (int i = 0; i <= 5; i++) {
    <do something with i>
}
```

Or you want to do something 10 times:
```
for (int i = 0; i < 10; i++) {
    <do the something>
}
```