# Faculty Users

This page has numerous guides for faculty users. See the nagivation bar to
explore the sections on this page.

## Client Setup

This guide details how to set up a faculty machine to use the git-keeper
client. The client has been used successfully in OS X and Linux. It may work in
Windows using the Windows Subsystem for Linux or Cygwin but that has not been
fully tested.

### Requirements

The client requires [Git](https://git-scm.com/downloads) and
[Python 3.8 or greater](https://www.python.org/downloads/).

In addition, you need the username and password sent to you by the 
`git-keeper` server.  This account must be created by the `git-keeper`
server.  For the faculty admin, your account is created the first time
you run `gkeepd`.  For other faculty, the faculty admin must use
`gkeep add_faculty` to create the account.

### Installing the Client

To install the client system-wide, run the following command:

```no-highlight
sudo python3 -m pip install git-keeper-client
```

Alternatively, you may want to install the client in a
[Python virtual environment](https://docs.python.org/3/tutorial/venv.html) if
you do not want to clutter your system's Python packages.

### Configuration

There must be a configuration file at `~/.config/git-keeper/client.cfg`. The
easiest way to create this file is to run `gkeep config`, which will prompt you
for various values and then create the file.

If you create `client.cfg` manually, you must include a section called
`[server]` which defines the hostname of the server, your faculty username on
the server, and optionally the SSH server's port number which defaults to 22.

You may also include an optional section `[local]` in which you can define a
directory into which `gkeep` will fetch submissions and the directory where
assignment templates are stored.  If present, these *must* be an absolute path.

Here is an example `client.cfg`:

```
[server]
host = gitkeeper.myhostname.com
username = myfacultyusername
# optional
ssh_port = 22

# optional section
[local]
submissions_path = ~/submissions
template_path = ~/gkeep_templates
```

### SSH Key

The client communicates with the server over SSH, and it requires SSH keys so
that you can make SSH connections without a password.

If you have never generated a public key, do so now:

```no-highlight
ssh-keygen
```

Use the default filename, and do **NOT** set a password for the key.

Next, copy your public key to your git-keeper server:

```no-highlight
ssh-copy-id <username>@<hostname>
```

### Check Your Configuration

To verify that everything is configured correctly, run

```no-highlight
gkeep check
```

The output should something look like:

```no-highlight
/home/turing/.config/git-keeper/client.cfg parsed without errors

Successfully communicated with gkserver

Server information:
  Version: 0.3.1
  gkeepd uptime: 29m21s
  Firejail installed: True
  Docker installed: True
```

### Getting Help

Run `gkeep` with no arguments to see a usage message.  Run `gkeep` with a
subcommand and no additional arguments to see a usage message for that
subcommand.

## Creating Classes

To create a class you first need to create a CSV file with the names and email
addresses of the students in the class.  Class names are unique for each
faculty member and cannot be changed.  We recommend you use a naming scheme
that includes information that identifies the course and the term.  For
example, `cs100f22`.

To create a class named `cs100f22`, create a file named `cs100f22.csv`
containing something like the following:

```no-highlight
Hamilton,Margaret,mhamilton@example.edu
Hopper,Grace,ghopper@example.edu
Lovelace,Ada,alovelace@example.edu
```

Now you can add the class on the server using `gkeep`:

```no-highlight
gkeep add cs100f22 cs100f22.csv
```

An account will be created for any student in the class that does not already
have an account on the server. The account name will be the username portion of
the student's email address, though modifications will be performed if the
email username is not a valid Linux username. In the case of a duplicate
username, a number will be appended to the username to create a unique account.
Passwords are randomly generated.  An email containing the student's username
and password will be sent to the student.

!!! note
    Faculty should save the CSV file in case they need to make changes to
    the enrollment of the class on the `git-keeper` server.

## Modifying Classes

Faculty can use the `gkeep modify` command to:

* Add new students to a class
* Remove students from a class
* Change a student's name (e.g. fix a typo)
* Change a student's email address

The system uses the email address to identify the student, so it will 
consider a change of email address as removing the old account and
adding a new account.

Faculty can make multiple changes to the CSV file and then run `gkeep modify`
to make all the changes at once.  The system will show you the changes and
prompt you for confirmation.

### Examples

In the following examples, assume you have a class named `cs100f22` based on the 
file `cs100f22.csv`:

```no-highlight
Hamilton,Margaret,mhamilton@example.edu
Hopper,Grace,ghopper@example.edu
Lovelace,Ada,alovelace@example.edu
```

#### Example: Add a New Student to a Class

Edit the class CSV file to add the student information:

```no-highlight
Hamilton,Margaret,mhamilton@example.edu
Hopper,Grace,ghopper@example.edu
Lovelace,Ada,alovelace@example.edu
Turing,Alan,turninga@example.edu
```

Modify the class enrollment and confirm the changes

```no-highlight
gkeep modify cs100f22 cs100f22.csv
```

The output will be:

```no-highlight
Modifying class cs100f22

The following students will be added to the class:
Turing, Alan, turninga@example.edu

Proceed? (Y/n) y
Students added successfully
```

#### Example: Remove a Student from a Class

Edit the class CSV file to remove the student information (removing Grace
Hopper in this example):

```no-highlight
Hamilton,Margaret,mhamilton@example.edu
Lovelace,Ada,alovelace@example.edu
```

Modify the class enrollment and confirm the changes

```no-highlight
gkeep modify cs100f22 cs100f22.csv
```

The output will be:

```no-highlight
Modifying class cs100f22

The following students will be removed from the class:
Hopper, Grace, ghopper@example.edu

Proceed? (Y/n) y
Students removed successfully
```

#### Example: Change the Name of a Student

Edit the class CSV file to update the student name (change "Margaret" to
"Maggie" in this example):

```no-highlight
Modifying class cs100f22

The following student names will be updated:
Hamilton, Margaret -> Hamilton, Maggie

Proceed? (Y/n) y
Students modified successfully
```

#### Example: Change the Email Address of a Student

Edit the class CSV file to update the student email address (change Ada's email
to "alovelace@babbage.edu" in this example):

Modify the class enrollment and confirm the changes:

```no-highlight
gkeep modify cs100f22 cs100f22.csv
```

The output will be:

```no-highlight
Modifying class cs100f22

The following students will be added to the class:
Lovelace, Ada, alovelace@babbage.edu

The following students will be removed from the class:
Lovelace, Ada, alovelace@example.edu

Proceed? (Y/n) y
Students added successfully
Students removed successfully
```

A new account was created because `git-keeper` uses the email address to
identify the student.

!!! note
    In this example, the new account on the `git-keeper` server will be
    `alovelace1` because the username `alovelace` is associated with the
    `alovelace@example.edu` email address.

## Class Status

Each class in `git-keeper` has a status, "open" or "closed."  When created a
class is open, and it remains open until the faculty explicitly closes it.
To change the status of a class run the command

```no-highlight
gkeep status <class_name> <status>
```

where `<status>` is `open` or `closed`.  The system will respond with

```no-highlight
Status updated successfully
```

When a class is open, the faculty member can publish assignments and the
students can receive results.

When a class is closed, the faculty cannot upload or publish any new
assignments.  If they run `gkeep upload` or `gkeep publish` on a closed course,
they will receive a message, "Class <classname> is closed."

If a student pushes to a repo associated with a closed course they will receive
an email indicating that the course is closed:

```no-highlight
Subject: [cs1] class is closed

You have pushed a submission for a class that is is closed.
```

## Password Reset

If a student forgets their password, the faculty member can reset their
password using

```no-highlight
gkeep reset <username> 
```

### Sample Password Reset Email

```no-highlight
Hello Sharon,

Your git-keeper password has been reset to QzmPflFP

If you have any questions, please contact your instructor rather than responding to this email directly.
```

## Assignments

What follows is a guide to creating, uploading, and publishing assignments and
then fetching the students' submissions.

### Assignment Structure

To create an assignment, first create a directory to contain the
assignment. The name of the directory will be the name of the assignment.

#### `assignment.cfg` (optional)

The optional `assignment.cfg` file may be used to configure the
testing environment, time and memory limits, and
whether or not the results emails will use HTML. See
[Testing Environments](#testing-environments) and
[Assignment Configuration](reference.md#assignment-configuration) for more details.

#### `base_code`

Within the assignment directory there must be a directory named
`base_code`. The contents of this directory will be the initial contents of the
student's repository for the assignment. Put skeleton code, data files,
instructions, etc. in this directory.

!!! note
    Git cannot track empty directories, so any empty directories within
    `base_code` will not appear when a student clones the assignment
    repository.

#### `email.txt`

There must also be a file named `email.txt`. The email that students receive
when a new assignment is published will always contain a clone URL, and the
contents of `email.txt` will be appended to the email after the
URL. `email.txt` may be empty.

#### `tests`

A directory named `tests` is also required, which must contain either a shell
script named `action.sh` or a Python script named `action.py`. The `tests`
directory also contains any other code and data files that you will use to test
student code.

When a student submits an assignment to the server it creates a temporary clone
of the student's repository and a temporary copy of the `tests` directory. With
the temporary `tests` directory as its working directory, the testing
environment then runs `action.sh` using `bash` or `action.py` using `python3`,
passing the action script the path to the temporary clone of the student's
directory.


### Creating Action Scripts

For some assignments you can write all your tests in bash or Python and so the
only file you need in the `tests` directory is `action.sh` or `action.py`.

For other assignments you may wish to write your tests in another language or
to use a testing framework such as JUnit to test the student code. In that case
you can simply call your tests from `action.sh`.


### Running Tests Locally

Before you upload the assignment, you can test your tests locally either using
the `gkeep local_test` command or by running your action script directly and
passing it the path a solution.

#### Using `gkeep local_test`

The `gkeep local_test` command takes an assignment directory and a solution
directory as arguments. It then makes copies of the assignment's `tests`
directory and the provided solution directory into a timestamped subdirectory
of `local_testing` within the assignment directory, creating `local_testing`
if necessary. The tests are then run. If you need to investigate any of the
output files that were created during testing, you can check within
`local_testing`.

It is useful to create a `solution` directory within the assignment directory
to use for testing. This command runs tests locally for an assignment
`hw01-hello_world` if we are in the assignment's parent directory and the
assignment directory contains a `solution` subdirectory:

```no-highlight
gkeep local_test hw01-hello_world hw01-hello_world/solution
```

Example output is below. Note that only the output between `BEGIN RESULTS` and
`END RESULTS` will be emailed to the student.

```no-highlight
Tests path:
/home/turing/cs100/hw01-hello_world/tests
Solution path:
/home/turing/cs100/hw01-hello_world/solution
Copies of these directories will be created in this testing directory:
/home/turing/cs100/hw01-hello_world/local_testing/2024-04-06T13-43-27.157582

Tests will be run directly locally and configured timeout and memory
limits will not be enforced. Be sure to try the tests on the server
before publishing.

Running tests...
Success!

----------------------- BEGIN RESULTS ------------------------
All tests passed, good job!

------------------------ END RESULTS -------------------------

If you need to inspect any output files, see /home/turing/cs100/hw01-hello_world/local_testing/2024-04-06T13-43-27.157582

If you would like to clean up testing directories in the future, use
--cleanup
```

#### Running Tests Manually

Alternatively you can run your tests manually by entering the `tests` directory
in the terminal and running `action.sh` or `action.py`, giving it the path to a
solution as a command line argument:

```no-highlight
bash action.sh ../solution
```

or

```no-highlight
python3 action.py ../solution
```

The output of the action script (both stdout and stderr) are placed in the
email that the student receives as feedback.


### Testing Environments

The testing environment for an assignment can be specified in the optional file
`assignment.cfg` within the assignment directory. If this file does not exist
for a given assignment, the assignment will use the default testing
environment. This will be `firejail`, unless specified otherwise in the
[Server Configuration](reference.md#server-configuration).

#### Host Environment

The `host` testing environment is straightforward, but less secure than the
other environment types, and requires that any dependencies for the tests be
installed on the server itself.

The git-keeper server creates a user named `tester`, and tests are run within a
temporary directory in `/home/tester`. The `tester` user cannot access any
other user home directories, but student code could potentially access other
files within the `tester` home directory, including files for other currently
running tests (if multiple threads are used for testing).

This environment may be specified by placing the following in `assignment.cfg`:

```
[tests]
env = host
```

#### Firejail Environment

This testing environment uses [Firejail](https://firejail.wordpress.com/) for
sandboxing. As with `host` environments, tests are run by the `tester` user
within a temporary directory in `/home/tester`, but `firejail` is used to limit
the process so that it can only access files within the temporary testing
directory. Dependencies for the tests must still be installed directly on the
server.

The `firejail` package may need to be explicitly installed on the server
before this environment can be used. It is available in the official
repositories for many Linux distributions, including Ubuntu.

By default, `firejail` is run with the following options:

```no-highlight
--noprofile --quiet --private=/home/tester/<temporary testing directory>
```

This makes `firejail` ignore any default profiles that may be installed on the
server, supresses `firejail` output so that it is not included in the results
email, and sandboxes the tests within the testing directory.

To use the default Firejail options, place the following in `assignment.cfg`:

```
[tests]
env = firejail
```

Additional options may be specified using the `append_args` field. For example,
if you wish to prohibit any network activity and prevent the process from
writing any files larger than 100 KB, you could use the following:

```
[tests]
env = firejail
append_args = --net=none --rlimit-fsize=102400
```

These options will be used in addition to the default options. For a full list
of options available for `firejail`, see the
[Firejail homepage](https://firejail.wordpress.com/) or read through the man
page.

#### Docker Environment

Tests may be run in a Docker container, which can provide both sandboxing and
encapsulation of dependencies.

TODO: setting up docker on the server

To use this environment, a Docker container image must be specified in
`assignment.cfg`. For example, to use our Python 3.10 container the following
may be used:

```
[tests]
env = docker
image = gitkeeper/git-keeper-tester:python3.10
```

The first time tests are run using a particular image, the server must download
the image. This can take some time, so it is important to submit a test
submission before publishing the assignment so that the image is downloaded to
the server before students start submitting.

TODO: Describe and link to our Docker Hub images

When tests are run, the temporary testing directory is mounted as a volume
within the container at `/git-keeper-testing`, and the `tests` directory is at
`/git-keeper-testing/tests`. To create your own container images, you will need
to use the `tests` directory as the working directory, and set the command to
run either `action.sh` or `action.py` depending on your preference.

For example, here is a `Dockerfile` to build an image with Python 3.10 that can
be used with git-keeper:

```dockerfile
FROM python:3.10-slim

WORKDIR /git-keeper-tester/tests

CMD ["bash", "action.sh"]
```

If you want to install additional Python packages within the container, use
`RUN` commands. For example, this installs the `pytest` and `pytest-timeout`
packages using `pip`:

```dockerfile
FROM python:3.10-slim

RUN pip install pytest pytest-timeout

WORKDIR /git-keeper-tester/tests

CMD ["bash", "action.sh"]
```

TODO: Describe how to test the image locally

You can upload your images to Docker Hub, where they can then be accessed by
the server. See the
[Docker Hub documentation](https://docs.docker.com/docker-hub/) for more
information.

### Example

Here is an example where the tests are written entirely in `action.sh`.

Let's say you want to create an assignment for which students will write a
Python program to print `Hello, world!`. You want them to write this program
in an initially empty file named `hello_world.py` and for them to receive
instructions by email.

You might create an assignment structure like this:

```no-highlight
hw01-hello_world
├── assignment.cfg
├── base_code
│   └── hello_world.py
├── email.txt
├── solution
│   └── hello_world.py
└── tests
    ├── action.sh
    └── expected_output.txt
```

`base_code/hello_world.py` can be an empty file which the students will receive
as their starting point, and into which they will place their code. `email.txt`
contains instructions for the assignment, `solution/hello_world.py` contains
your solution, and `tests/expected_output.txt` contains `Hello, world!`.

In `assignment.cfg` let's use `firejail` as the testing environment and set a 5
second timeout in case the student writes an infinite loop in their code:

```
[tests]
env = firejail
timeout = 5
```

What's left is to write `action.sh`. You want to run the student's
`hello_world.py` and compare the output to `expected_output.txt`. Here is a
simple way to go about it:

```bash
# The path to the student's submission directory is in $1
SUBMISSION_DIR=$1

# Run the student's code and put the output (stdout and stderr) in output.txt
python $SUBMISSION_DIR/hello_world.py &> output.txt

# Compare the output with the expected output. Throw away the diff output
# because we only care about diff's exit code
diff output.txt expected_output.txt &> /dev/null

# diff returns a non-zero exit code if the files were different
if [ $? -ne 0 ]
then
    echo "Your program did not produce the expected output. Your output:"
    echo
    cat output.txt
    echo
    echo "Expected output:"
    echo
    cat expected_output.txt
else
    echo "Tests passed, good job!"
fi

# Always exit 0. If action.sh exits with a non-zero exit code the server sees
# this as an error in your tests.
exit 0
```

### Uploading an Assignment

Let's assume you have created an assignment named `hw01-hello_world`, as in the
example above, which is for the class `CS100`. You can upload the assignment to
the server like so:

```no-highlight
gkeep upload CS100 hw01-hello_world
```

Uploading an assignment does not immediately send it to your students. If the
assignment uploads successfully you will receive an email that looks just like
the email that the students get when they receive the assignment. You can make
sure the assignment works as expected by using `gkeep test` or by cloning it
and pushing some solutions.

If you discover errors in your assignment you can update it before sending it
to the students. You can modify any one of the four components of the
assignment individually, or update everything. To update the entire assignment:

```no-highlight
gkeep update CS100 hw01-hello_world all
```

Run `gkeep update` without additional arguments for more info.

### Publishing an Assignment

Once you are satisfied with your uploaded assignment you can publish it, which
will send it out to students:

```no-highlight
gkeep publish CS100 hw01-hello_world
```

Once an assignment is published you cannot update the base code or the email,
but you can update the tests.

### Fetching Submissions

When you want to grade your students' submissions, you can fetch them with
`gkeep fetch`. If you defined `submissions_path` in the `[local]` section of
`client.cfg` then `gkeep` can fetch all your assignments into a common
directory. Otherwrise you need to specify a directory to fetch to.

This will fetch into `submissions_path`:

```no-highlight
gkeep fetch CS100 hw01-hello_world
```

Fetch into the current directory:

```no-highlight
gkeep fetch CS100 hw01-hello_world
```

The fetched directory for the assigment contains 2 subdirectories: `reports`
and `submissions`. `reports` contains the text of the emails that your students
received when they submitted. The `submissions` directory contains the code
that your students submitted.

### Assignment Templates

You can use the command `gkeep new` to create the files and directories required for
an assignment.  For example,

```no-highlight
gkeep new homework1
```

will create a folder `homework1` in the current directory with the following structure:

```no-highlight
homework1
├── assignment.cfg
├── base_code
├── email.txt
└── tests
    └── action.sh
```

where `homework1`, `base_code`, and `tests` are folders and `assignment.cfg`, 
`email.txt`, and `action.sh` are empty files.

You can create your own assignment templates in 
`~/.config/git-keeper/templates` and then provide a template name to
`gkeep new` to create an assignment from one of your templates. The new
assignment directory will simply be a copy of the template directory.

For example, 

```no-highlight
gkeep new function_examples inclass 
```

Would create an assignment folder named `function_examples` using the template `inclass`.

This feature is useful when you have a standard `assignment.cfg`, `email.txt`, `action.sh`, or
other files.


You can change the location of the templates in `client.cfg`.  In the `[local]` section, add
`templates_path`, which must be an absolute path.  For example,

```
# ... other lines omitted
[local]
templates_path = ~/templates
```

## Tutorials

The tutorials below will walk you through various scenarios.


### Create your First Assignment

In this tutorial you will create, test, and publish a simple assignment for an existing class.

#### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer
* An active class in `git-keeper`

Throughout the tutorial, we will use the class name `cs100f22`.  You should use the name of 
your existing class.

#### Create a Base Assignment from the Default Template

The easiest way to create an assignment is to use the `gkeep new` command, which will create 
a directory containing empty copies of all the required files for an assignment.  Use the following
command to create an assignment named `hwk_even`:

```no-highlight
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

#### Prepare the Assignment

In this tutorial, we will create a simple CS1-level assignment in Python where students
must implement a function that determines if a number is even.  The tests will use the built-in
`unittest` framework to execute tests on the assignment.

##### Base Code

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

##### Tests

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


##### Email Announcement

The contents of `hwk_even/email.txt` will be used in the assignment announcement email
sent to all students.  Edit this file to contain:

```no-highlight
hwk_even: Implement a function to determine if a number is even.

HINT: Use the modulus operator!
```

##### Assignment Configuration

An empty file `assignment.cfg` was created by `gkeep new`, but we do not need to edit it
for this assignment.  All possible values in this file are optional, and by leaving it
empty the server will use default values.

#### Upload the Assignment

Now that we have all the files prepared for the assignment, we can upload it to the server.
In the **parent** directory of `hwk_even`, run:

```no-highlight
gkeep upload cs100f22 hwk_even
```

The output should be

```no-highlight
uploading hwk_even in cs100f22
Assignment uploaded successfully
```

In addition, you should have an email from `git-keeper` containing:

```no-highlight
Clone URL:
ssh://prof1@gkserver/home/prof1/prof1/cs100f22/hwk_even.git


hwk_even: Implement a function to determine if a number is even.

HINT: Use the modulus operator!
```

NOTE: You will see your username in place of `prof1` in the clone URL.


#### Test the Assignment

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

```no-highlight
gkeep test cs100f22 hwk_even hwk_even/solution
```

The output should be:

```no-highlight
Testing solution hwk_even/solution for assignment hwk_even in class cs100f22
Pushing your solution using git
Solution pushed successfully, you should receive a report via email
```

You should receive an email containing:

```no-highlight
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

```no-highlight
gkeep test cs100f22 hwk_even hwk_even/base_code
```

The output should be:

```no-highlight
Testing solution hwk_even/base_code for assignment hwk_even in class cs100f22
Pushing your solution using git
Solution pushed successfully, you should receive a report via email
```

The email from `git-keeper` should be:

```no-highlight
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

```no-highlight
Testing solution hwk_even/bad_code for assignment hwk_even in class cs100f22
Pushing your solution using git
Solution pushed successfully, you should receive a report via email
```

The email from `git-keeper` should be:

```no-highlight
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

#### Publish the Assignment

At this point we have demonstrated that our submission testing handles correct solutions
as well as solutions that produce incorrect output or produce an error.  We are ready to 
publish the assignment:

```no-highlight
gkeep publish cs100f22 hwk_even
```

The output should be:

```no-highlight
Publishing assignment hwk_even in class cs100f22
Assignment successfully published
```

Each student will receive an announcement email:

```no-highlight
Clone URL:
ssh://alovelace@gkserver/home/alovelace/prof1/cs100f22/hwk_even.git


hwk_even: Implement a function to determine if a number is even.

HINT: Use the modulus operator!
```

### A Simple Assignment From the Default Template

In this tutorial you will create a simple assignment and upload it to
the `git-keeper` server.

#### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer
* A class named `cs100f22` added to the server

#### Overview

The `gkeep new` is a fast way to create the required files and directory 
structure for an assignment.

Use the `gkeep new` command to create an assignment named `project1`.

```no-highlight
gkeep new project1
```

Edit `project1/base_code/proj1.py`:

```no-highlight
def is_valid(username):
    return False
```

Edit `project1/email.txt`:

```no-highlight
Your first project.  See Canvas for details.
```

Edit `project1/tests/action.sh`:

```no-highlight
echo "Your submission was received"
exit 0
```

Upload the assignment:

```no-highlight
gkeep upload cs100f22 project1
```

The output should be:

```no-highlight
uploading project1 in cs100f22
Assignment uploaded successfully
```

And you should have an email containing:

```no-highlight
Clone URL:
ssh://prof1@gkserver/home/prof1/prof1/cs100f22/project1.git

Your first project.  See Canvas for details.
```

(where `prof1` is your username on the `git-keeper` server).


### Use an Assignment Template

In this tutorial you will create a template and then use it to create a new assignment.

#### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer

#### Overview

The `gkeep new` command is used to create a new assignment.  By default, the command creates
the required directories and files for a valid assignment, and then the faculty member modifies
things to create the assignment.  But `gkeep new` can also create an assignment from a template.
This is useful, for example, when you have a common test mechanism for a course.

A template has the same structure as an assignment, but all files are optional:

```no-highlight
<template_name>
├── assignment.cfg
├── base_code
├── email.txt
└── tests
    └── action.sh
```

By default, `gkeep new` will look in `~/.config/git-keeper/templates` for templates unless
the `~/.config/git-keeper/client.cfg` file contains

```
[local]
template_path = <absolute path>
```

in which case `gkeep new` will look in `<absolute path>`.

#### Create a Template

Faculty often use `git-keeper` to distribute code for in-class examples.  In this case, the 
email announcement is typically minimal, and we do not expect students to submit a solution.
We can create an assignment template containing an `email.txt` with the default message
and an `action.sh` that simply reminds students they do not need to submit.

Start by using `gkeep new` to create a default template within `~/.config/git-keeper/templates`
in a folder named `inclass`:

```no-highlight
gkeep new ~/.config/git-keeper/templates/inclass
```

Edit the file `~/.config/git-keeper/templates/inclass/email.txt` to contain a message
such as the following:

```no-highlight
This repo contains an in-class example.
```

Edit the file `~/.config/git-keeper/templates/inclass/tests/action.sh` such that it reminds
students they do not need to submit:

```bash
echo 'No need to push in-class examples.'
exit 0
```

Edit the file `~/.config/git-keeper/templates/inclass/assignment.cfg` so that the subject
of the announcement email for any example created from this template will indicate it is an
in-class example. Git-keeper will replace `{class_name}` and `{assignment_name}` in the
subject template with the class and assignment names, so this configuration will work for any
class and assignment:

```ini
[email]
announcement_subject = [{class_name}] New in-class example: {assignment_name}
```

#### Use the template

Go to a directory where you want to create an assignment and then run:

```no-highlight
gkeep new example1 inclass
```

The system will create a folder named `example1` that contains the files in 
`~/.config/git-keeper/templates/inclass`.  You can add your code to `base_code`
and then upload and publish the assignment.


### Update an Assignment

In this tutorial, you will update an existing assignment. 

#### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer
* A class named `cs100f22` added to the server
* The [`project1` example assignment](#a-simple-assignment-from-the-default-template) created and uploaded (but not published)**

#### Overview

The `gkeep update` command is used to modify an existing assignment.  *Before* an assignment is 
published, `gkeep update` can be used to modify any aspect of an assignment (base code, email, 
tests, configuration).  Once an assignment is published, each student has a copy of the base code
repo and has received the announcement email, and therefore only the tests and configuration
may be changed with `gkeep update`.


#### Example: Update the Email Before Publish

Edit `project1/email.txt`:

```no-highlight
Your first project is to implement a function to validate
a username.  See Canvas for details.
```

Update the assignment:

```no-highlight
gkeep update cs100f22 project1 email
```

The output should be:

```no-highlight
updating project1 in cs100f22
Assignment updated successfully
```

And you should have an email containing:

```no-highlight
Clone URL:
ssh://prof1@gkserver/home/prof1/prof1/cs100f22/project1.git

Your first project is to implement a function to validate
a username.  See Canvas for details.
```

#### Example: Update Base Code Before Publish

Edit `project1/base_code/proj1.py`:

```
def is_valid(username):
    """
    A username is valid if it contains only lowercase
    letters, numbers, and the underscore character.
    In addition, it must start with a letter.
    """
    return False
```

Update the assignment:

```no-highlight
gkeep update cs100f22 project1 base_code
```

The output should be:

```no-highlight
updating project1 in cs100f22
Assignment updated successfully
```

And you should have an email containing:

```no-highlight
Clone URL:
ssh://prof1@gkserver/home/prof1/prof1/cs100f22/project1.git

Your first project is to implement a function to validate
a username.  See Canvas for details.
```

In addition, if you clone the repo you will find a *single* commit that 
contains the base code.  This ensures that students only see the final
version of the assignment when they clone the repo.

#### Other Updates

Before you publish an assignment, you can update the `tests` or `config`
in a similar way to the previous examples.

If you need to update multiple aspects of an assignment, modify all the files
and then run

```no-highlight
gkeep update cs100f22 project1 all
```

#### Example: Base Code Cannot be Updated After Publish

First, publish the assignment

```no-highlight
gkeep publish cs100f22 project1
```

The output should be: 

```no-highlight
Publishing assignment project1 in class cs100f22
Assignment successfully published
```

Now edit `project1/base_code`:

```
# Name:
def is_valid(username):
    """
    A username is valid if it contains only lowercase
    letters, numbers, and the underscore character.
    In addition, it must start with a letter.
    """
    return False
```

And attempt to update:

```no-highlight
gkeep update cs100f22 project1 base_code
```

The output should be:

```no-highlight
Assignment is already published, only tests or config may be updated.
```

You cannot update the base code of an assignment after it is published.  The publish
action creates a copy of the repo in each student's account, and they may have cloned
their repo.  Making a change to the student repo now could lead to `git` merge 
conflicts.

If you publish an assignment and later have to change the code, you will have to 
distribute these changes **outside** of `git-keeper` (for example, post an announcement
on your LMS).

#### Example: Update Tests After Publish

Edit `project1/tests/test_proj1.py`:

```
from proj1 import is_valid

def verify_result(case, expected):
    result = is_valid(case)
    if result == expected:
        print('GOOD: is_valid({}) returns {}'.format(case, expected))
    else:
        print('ERROR: is_valid({}) should return {}'.format(case, expected))

print('Here are the results from a few test cases:')

verify_result('username', True)
verify_result('Username', False)
verify_result('user_name', True)
verify_result('_username', False)

print('"GOOD" for all cases does not guarantee a correct solution.')
print('When grading I will test additional cases!')
```

Edit `project1/tests/action.sh`:

```
export PYTHONPATH=$1
python3 test_proj1.py
exit 0
```

Update the assignment:

```no-highlight
gkeep update cs100f22 project2 tests
```

The output should be:

```no-highlight
updating project2 in cs100f22
Assignment updated successfully
```

Keep in mind that students may have already submitted, and `git-keeper` **WILL NOT** 
automatically rerun tests.  You can use the `gkeep trigger` command to manually run
tests.


### Trigger Tests for One or More Students

In this tutorial you will trigger tests for one or more students.

#### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer
* A class named `cs100f22` added to the server
* The [`project1` example assignment](#a-simple-assignment-from-the-default-template) created, uploaded, and published


#### Overview

The `gkeep trigger` command causes the `action.sh` or `action.py` script of an assignment
to be executed for the current repos of one or more students.  This is useful if a
student deletes the `git-keeper` response email or if you change the tests for an
assignment after it is published.

#### Trigger Tests For the Entire Class

To trigger tests for all students in the class:

```no-highlight
gkeep trigger cs100f22 project1
```

The output will ask for confirmation:

```no-highlight
Triggering tests for project1 in class cs100f22 for the following students:
mhamilton
ghopper
alovelace
Proceed? (Y/n) y
Tests triggered successfully
```

The `action.sh` will run with each student's repo regardless of whether they have pushed
changes.

#### Trigger Tests for a Subset of Students

To trigger the tests for a subset of students

```no-highlight
gkeep trigger cs100f22 project1 ghopper alovelace
```

The output will ask for confirmation:

```no-highlight
Triggering tests for project1 in class cs100f22 for the following students:
ghopper
alovelace
Proceed? (Y/n) y
Tests triggered successfully
```

### Delete or Disable an Assignment

In this tutorial, you will delete an unpublished assignment and disable a
published assignment.

#### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer
* A class named `cs100f22` added to the server
* The [`project1` example assignment](#a-simple-assignment-from-the-default-template) created and uploaded (but not published)

#### Overview

Before you publish an assignment, it is safe to delete it from the server because it only exists 
in your account.   After you publish an assignment, you can no longer delete it because each
student in the class has a copy of the repo (and they may have already cloned that repo).  In 
this case your only option is to disable the assignment.

#### Example: Delete an Unpublished Assignment

At this point, the `project1` assignment is uploaded but not published.  The repo exists
in your faculty account, but it has not been copied to the students' accounts.  Therefore,
it is safe to delete the assignment:

```no-highlight
gkeep delete cs100f22 project1
```

The output asks for confirmation:

```no-highlight
Deleting assignment project3 in class cs100f22
Proceed? (Y/n) y
Assignment deleted successfully
```

#### Example: Disable a Published Assignment

If you completed the first example, re-upload the assignment:

```no-highlight
gkeep upload cs100f22 project3
```

The output should be:

```no-highlight
uploading project3 in cs100f22
Assignment uploaded successfully
```

Regardless of whether you completed the previous example, publish the assignment:

```no-highlight
gkeep publish cs100f22 project1
```

The output should be:

```no-highlight
Publishing assignment project3 in class cs100f22
Assignment successfully published
```

Now try to delete the assignment:

```no-highlight
gkeep delete cs100f22 project1
```

The output should be:

```no-highlight
Assignment project1 is published and cannot be deleted.
Use gkeep disable if you wish to disable this assignment.
```

You cannot delete a published assignment because the students already received their
announcement emails, and they may have cloned the assignment.

Instead, you must disable the assignment:

```no-highlight
gkeep disable cs100f22 project1
```

The output asks for confirmation:

```no-highlight
Disabling assignment projet1 in class cs100f22. This cannot be undone.
Students will be notified that the assignment has been disabled.
The action.sh/action.py script will no longer be run on submissions
to this assignment.  Instead, students will receive an email stating
that the assignment is disabled.
Proceed? (Y/n) y
Assignment disabled successfully
```

The students in the class receive an email:

```no-highlight
Assignment project1 in class cs100f22 has been disabled. No tests will be run if you push to your repository for this assignment.
```

If the student pushes to the repo, they will receive an email:

```no-highlight
Assignment project1 in class cs100f22 has been disabled.
```
