
In this tutorial you will create, test, and publish a simple assignment for an existing class.

### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer
* An active class in `git-keeper`

Throughout the tutorial, we will use the class name `cs100f22`.  You should use the name of 
your existing class.

## Create a Base Assignment from the Default Template

The easiest way to create an assignment is to use the `gkeep new` command, which will create 
a directory containing empty copies of all the required files for an assignment.  Use the following
command to create an assignment named `hwk_even`:

```
gkeep new hwk_even
```

An assignment in `git-keeper` is a folder where the name of the folder is the name of the assignment.  
The folder contains:

* `base_code` - a folder containing one or more files that will in the `git` repository of every student
* `email.txt` - a file containing any information you want to include with the clone url when the
    assignment is published
* `assignment.cfg` (optional) - a configuration file specifying system-level details of how each 
    student submission will be tested
* `tests` - a folder containing any code and data used to test a student submission
* `tests/action.sh` OR `tests/action.py` - a script that executes your tests

## Prepare the Assignment

In this tutorial, we will create a simple CS1-level assignment in Python where students
must implement a function that determines if a number is even.  The tests will use the built-in
`unittest` framework to execute tests on the assignment.

### Base Code

Create a new file `hwk_even/base_code/even.py`:

```
def is_even(number):
    return False


for number in range(10):
    if is_even(number):
        print('{} is even'.format(number))
    else:
        print('{} is odd'.format(number))
```

### Tests

To test a student submission we will compare the output of the student submission 
and of a correct solution.

First, create a new file `hwk_even/tests/expected.py` containing the correct solution:

```
def is_even(number):
    return number % 2 == 0


for number in range(10):
    if is_even(number):
        print('{} is even'.format(number))
    else:
        print('{} is odd'.format(number))
```

The `git-keeper` system runs `action.sh` to start the test process.  Edit the file 
`hwk_even/tests/action.sh`:

```
# Redirect stderr and stdout to a file
python3 $1/even.py > student_output.txt 2>&1

# If python has a non-zero exit code, something went wrong running the student code
if [ $? -ne 0 ]; then
        echo "There was an error when running your code:"
        echo "-------------------------------------------------"
        cat student_output.txt
        echo "-------------------------------------------------"
        echo "Please try again"
        exit 0
fi

# Redirect output of a correct solution
python3 expected.py > expected_output.txt

# Compare the student output with the correcdt output
# Send output to /dev/null because we don't need it
diff -w student_output.txt expected_output.txt >> /dev/null

# diff returns non-zero when the files are not the same
if [ $? -ne 0 ]; then
        echo "Your output is not correct.  Expected:"
        cat expected_output.txt
        echo "Your output:"
        cat student_output.txt
        exit 0
fi

echo "Your output is correct.  Nice work!"
cat student_output.txt

# Any non-zero exit code indicates a problem with the test process
# Make sure to have the following line at the end of all action.sh files
exit 0
```


### Email Announcement

The contents of `hwk_even/email.txt` will be used in the assignment announcement email
sent to all students.  Edit this file to contain:

```
hwk_even: Implement a function to determine if a number is even.

HINT: Use the modulus operator!
```

### Assignment Configuration

An empty file `assignment.cfg` was created by `gkeep new`, but we do not need to edit it
for this assignment.  All possible values in this file are optional, and by leaving it
empty the server will use default values.

## Upload the Assignment

Now that we have all the files prepared for the assignment, we can upload it to the server.
In the **parent** directory of `hwk_even`, run:

```
gkeep upload cs100f22 hwk_even
```

The output should be

```
uploading hwk_even in cs100f22
Assignment uploaded successfully
```

In addition, you should have an email from `git-keeper` containing:

```
Clone URL:
prof1@gkserver:/home/prof1/prof1/cs100f22/hwk_even.git


hwk_even: Implement a function to determine if a number is even.

HINT: Use the modulus operator!
```

NOTE: You will see your username in place of `prof1` in the clone URL.


## Test the Assignment

At this point the assignment is on the server, but it is **NOT** distributed to the students.
Before we publish the assignment, let's test it to make sure the test process works as
expected.

We will use the `gkeep test` command to simulate the process of a student pushing their code to
their repo.

First we will submit a copy of the correct solution.  Create a folder named `solution` in 
`hwk_even` and then edit the file `hwk_even/solution/even.py`:

```
def is_even(number):
    return number % 2 == 0


for number in range(10):
    if is_even(number):
        print('{} is even'.format(number))
    else:
        print('{} is odd'.format(number))
```

Now run the tests on this solution:

```
gkeep test cs100f22 hwk_even hwk_even/solution
```

The output should be:

```
Testing solution hwk_even/solution for assignment hwk_even in class cs100f22
Pushing your solution using git
Solution pushed successfully, you should receive a report via email
```

You should receive an email containing:

```
Your output is correct.  Nice work!
0 is even
1 is odd
2 is even
3 is odd
4 is even
5 is odd
6 is even
7 is odd
8 is even
9 is odd
```

Next we will submit an incorrect solution:

```
gkeep test cs100f22 hwk_even hwk_even/base_code
```

The output should be:

```
Testing solution hwk_even/base_code for assignment hwk_even in class cs100f22
Pushing your solution using git
Solution pushed successfully, you should receive a report via email
```

The email from `git-keeper` should be:

```
Your output is not correct.  Expected:
0 is even
1 is odd
2 is even
3 is odd
4 is even
5 is odd
6 is even
7 is odd
8 is even
9 is odd
Your output:
0 is odd
1 is odd
2 is odd
3 is odd
4 is odd
5 is odd
6 is odd
7 is odd
8 is odd
9 is odd
```

Finally, let's submit code that throws an exception.  Create a folder `hwk_even/bad_code`
and then edit the file `hwk_even/bad_code/even.py`:

```
def is_even(number):
    return 0/0


for number in range(10):
    if is_even(number):
        print('{} is even'.format(number))
    else:
        print('{} is odd'.format(number))
```

The output should be:

```
Testing solution hwk_even/bad_code for assignment hwk_even in class cs100f22
Pushing your solution using git
Solution pushed successfully, you should receive a report via email
```

The email from `git-keeper` should be:

```
There was an error when running your code:
-------------------------------------------------
Traceback (most recent call last):
  File "/home/tester/hwk_even/even.py", line 7, in <module>
    if is_even(number):
  File "/home/tester/hwk_even/even.py", line 2, in is_even
    return 0/0
ZeroDivisionError: division by zero
-------------------------------------------------
Please try again
```

## Publish the Assignment

At this point we have demonstrated that our submission testing handles correct solutions
as well as solutions that produce incorrect output or produce an error.  We are ready to 
publish the assignment:

```
gkeep publish cs100f22 hwk_even
```

The output should be:

```
Publishing assignment hwk_even in class cs100f22
Assignment successfully published
```

Each student will receive an announcement email:

```
Clone URL:
alovelace@gkserver:/home/alovelace/prof1/cs100f22/hwk_even.git


hwk_even: Implement a function to determine if a number is even.

HINT: Use the modulus operator!
```
