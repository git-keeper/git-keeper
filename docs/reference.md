# Reference

Below is reference documentation for numerous git-keeper topics.

## User Accounts

The two main categories of users that are created by `gkeepd` on the server
are *faculty users* and *student users*. Additionally there are two
special users used by `gkeepd`: `tester` and `keeper`.

### The `keeper` User

The `keeper` user is the user that runs `gkeepd`. This user is created manually
during [Server Setup](admin-users.md#server-setup). The `keeper` user has full
`sudo` privileges and creates all of the other accounts on the server.

### The `tester` User

The `tester` user is used for running tests. It has no `sudo` permissions, and
cannot access any other users' home directories. The `tester` user is created
automatically when running `gkeepd` for the first time.

### Faculty Users

A faculty user is created by an admin faculty user, and a new faculty user will
receive an email with the username and password for their account.

Passwords are randomly generated, but can be changed by using SSH to connect to
the server and running `passwd`.

 If possible, the username will match the user's email username. See
[Account Usernames](#account-usernames) for more on usernames.

All facutly users can create and modify classes and assignments using the
[`gkeep` client](#client). *Admin* faculty users can create additional faculty
users using [`gkeep add_faculty`](#add_faculty), promote other faculty users to
admin using [`gkeep admin_promote`](#admin_promote), and demote other faculty
users from admin using [`gkeep admin_demote`](#admin_demote). The first admin
user is defined in the [Server Configuration](#server-configuration).

!!! warning

    Facutly users can log into their accounts on the server normally using SSH,
    but should refrain from manually modifying any of the files in their home
    directories that are managed by `gkeepd`.

If a facutly user is added to a class owned by another faculty user, then they
become both a faculty and student user, without the
[Git shell](#student-server-access) restrictions placed on normal student
users.

### Student Users

When a faculty user adds students to a class with
[`gkeep add`](reference.md#add) or [`gkeep modify`](reference.md#modify), the
`git-keeper` server creates an account for any student who does not already
have an account.  When account is made, the system will email the student an
email containing their username and password.

Usernames are generally the username of the email, but modifications will be
made for duplicate usernames or email usernames with inappropriate characters.
See [Account Usernames](#account-usernames) for more information.

Passwords are randomly generated for each student.

If a student already has an account when added to a class, no email is
generated.

#### Sample email

```no-highlight
From: git-keeper@gitkeeper.edu
Subject: New git-keeper account

Hello Sharon,

An account has been created for you on the git-keeper server. Here are your credentials:

Username: colemans
Password: 1ZEZfx3x

If you have any questions, please contact your instructor rather than responding to this email directly.

Enjoy!
```

#### Student Server Access

Student accounts on the `git-keeper` server are not intended to support normal
interactive sessions. If a student connects to the server using SSH, their
account is configured to use the
[git-shell](https://git-scm.com/docs/git-shell), which will only allow them to
use `passwd` to change their password.

#### Student SSH Keys

Most IDEs allow users to store login credentials for remote `git` servers.
However, if students are using the command line Git interface they may wish to
create an SSH key and copy it to the `git-keeper` server so that they do not
need to enter a password when cloning and pushing. Run

```no-highlight
ssh-keygen
```

Use the default filename, and do **NOT** set a password for the key.

Next, copy your public key to your git-keeper server:

```no-highlight
ssh-copy-id <username>@<hostname>
```

### Account Usernames

The username of a new user is based on the user's email address. If the
username portion of a new user's email address is not a valid Linux username,
normalization is performed to create a username with characters omitted, or
substituted with approximations. If a user is added with an email address whose
username portion matches that of another user (say `jsmith@xavier.edu` is added
when `jsmith@moravian.edu` already exists), then a number is added at the end
of the username to make it unique.

## Assignments

Assignments are distributed to students via emails which contain Git clone URLs
which the students use to obtain a Git repository in which to do their work and
optional additional text. Faculty users create tests to go with each assignment
which will be run when students push assignment submissions back to the
server. Students receive tests results via email.

There are numerous [`gkeep` commands](#gkeep-commands) for working with
assignments.

### Structure

Faculty users define assignments in a directory with the following structure:

```no-highlight
assignment_name
├── assignment.cfg (optional)
├── base_code
│   └── (starting code, README, etc. go here)
├── email.txt
└── tests
    ├── action.sh or action.py
    └── (additional files to support tests go here)
```

#### Assignment Names

The name of the assignment is defined by the name of the directory. Assignment
names may only contain characters `A-Z`, `a-z`, `0-9`, `-`, and `_`. The word
`all` is reserved and may not be used as an assignment name.

#### Assignment Configuration

The optional `assignment.cfg` file can be used to customize the testing
environment and the emails sent to students. It must use Python's
[INI File Structure](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure)
and may contain the sections `[tests]` and/or `[email]`.

Below is an example `assignment.cfg`:

```
[tests]
env = firejail
timeout = 15
memory_limit = 512

[email]
use_html = false
announcement_subject = [{class_name}] New assignment: {assignment_name}
results_subject = [{class_name}] {assignment_name} submission test results
```

##### Tests Configuration

The `env` field defines the type of testing environment, which must be `host`,
`firejail`, or `docker`. See
[Testing Environments](faculty-users.md#testing-environments) for more details.

The `timeout` field specifies a timeout in seconds. If the timeout is exceeded
during testing, testing halts and the student receives an email that there was
a timeout. Using this setting overrides the timeout value in the
[Server Configuration](#server-configuration).

The `memory_limit` field specifies a memory limit in megabytes. If the memory
limit is exceeded during testing, testing halts and the student receives an
email that something went wrong during testing. Using this setting overrides
the memory limit defined in the [Server Configuration](#server-configuration).

##### Email Configuration

The `use_html` option specifies whether or not to use HTML in test results
emails to display the text in a monospace font. This overrides the value set in
the [Server Configuration](#server-configuration).

The `announcement_subject` option can be used to specify a custom subject line
for new assignment announcement emails. The strings `{class_name}` and
`{assignment_name}` will be replaced by the class name and assignment name.

The `results_subject` option works similarly to specify a custom subject line
for test results emails for the assignment.

#### Base Code

The contents of the required `base_code` directory will be used to create
initial Git repositories for each student in the class. Since Git repositories
cannot be empty, this directory must contain at least one file, which can be
empty.

#### Email Text

The text within the required `email.txt` file will be appended to the new
assignment announcement email after the clone URL. This file may be empty.

#### Tests

The `tests` directory must contain an action script (either `action.sh` or
`action.py`) which will be run when a student pushes a submission. The tests
directory may contain any number of additional files and directories to support
testing. The action script is passed a path to a clone of the student's
submission repository as its first argument, so that the action script may
access the student files.

The output of running the action script (both standard output and standard
error) is placed in the email sent to the student, and in the reports
repository for the assignment.

## Classes

A class is owned by a single faculty user, and consists of a collection of
students and assignments.

A new class is created using the [`gkeep add`](#add) command, and the roster
can be modified using [`gkeep modify`](#modify).

A class name may only contain the characters `A-Z`, `a-z`, `0-9`, `-`, and `_`.

The status of a class may be `open` or `closed`. If a student tries to submit
to a closed class, tests will not run and they will receive an email that the
class is closed.

## Client

Faculty users interact with the git-keeper server using the `gkeep` client
application. For information about installing the client, see
[Client Setup](faculty-users.md#client-setup).

### Client Configuration

The default configuration file path for `gkeep` is
`~/.config/git-keeper/client.cfg`. This file can be created using the
`gkeep config` command, or edited manually. An alternate configuration file
path may be specified using `--config_file <file path>` or `-f <file path>`.

The configuration file is read using Python's `ConfigParser`, and as such must
be written using the corresponding
[INI File Structure](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure).

#### Server Section

The `[server]` section is required, and has the following fields:

* `host` (required): the hostname of the server
* `username` (required): the user's account username
* `ssh_port` (optional, defaults to 22): the SSH port of the server

#### Local Section

The `[local]` section is optional and has the following fields:

* `submissions_path` (optional): A path to a directory in which to fetch
  student submissions from the server. If this is not specified, each
  assignment's submissions must be fetched independently into individual
  locations.
* `templates_path` (optional, defaults to `~/.config/git-keeper/templates`): A
  path to a directory containing assignment templates to use with `gkeep new`

#### Class Aliases Section

The `[class_aliases]` section is optional, and is used to define aliases for
class names. For example, the following section defines the alias `100` for the
class `cs100f22`, allowing `100` to be used in place of `cs100f22` whenever
`gkeep` expects a class name:

```
[class_aliases]
100 = cs100f22
```

Multiple aliases may be defined in this section.

### gkeep Commands

`gkeep` has numerous sub-commands to carry out various actions for faculty
users.

#### check

Checks that `gkeep` is properly configured and can communicate with the
server. Parses the configuration file, connects to the server, and retrieves
information about the server.

Usage: `gkeep check`

#### add

Adds a new class on the server.

Usage: `gkeep add <class name> [<csv filename>]`

* `<class name>`: Name of the new class
* `<csv filename>`: Path to a class roster, with lines of the form
  `Last,First,email@school.edu`. If omitted, an empty class will be created and
  students can be added later.

#### modify

Modifies an existing class on the server. If students are added after
assignments have been published, the new students will receive new assignment
emails for each published assignment.

Usage: `gkeep modify <class name> <csv filename>`

* `<class name>`: Name of an existing class to modify
* `<csv filename>`: Path to the updated roster, in the same format as for
  `gkeep add`

#### new

Creates a directory containing base files for a new assignment. By default
empty files and directories will be created, but the user can create
[Template Directories](#new-assignment-templates) to create custom assignment templates.

Usage: `gkeep new <path to assignment folder> [<template name>]`

* `<path to assignment folder>`: Path of the directory that will be created for
  the assignment
* `<template name>`: Optional template name. If omitted, a default template
  will be used. If provided, specifies the name of a template in the
  [Templates Directory](#new-assignment-templates).

#### upload

Uploads a new assignment to the server. The name of the directory containing
the assignment files will be the name of the assignment. See
[Assignment Names](#assignment-names) for information about valid names.

The faculty user receives the email that will be sent to the students when the
assignment is published, and the faculty user can submit solutions to test the
tests before publishing the assignment.

Usage: `gkeep upload <class name> <assignment directory>`

* `<class name>`: Name of an existing class in which to add the assignment
* `<assignment directory>`: Path to a directory containing the assignment
  files. See [Assignments](#assignments) for details about the required
  structure.

#### update

Updates an existing assignment on the server. If the assignment is already
published, only a subset of the assignment's items may be updated. The faculty
user will receive an additional email after updating.

Usage: `gkeep update <class name> <assignment directory> <update item>`

* `<class name>`: The class that the assignment belongs to
* `<assignment directory>`: Path to the assignment directory. The directory's
  name must be unchanged, since the assignment name is based on the directory
  name.
* `<update item>`: One of the following:
    * `base_code`: update the contents of the `base_code` directory. This may
      only be updated for unpublished assignments.
    * `email`: Update the contents of `email.txt`. This may only be updated for
      unpublished assignments.
    * `tests`: Update the contents of the `tests` folder. This may be done for
      published assignments. If students have already submitted the tests will
      not be re-run automatically, but can be triggered to run again with
      `gkeep trigger`
    * `config`: Update the contents of `assignment.cfg`
    * `all`: Update all of the above. This may only be updated for unpublished
    assignments.

#### publish

Publish an uploaded assignment. Each student in the class will receive an email
with a clone URL for the assignment and the contents of the assignment's
`email.txt`.

Usage: `gkeep publish <class name> <assignment name>`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name

#### delete

Delete an assignment. The assignment must not be published. Published
assignments may be disable with `gkeep disable` instead.

Usage: `gkeep delete <class name> <assignment name>`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name

#### disable

Disable a published assignment. If students attempt to submit to a disabled
assignment, no tests will be run. Instead they will receive an email that the
assignment has been disabled.

Usage: `gkeep disable <class name> <assignment name>`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name

#### fetch

Fetch student submissions and test results from the server. Submission data
will be placed in a directory with the same name as the assignment, and will
contain two subdirectories, `reports` and `submissions`. The `reports`
directory will contain a subdirectory for each student, and each student
directory will contain one text file for each submission made by the
student. The submission report will contain the same contents as the results
email sent to the student. The `submissions` subdirectory also contains one
subdirectory for each student. Each student directory is a clone of their
submission repository.

The behavior of this command depends on whether or not the `submissions_path`
option is set in the [Client Configuration](#client-configuration).

Usage: `gkeep fetch <class name> <assignment name> [<destination>]`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name
* `<destination>`: Optional path to a directory in which to fetch assignment
  submission data. The assignment submission data will be fetched to the
  directory `<destination>/<assignment name>`. If `<destination>` is omitted,
  it will either be set to the current working directory or to the
  `submissions_path` specified in the
  [Client Configuration](#client-configuration)

#### query

Query the server for data regarding the faculty user's classes, assignments,
and students.

Output can be human readable or in a JSON format to be consumed by other
applications. Below is the JSON structure for the various queries.

Classes:

```json
[
    {
        "name": "class_name",
        "open": true
    },
    ...
]
```

Assignments:

```json
{
    "class_name": [
        {
            "name": "assignment_name",
            "published": true,
            "disabled": false
        },
        ...
    ],
    ...
}
```

Recent:

```json
{
    "class_name": {
        "assignment_name": [
            {
                "time": 1659205175,
                "human_time": "2022-07-30 18:19:35",
                "first_name": "First",
                "last_name": "Last",
                "username": "student1",
                "email_address": "student1@school.edu"
            },
            ...
        ],
        ...
    },
    ...
}
```

Students:

```json
{
    "class_name": [
        {
            "first_name": "First",
            "last_name": "Last",
            "username": "student1",
            "email_address": "student1@school.edu"
        },
        ...
    ],
    ...
}
```

Usage: `gkeep query [--json] <query type> [<number of days>]`

* `--json`: Optional switch to output JSON rather than a human readable list
* `<query type>`: One of the following:
    * `classes`: List all classes. Closed classes will be listed, but marked
      `(closed)`
    * `assignments`: List all assignments in all open classes. Published
      assignments are marked with `P` and unpublished assignments are marked
      with `U`
    * `recent`: List recent submissions
    * `students`: List all sudents in all open classes
* `<number of days>`: Optional number to specify the number of days to consider
  recent. Defaults to 1

#### trigger

Trigger tests to be run on the latest commits in submission repositories for
a list of specified students or all students in the class. This can be used to
re-run tests after updating them. Note that if you trigger tests for a student
that has never submitted, tests will be run against the base code. Tests may be
triggered for the faculty user that owns the class as well.

Usage: `gkeep trigger <class name> <assignment name> [<student username> ...]`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name
* `<student username>`: Optional username or list of user names to trigger
  tests for. If omitted, tests will be triggered for all students in the class.

#### passwd

Reset the password of a student user. A new password will be randomly generated
and emailed to the student.

Usage: `gkeep passwd <username>`

* `<username>`: Username of the user whose password will be reset

#### test

Submits a solution to the server to be tested in the same manner that student
submissions are tested, and results are sent via email. This can be used to
test the tests before publishing an assignment.

Usage: `gkeep test <class name> <assignment name> <solution path>`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name
* `<solution path>`: The path to a directory containing a solution for the
  assignment

#### config

Writes a `gkeep` configuration file to `~/.config/git-keeper/config.cfg`. The
user is prompted to enter values for the various fields.

Usage: `gkeep config`

#### status

Changes the status of a class to `open` or `closed`. If a class is closed,
tests will not be run if a student pushes a new submission, and the student
will recieve an email that says the class is closed. Closed classes will be
omitted when listing assignments and students using [`gkeep_query`](#query).

Usage: `gkeep status <class name> <class status>`

* `<class name>`: Name of the class to open or close
* `<class status>`: New status for the class, either `open` or `closed`

#### add_faculty

Adds a new faculty user. The user running this command must be an admin
user. An account will be created for the user, and the username will be based
on the user's email address. See [Account Usernames](#account-usernames) for
more information on usernames.

Usage: `gkeep add_faculty <last name> <first name> <email address>`

* `<last name>`: Last name of the new faculty user
* `<first name>`: First name of the new faculty user
* `<email address>`: Email address of the new faculty user

#### admin_promote

Promotes an existing faculty user to an admin user. The user running this
command must be an admin user. The first admin user must be specified in the
[Server Configuration](#server-configuration).

Usage: `gkeep admin_promote <email address>`

* `<email address>`: Email address of the facutly user to promote

#### admin_demote

Remove admin privileges for a user.

Usage: `gkeep admin_demote <email address>`

* `<email address>`: Email address of the facutly user to demote

### New Assignment Templates

The [`gkeep new`](#new) command can create a directory structure with empty files
as a skeleton for a new assignment, or it can copy a custom template directory
for you. By default, `gkeep new` looks for templates in
`~/.config/git-keeper/templates`, but this location can be overridden by
setting the `templates_path` option in the
[Client Configuration](#client-configuration).

Note that `gkeep new` does not perform any checks on the template to ensure the
proper structure, it simply performs a copy of the template directory.

### Fetched Submissions

The [`gkeep fetch`](#fetch) command can fetch student submission data to a specified
location. If the location is omitted, then submission data is fetched either
into the current working directory, or into a specified submissions location
specified by the `submissions_path` setting in the
[Client Configuration](#client-configuration).

Submission data for an assignment includes 2 folders: `reports` and
`submissions`. Each of these contains one subdirectory for each student, named
as `last_first_username`. In the reports directory, each student's subdirectory
contains one text file for each submission, containing the test results that
the student received by email. The reports directory is a clone of a Git
repository from the server. In the submissions directory, each student's
subdirectory is a clone of the student's submission repository.

Performing the same fetch command multiple times will not do anything if
nothing has changed since the last fetch, or will pull in updated items if a
student has submitted since the last fetch.

Here is an example structure for feched data in an assignment named
`hello_world` for a class with 2 students that have each submitted once:

```no-highlight
hello_world
├── reports
│   ├── hamilton_margaret_mhamilton
│   │   └── report-2022-07-30_14-19-36-UTC.txt
│   └── hopper_grace_ghopper
│       └── report-2022-07-30_13-25-44-UTC.txt
└── submissions
    ├── hamilton_margaret_mhamilton
    │   └── hello_world.py
    └── hopper_grace_ghopper
        └── hello_world.py
```

There are additional hidden files and directories within this
structure. The `reports` directory and each student subdirectory within
`reports` each contain a `.placeholder` file since these are managed by a Git
repository and may be empty, and Git cannot track empty directories. There are
also `.git` folders within each Git repository in the structure. To make
subsequent fetches run quickly if no data has changed, a `.hash_cache` file is
stored at the assignment directory level which contains the Git hashes of the
`HEAD` commits of each repository.

The full structure including hidden files and directories is below:

```no-highlight
hello_world
├── .hash_cache
├── reports
│   ├── .git
│   │   └── (.git contents omitted for brevety)
│   ├── .placeholder
│   ├── hamilton_margaret_mhamilton
│   │   ├── .placeholder
│   │   └── report-2022-07-30_14-19-36-UTC.txt
│   ├-─ hopper_grace_ghopper
│   │   ├── .placeholder
│   │   └── report-2022-07-30_13-25-44-UTC.txt
└── submissions
    ├── hamilton_margaret_mhamilton
    │   ├── .git
    │   │   └── (.git contents omitted for brevety)
    │   └── hello_world.py
    └── hopper_grace_ghopper
        ├── .git
        │   └── (.git contents omitted for brevety)
        └── hello_world.py
```

## Server

The server side of git-keeper is implemented by the `gkeepd` application. See
the [Server Setup](admin-users.md#server-setup) guide for a walk-through of how
to set up the server.

### Dependencies

`gkeepd`, must run on a Linux system. It is very highly recommended that the
Linux system be dedicated to running `gkeepd` and nothing else, since `gkeepd`
needs to create accounts on the machine and manage files in users' home
directories.

The system must be able to send emails, so access to an SMTP server is
required.

`gkeepd` also requires Git and Python 3.8 or higher. By default, the Firejail
sandboxing tool is used to run tests. This setting can be changed, but it is
highly recommended that Firejail be installed for added security. Docker may
also be used as a testing environment.

### Server Configuration

`gkeepd` is configured with the `server.cfg` file in the `keeper` user's home
directory. Details about all sections and fields are below. There is a
[template `server.cfg`](admin-users.md#template-servercfg) in the
[Admin Users](admin-users.md) guide.

 `server.cfg` has four sections: `[server]`, `[email]`, `[admin]`,
and `[gkeepd]`.

#### `[server]`

The `[server]` section has a single required parameter `hostname`, which is the
hostname of the server. This will be used to build Git URLs.

#### `[email]`

The `[email]` section is also required. The following parameters are required:

```
from_name = <name that the emails will be from>
from_address = <email address that the emails come from>
smtp_server = <hostname of the SMTP server>
smtp_port = <SMTP server port>
```

The following parameters are optional:

```
use_tls = <true or false, defaults to true>
email_username = <username for the SMTP server>
email_password = <password for the SMTP server>
email_interval = <seconds to wait between sending emails>
use_html = <true or false, defaults to false>
```

If `use_html` is true, submission test results will be sent as an HTML email,
placing the contents within pre tags so that they appear in a fixed width font.

#### `[admin]`

The `[admin]` section is also required. The section defines an admin user. The
admin user will automatically be added as a faculty user when the server first
starts, and then the admin user will be able to add additional faculty members.

The following parameters are required:

```
admin_email = <email address of the admin user>
admin_first_name = <first name of the admin user>
admin_last_name = <last name of the admin user>
```

#### `[gkeepd]`

The `[gkeepd]` section is optional. Below are the allowed parameters and their
defaults:

```
test_thread_count = 1
tests_timeout = 300
tests_memory_limit = 1024
default_test_env = firejail
```

The `test_thread_count` parameter specifies how many threads will be used to
run student tests. Multiple threads will allow multiple tests to be run
simultaneously. Be sure to set the `tests_memory_limit` appropriately based on
the number of test threads and the memory available on the system.

The `tests_timeout` parameter specifies a global timeout for tests in case an
assignment's tests fail to properly account for infinite loops. The default is
300 seconds. If this timeout occurs the student's test results will state that
the tests timed out.

Similar to `tests_timeout`, the `tests_memory_limit` sets a global memory limit
for tests. The default limit is 1024 MB. If the memory limit is exceeded, tests
will be halted and the student and faculty users will receive emails that there
was an error running the tests.

The `default_test_env` parameters specifies the test environment that will be
used if an assignment has not defined a test environment in
`assignment.cfg`. The default is `firejail`, but this can also be set to `host`
if Firejail is not available on your server.

!!! warning

    Using `host` as the default test environment is potentially insecure.
