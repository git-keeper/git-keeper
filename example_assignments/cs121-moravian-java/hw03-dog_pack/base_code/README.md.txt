# CSCI 121 - Computer Science II
## HW 3 - Dog Pack

This assignment will give you some experience using arrays of references.

### Classes

#### Dog

The `Dog` class we created in class today is provided for you. You do not need to change this class at all.

#### DogPack

The `DogPack` class is only partially implemented. The `dogs` instance variable is a reference to an array of `Dog` references used to store the pack of dogs. The constructor has a reference to an array of `String` as its parameter, named `dogNames`. You are to implement the constructor so that it creates a new array for `dogs` to refer to which is the same length as `dogNames`. You should also write a loop that creates a new `Dog` object for each string in `dogNames` and stores the references to the new `Dog` objects in the `dogs` array.

You are also to implement the `makeRuckus()` method. This method should contain a loop which calls the `talk()` method for each `Dog` in `dogs`.

#### DogPackTestDrive

The `DogPackTestDrive` class has been provided for you. As it is, the `main()` method of this class creates an array of dog names, creates a `DogPack` object from those names, and calls the `makeRuckus()` method of the pack.

After you have implemented the `DogPack` class, run the `DogPackTestDrive` class to make sure it works. You should see 3 lines of output, one for each dog. Try adding more names to the `dogNames` array and make sure that `DogPack` works with more than 3 dogs too.

### Submission

My tests for this assignment will use your `DogPack` class directly. It does not matter what you have in `DogPackTestDrive` as far as my tests are concerned. The output you receive via email will be similar to the last assignment.

My tests ensure that `makeRuckus()` prints one line for each dog, and that each line contains the proper dog name.

