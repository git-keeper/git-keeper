
## Use an Assignment Template

In this tutorial you will create a template and then use it to create a new assignment.

### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer

## Overview

The `git new` command is used to create a new assignment.  By default, the command creates
the required directories and files for a valid assignment, and then the faculty member modifies
things to create the assignment.  But `gkeep new` can also create an assignment from a template.
This is useful, for example, when you have a common test mechanism for a course.

A template has the same structure as an assignment, but all files are optional:

```
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

## Create a Template

Faculty often use `git-keeper` to distribute code for in-class examples.  In this case, the 
email announcement is typically minimal, and we do not expect students to submit a solution.
We can create an assignment template containing an `email.txt` with the default message
and an `action.sh` that simply reminds students they do not need to submit.

Create the following folders and files

1. Create the folder `~/.config/git-keeper/templates/inclass/base_code`
2. Create the file `~/.config/git-keeper/templates/inclass/email.txt`:
    ```
    This repo contains an in-class example.
    ```
3. Create the file `~/.config/git-keeper/templates/tests/action.sh`:
    ```
    echo 'No need to push in-class examples.
    exit 0
    ```
   
We do not need an `assignment.cfg` because this file is optional and all the default 
values are appropriate.

## Use the template

Go to a directory where you want to create an assignment and then run:

```
gkeep new example1 inclass
```

The system will create a folder named `example1` that contains the files in 
`~/.config/git-keeper/templates/inclass`.  You can add your code to `base_code`
and then upload and publish the assignment.

