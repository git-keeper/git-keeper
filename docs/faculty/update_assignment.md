
## Update an Assignment

In this tutorial, you will update an existing assignment. 

### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer
* A class named `cs100f22` added to the server
* The [`project1` example assignment](new_assignment.md) created and uploaded (but not published)

## Overview

The `gkeep update` command is used to modify an existing assignment.  *Before* an assignment is 
published, `gkeep update` can be used to modify any aspect of an assignment (base code, email, 
tests, configuration).  Once an assignment is published, each student has a copy of the base code
repo and has received the announcement email, and therefore only the tests and configuration
may be changed with `gkeep update`.


## Example: Update the Email Before Publish

Edit `project1/email.txt`:

```
Your first project is to implement a function to validate
a username.  See Canvas for details.
```

Update the assignment:

```
gkeep update cs100f22 project1 email
```

The output should be:

```
updating project1 in cs100f22
Assignment updated successfully
```

And you should have an email containing:

```
Clone URL:
prof1@gkserver:/home/prof1/prof1/cs100f22/project1.git

Your first project is to implement a function to validate
a username.  See Canvas for details.
```

## Example: Update Base Code Before Publish

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

```
gkeep update cs100f22 project1 base_code
```

The output should be:

```
updating project1 in cs100f22
Assignment updated successfully
```

And you should have an email containing:

```
Clone URL:
prof1@gkserver:/home/prof1/prof1/cs100f22/project1.git

Your first project is to implement a function to validate
a username.  See Canvas for details.
```

In addition, if you clone the repo you will find a *single* commit that 
contains the base code.  This ensures that students only see the final
version of the assignment when they clone the repo.

## Other Updates

Before you publish an assignment, you can update the `tests` or `config`
in a similar way to the previous examples.

If you need to update multiple aspects of an assignment, modify all the files
and then run

```
gkeep update cs100f22 project1 all
```

## Example: Base Code Cannot be Updated After Publish

First, publish the assignment

```
gkeep publish cs100f22 project1
```

The output should be: 

```
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

```
gkeep update cs100f22 project1 base_code
```

The output should be:

```
Assignment is already published, only tests or config may be updated.```
```

You cannot update the base code of an assignment after it is published.  The publish
action creates a copy of the repo in each student's account, and they may have cloned
their repo.  Making a change to the student repo now could lead to `git` merge 
conflicts.

If you publish an assignment and later have to change the code, you will have to 
distribute these changes **outside** of `git-keeper` (for example, post an announcement
on your LMS).

## Example: Update Tests After Publish

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

```
gkeep update cs100f22 project2 tests
```

The output should be:

```
updating project2 in cs100f22
Assignment updated successfully
```

Keep in mind that students may have already submitted, and `git-keeper` **WILL NOT** 
automatically rerun tests.  You can use the `gkeep trigger` command to manually run
tests.
