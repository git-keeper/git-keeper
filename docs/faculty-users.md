# Faculty Users

This page has guides for faculty users:

* [Client Setup](#client-setup)
* [Creating Classes](#creating-classes)
* [Modifying Classes](#modifying-classes)
* [Class Status](#class-status)
* [Password Reset](#password-reset)
* [Assignments](#assignments)

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
subcommands and no additional arguments to see a usage message for that
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

An Account will be created for any student in the class that does not already
have an account on the server. The account name will be the username portion of
the student's email address. In the case of a duplicate, a number will be added
after the username to create a unique account.  Passwords are randomly
generated.  An email containing the student's username and password will be
sent to the student.

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

In the following examples, assume you have a class named `cs1f22` based on the 
file `cs1f22.csv`:

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
gkeep modify cs1f22 cs1f22.csv
```

The output will be:

```no-highlight
Modifying class cs1f22

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
gkeep modify cs1f22 cs1f22.csv
```

The output will be:

```no-highlight
Modifying class cs1f22

The following students will be removed from the class:
Hopper, Grace, ghopper@example.edu

Proceed? (Y/n) y
Students removed successfully
```

#### Example: Change the Name of a Student

Edit the class CSV file to update the student name (change "Margaret" to
"Maggie" in this example):

```no-highlight
Modifying class cs1f22

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
gkeep modify cs1f22 cs1f22.csv
```

The output will be:

```no-highlight
Modifying class cs1f22

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
class it is open, and it remains open until the faculty explicitly closes it.
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
[Assignment Configuration](#assignment-configuration) for more details.

#### `base_code`

Within the assignment directory there must be a directory named
`base_code`. The contents of this directory will be the initial contents of the
student's repository for the assignment. Put skeleton code, data files,
instructions, etc. in this directory.

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
of the student's repository and and a temporary copy of the tests
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

```no-highlight
bash action.sh ../solution
```

or

```no-highlight
python3 action.py ../solution
```

The output of the action script (both stdout and stderr) are placed in the
email that the student receives as feedback.


### Creating Action Scripts

For some assignments you can write all your tests in bash or Python and so the
only file you need in the `tests` directory is `action.sh` or `action.py`.

For other assignments you may wish to write your tests in another language or
to use a testing framework such as JUnit to test the student code. In that case
you can simply call your tests from `action.sh`.


### Testing Environments

The testing environment for an assignment can be specified in the optional file
`assignment.cfg` within the assignment directory. If this file does not exist
for a given assignment, the assignment will use the default testing
environment. This will be `firejail`, unless specified otherwise in the
[Server Configuration]().

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
sure the assignment works as expected by cloning it and pushing some solutions.

If you discover errors in your assignment you can update it before sending it
to the students. You can modify the any one of the three components of the
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

You can create your own template assignment in `~/.config/git-keeper/templates`
and then add a template name to `gkeep new` to create an assignment from that
template.

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

