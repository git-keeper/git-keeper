What follows is a guide to creating, uploading, and publishing assignments and
then fetching the students' submissions.

## Assignment Structure

To create an assignment, first create a directory to contain the
assignment. The name of the directory will be the name of the assignment.

### `assignment.cfg` (optional)

The `assignment.cfg` is an optional file that allows a faculty member to
change various behaviors of the test environment.  

* Test environment: in a [Firejail](https://firejail.wordpress.com/) sandbox
  (default), in a [Docker](https://www.docker.com/) container, or
  (not recommended) direcdtly on the host.
* Timeout: the number of seconds before tests are automatically terminated
* Memory Limit: the maximum number of megabytes the testing process can use
* HTML Email: whether the response email should be formatted in a variable-width font
    or a fixed-width font
* Announcement Subject: Format string for the email subject line announcing the assignment
* Results Subject: Format string for the email subject line responding to a submission

If this file is not present, the default values of the server are used.

See [Testing Environments](testing-environments.md) for more details.

### `base_code`

Within the assignment directory there must be a directory named
`base_code`. The contents of this directory will be the initial contents of the
student's repository for the assignment. Put skeleton code, data files,
instructions, etc. in this directory.

### `email.txt`

There must also be a file named `email.txt`. The email that students receive
when a new assignment is published will always contain a clone URL, and the
contents of `email.txt` will be appended to the email after the
URL. `email.txt` may be empty.

### `tests`

A directory named `tests` is also required, which must contain either a shell
script named `action.sh` or a Python script named `action.py`. The `tests`
directory also contains any other code and data files that you will use to test
student code.

When a student submits an assignment to the server it creates a temporary clone
of the student's repository and a temporary copy of the `tests`
directory. With the temporary `tests` directory as its working directory, the
testing environment then runs `action.sh` using `bash` or `action.py` using
`python3`, passing the action script the path to the temporary clone of the
student's directory.

This means that before you upload the assignment you can test your tests
locally by entering the `tests` directory in the terminal and running
`action.sh` or `action.py`, giving it the path to a solution as a command line
argument. It is convenient to also store a `solution` directory in the
assignment directory for testing. This way you can run the following from
inside the `tests` directory to test your tests against your solution:

```
bash action.sh ../solution
```

or

```
python3 action.py ../solution
```

The output of the action script (both stdout and stderr) are placed in the
email that the student receives as feedback.


## Assignment Templates

You can use the command `gkeep new` to create the files and directories required for
an assignment.  For example,

```
gkeep new homework1
```

will create a folder `homework1` in the current directory with the following structure:

```
homework1
├── assignment.cfg
├── base_code
├── email.txt
└── tests
    └── action.sh
```

where `homework1`, `base_code`, and `tests` are folders and `assignment.cfg`, 
`email.txt`, and `action.sh` are empty files.

You can create your own template assignment in `~/.config/git-keeper/templates`
and then add a template name to `gkeep new` to create an assignment from that
template.

For example, 

```
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

## Creating `action.sh`


For some assignments you can write all your tests in bash or Python and so the
action script is the only file you need in the `tests` directory.

For other assignments you may wish to write your tests in another language or
to use a testing framework such as JUnit to test the student code. In that case
you can simply call your tests from `action.sh`.

## Example

Here is an example where the tests are written entirely in `action.sh` and
tests are run directly on the server.

Let's say you want to create an assignment for which students will write a
Python program to print `"Hello, world!"`. You want them to write this program
in an initially empty file named `hello_world.py` and for them to receive
instructions by email.

You might create an assignment structure like this:

```
hw01-hello_world
├── base_code
│   └── hello_world.py
├── email.txt
├── solution
│   └── hello_world.py
└── tests
    ├── action.sh
    └── expected_output.txt
```

where `base_code/hello_world.py` is an empty file, `email.txt` contains
instructions for the assignment, `solution/hello_world.py` contains your
solution, and `tests/expected_output.txt` contains `"Hello, world!"`

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

### Time and Memory Limits

Student code containing infinite loops is troublesome. Let's add the use of
`timeout` and `ulimit` to the example to catch infinite loops or excessive
memory use:

```bash
# Use a 10-second timeout
TIMEOUT=10
# Limit memory use to 400 MB
MEM_LIMIT_MB=400

# ulimit uses KB
MEM_LIMIT_KB=$(($MEM_LIMIT_MB * 1024))

# Set the memory limit
ulimit -v $MEM_LIMIT_KB

# The path to the student's submission directory is in $1
SUBMISSION_DIR=$1

# Run the student's code and put the output (stdout and stderr) in output.txt.
# If execution takes more than 10 seconds the process will be killed
timeout $TIMEOUT python $SUBMISSION_DIR/hello_world.py &> output.txt

# timeout returns an exit code of 124 on a timeout, otherwise it returns the
# exit code of the process it ran
if [ $? -eq 124 ]
then
    echo "Your program ran for too long. Perhaps you have an infinite loop?"
    exit 0
fi

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

## Uploading an Assignment

Let's assume you have created an assignment named `hw01-hello_world`, as in the
example above, which is for the class `CS100`. You can upload the assignment to
the server like so:

```
gkeep upload CS100 hw01-hello_world
```

Uploading an assignment does not immediately send it to your students. If the
assignment uploads successfully you will receive an email that looks just like
the email that the students get when they receive the assignment. You can make
sure the assignment works as expected by cloning it and pushing some solutions.

If you discover errors in your assignment you can update it before sending it
to the students. You can modify the any one of the three components of the
assignment individually, or update everything. To update the entire assignment:

```
gkeep update CS100 hw01-hello_world all
```

Run `gkeep update` without additional arguments for more info.

## Publishing an Assignment

Once you are satisfied with your uploaded assignment you can publish it, which
will send it out to students:

```
gkeep publish CS100 hw01-hello_world
```

Once an assignment is published you cannot update the base code or the email,
but you can update the tests.

## Fetching Submissions

When you want to grade your students' submissions, you can fetch them with
`gkeep fetch`. If you defined `submissions_path` in the `[local]` section of
`client.cfg` then `gkeep` can fetch all your assignments into a common
directory. Otherwrise you need to specify a directory to fetch to.

This will fetch into `submissions_path`:

```
gkeep fetch CS100 hw01-hello_world
```

Fetch into the current directory:

```
gkeep fetch CS100 hw01-hello_world
```

The fetched directory for the assigment contains 2 subdirectories: `reports`
and `submissions`. `reports` contains the text of the emails that your students
received when they submitted. The `submissions` directory contains the code
that your students submitted.
