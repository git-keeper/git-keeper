# Assignments

Assignments are distributed to students via emails which contain Git clone URLs
which the students use to obtain a Git repository in which to do their work and
optional additional text. Faculty users create tests to go with each assignment
which will be run when students push assignment submissions back to the
server. Students receive tests results via email.

There are numerous [`gkeep` commands]() for working with assignments.

## Structure

Faculty users define assignments in a directory with the following structure:

```
assignment_name
├── assignment.cfg (optional)
├── base_code
│   └── (starting code, README, etc. go here)
├── email.txt
└── tests
    ├── action.sh or action.py
    └── (additional files to support tests go here)
```

### Assignment Names

The name of the assignment is defined by the name of the directory. Assignment
names may only contain characters `A-Z`, `a-z`, `0-9`, `-`, and `_`. The word
`all` is reserved and may not be used as an assignment name.

### Assignment Configuration

The optional `assignment.cfg` file can be used to customize the testing
environment and the emails sent to students. It must use Python's
[INI File Structure](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure)
and may contain the sections `[tests]` and/or `[email]`.

Below is an example `assignment.cfg`:

```
[tests]
env: firejail
timeout: 15
memory_limit: 512

[email]
use_html: false
announcement_subject: [{class_name}] New assignment: {assignment_name}
results_subject: [{class_name}] {assignment_name} submission test results
```

#### Tests Configuration

The `env` field defines the type of testing environment, which must be `host`,
`firejail`, or `docker`. See [Testing Environments](testing-environments.md)
for more details.

The `timeout` field specifies a timeout in seconds. If the timeout is exceeded
during testing, testing halts and the student receives an email that there was
a timeout. Using this setting overrides the timeout value in the
[Server Configuration]().

The `memory_limit` field specifies a memory limit in megabytes. If the memory
limit is exceeded during testing, testing halts and the student receives an
email that something went wrong during testing. Using this setting overrides
the memory limit defined in the [Server Configuration]().

#### Email Configuration

The `use_html` option specifies whether or not to use HTML in test results
emails to display the text in a monospace font. This overrides the value set in
the [Server Configuration]().

The `announcement_subject` option can be used to specify a custom subject line
for new assignment announcement emails. The strings `{class_name}` and
`{assignment_name}` will be replaced by the class name and assignment name.

The `results_subject` option works similarly to specify a custom subject line
for test results emails for the assignment.

### Base Code

The contents of the required `base_code` directory will be used to create
initial Git repositories for each student in the class. Since Git repositories
cannot be empty, this directory must contain at least one file, which can be
empty.

### Email Text

The text within the required `email.txt` file will be appended to the new
assignment announcement email after the clone URL. This file may be empty.

### Tests

The `tests` directory must contain an action script (either `action.sh` or
`action.py`) which will be run when a student pushes a submission. The tests
directory may contain any number of additional files and directories to support
testing. The action script is passed a path to a clone of the student's
submission repository as its first argument, so that the action script may
access the student files.

The output of running the action script (both standard output and standard
error) is placed in the email sent to the student, and in the reports
repository for the assignment.
