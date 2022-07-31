Faculty users interact with the git-keeper server using the `gkeep` client
application. For information about installing the client, see [Client Setup]().

# Configuration

The default configuration file path for `gkeep` is
`~/.config/git-keeper/client.cfg`. This file can be created using the
`gkeep config` command, or edited manually. An alternate configuration file
path may be specified using `--config_file <file path>` or `-f <file path>`.

The configuration file is read using Python's `ConfigParser`, and as such must
be written using the corresponding
[INI File Structure](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure).

## Server Section

The `[server]` section is required, and has the following fields:

* `host` (required): the hostname of the server
* `username` (required): the user's account username
* `ssh_port` (optional, defaults to 22): the SSH port of the server

## Local Section

The `[local]` section is optional and has the following fields:

* `submissions_path` (optional): A path to a directory in which to fetch
  student submissions from the server. If this is not specified, each
  assignment's submissions must be fetched independently into individual
  locations.
* `templates_path` (optional, defaults to `~/.config/git-keeper/templates`): A
  path to a directory containing assignment templates to use with `gkeep new`

## Class Aliases Section

The `[class_aliases]` section is optional, and is used to define aliases for
class names. For example, the following section defines the alias `100` for the
class `cs100f22`, allowing `100` to be used in place of `cs100f22` whenever
`gkeep` expects a class name:

```
[class_aliases]
100 = cs100f22
```

Multiple aliases may be defined in this section.

# Actions

`gkeep` has numerous sub-commands to carry out various actions for faculty
users.

## check

Checks that `gkeep` is properly configured and can communicate with the
server. Parses the configuration file, connects to the server, and retrieves
information about the server.

Usage: `gkeep check`

## add

Adds a new class on the server.

Usage: `gkeep add <class name> [<csv filename>]`

* `<class name>`: Name of the new class. See [Class Names]() for valid names.
* `<csv filename>`: Path to a class roster, with lines of the form
  `Last,First,email@school.edu`. If omitted, an empty class will be created and
  students can be added later.

## modify

Modifies an existing class on the server.

Usage: `gkeep modify <class name> <csv filename>`

* `<class name>`: Name of an existing class to modify
* `<csv filename>`: Path to the updated roster, in the same format as for
  `gkeep add`

## new

Creates a directory containing base files for a new assignment. By default
empty files and directories will be created, but the user can create
[Template Directories]() to create custom assignment templates.

Usage: `gkeep new <path to assignment folder> [<template name>]`

* `<path to assignment folder>`: Path of the directory that will be created for
  the assignment
* `<template name>`: Optional template name. If omitted, a default template
  will be used. If provided, specifies the name of a template in the
  [Templates Directory]().

## upload

Uploads a new assignment to the server. The name of the directory containing
the assignment files will be the name of the assignment. See
[Assignment Names]() for information about valid names.

The faculty user receives the email that will be sent to the students when the
assignment is published, and the faculty user can submit solutions to test the
tests before publishing the assignment.

Usage: `gkeep upload <class name> <assignment directory>`

* `<class name>`: Name of an existing class in which to add the assignment
* `<assignment directory>`: Path to a directory containing the assignment
  files. See [Assignment Directories]() for details about the required
  structure.

## update

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

## publish

Publish an uploaded assignment. Each student in the class will receive an email
with a clone URL for the assignment and the contents of the assignment's
`email.txt`.

Usage: `gkeep publish <class name> <assignment name>`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name

## delete

Delete an assignment. The assignment must not be published. Published
assignments may be disable with `gkeep disable` instead.

Usage: `gkeep delete <class name> <assignment name>`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name

## disable

Disable a published assignment. If students attempt to submit to a disabled
assignment, no tests will be run. Instead they will receive an email that the
assignment has been disabled.

Usage: `gkeep disable <class name> <assignment name>`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name

## fetch

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
option is set in the [Client Configuration]().

Usage: `gkeep fetch <class name> <assignment name> [<destination>]`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name
* `<destination>`: Optional path to a directory in which to fetch assignment
  submission data. The assignment submission data will be fetched to the
  directory `<destination>/<assignment name>`. If `<destination>` is omitted,
  it will either be set to the current working directory or to the
  `submissions_path` specified in the [Client Configuration]()

## query

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

## trigger

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

## passwd

Reset the password of a student user. A new password will be randomly generated
and emailed to the student.

Usage: `gkeep passwd <username>`

* `<username>`: Username of the user whose password will be reset

## test

Submits a solution to the server to be tested in the same manner that student
submissions are tested, and results are sent via email. This can be used to
test the tests before publishing an assignment.

Usage: `gkeep test <class name> <assignment name> <solution path>`

* `<class name>`: Name of the class containing the assignment
* `<assignment name>`: The name of the assignment, or a path to a directory
  whose name matches the assignment name
* `<solution path>`: The path to a directory containing a solution for the
  assignment

## config

Writes a `gkeep` configuration file to `~/.config/git-keeper/config.cfg`. The
user is prompted to enter values for the various fields.

Usage: `gkeep config`

## status

Changes the status of a class to `open` or `closed`. If a class is closed,
tests will not be run if a student pushes a new submission, and the student
will recieve an email that says the class is closed. Closed classes will be
omitted when listing assignments and students using [`gkeep_query`]().

Usage: `gkeep status <class name> <class status>`

* `<class name>`: Name of the class to open or close
* `<class status>`: New status for the class, either `open` or `closed`

## add_faculty

Adds a new faculty user. The user running this command must be an admin
user. An account will be created for the user, and the username will be based
on the user's email address. See [Account Usernames]() for more information on
usernames.

Usage: `gkeep add_faculty <last name> <first name> <email address>`

* `<last name>`: Last name of the new faculty user
* `<first name>`: First name of the new faculty user
* `<email address>`: Email address of the new faculty user

## admin_promote

Promotes an existing faculty user to an admin user. The user running this
command must be an admin user. The first admin user must be specified in the
[Server Configuration]().

Usage: `gkeep admin_promote <email address>`

* `<email address>`: Email address of the facutly user to promote

## admin_demote

Remove admin privileges for a user.

Usage: `gkeep admin_demote <email address>`

* `<email address>`: Email address of the facutly user to demote
