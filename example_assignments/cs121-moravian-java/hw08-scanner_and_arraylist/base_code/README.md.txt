# CSCI 121 - Computer Science II
## Homework 8 - Scanner and ArrayList

This assignment is intended to introduce you to the `Scanner` and `ArrayList` classes by example. To complete this assignment you will need to make a small modification to existing code.

### Code Structure

You are given 2 classes: `Dog` and `Main`.

The `main()` method in the `Main` class has an input loop that continually asks the user to enter dog names until the user enters an empty string. You may recognize this pattern of input gathering from CS I last semester.

Each time the user enters a name, a new `Dog` object is created and appended to an ArrayList. Once the user is done entering names, there is a loop which calls each `Dog` object's `talk()` method.

Here is what an example run looks like:

```
Enter a name for a dog (enter nothing to stop): Charlie
Enter a name for a dog (enter nothing to stop): Dee
Enter a name for a dog (enter nothing to stop): Dennis
Enter a name for a dog (enter nothing to stop): Mac
Enter a name for a dog (enter nothing to stop): 
Bark bark, my name is Charlie
Bark bark, my name is Dee
Bark bark, my name is Dennis
Bark bark, my name is Mac
```

### Modification

Your task is to change the code in the `for` loop in `main()` so that only dogs whose names have more than 4 letters will talk. After your change the same sequence of names should produce output like this:

```
Enter a name for a dog (enter nothing to stop): Charlie
Enter a name for a dog (enter nothing to stop): Dee
Enter a name for a dog (enter nothing to stop): Dennis
Enter a name for a dog (enter nothing to stop): Mac
Enter a name for a dog (enter nothing to stop): 
Bark bark, my name is Charlie
Bark bark, my name is Dennis
```

You can find out how many characters are in a string by using its `length()` method.

### Submission

My tests will run your program and simulate user input using different names from the above example and make sure that your program prints the right output.
