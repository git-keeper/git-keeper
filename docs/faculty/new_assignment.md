
## Tutorial: A Simple Assignment From the Default Template

In this tutorial you will create a simple assignment and upload it to
the `git-keeper` server.

### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer
* A class named `cs100f22` added to the server

## Overview

The `gkeep new` is a fast way to create the required files and directory 
structure for an assignment.

Use the `gkeep new` command to create an assignment named `project1`.

```
gkeep new project1
```

Edit `project1/base_code/proj1.py`:

```
def is_valid(username):
    return False
```

Edit `project1/email.txt`:

```
Your first project.  See Canvas for details.
```

Edit `project1/tests/action.sh`:

```
echo "Your submission was received"
exit 0
```

Upload the assignment:

```
gkeep upload cs100f22 project1
```

The output should be:

```
uploading project1 in cs100f22
Assignment uploaded successfully
```

And you should have an email containing:

```
Clone URL:
prof1@gkserver:/home/prof1/prof1/cs100f22/project1.git

Your first project.  See Canvas for details.
```

(where `prof1` is your username on the `git-keeper` server).