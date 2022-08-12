
## Trigger Tests for One or More Students

In this tutorial you will trigger tests for one or more students.

### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer
* A class named `cs100f22` added to the server
* The [`project1` example assignment](new_assignment.md) created, uploaded, and published


## Overview

The `gkeep trigger` command causes the `action.sh` or `action.py` script of an assignment
to be executed for the current repos of one or more students.  This is useful if a 
student deletes the `git-keeper` response email or if you change the tests for an 
assignment after it is published.

## Trigger Tests For the Entire Class

To trigger tests for all students in the class:

```
gkeep trigger cs100f22 project1
```

The output will ask for confirmation:

```
Triggering tests for project1 in class cs100f22 for the following students:
mhamilton
ghopper
alovelace
Proceed? (Y/n) y
Tests triggered successfully
```

The `action.sh` will run with each student's repo regardless of whether they have pushed
changes.

## Trigger Tests for a Subset of Students

To trigger the tests for a subset of students

```
gkeep trigger cs100f22 project1 ghopper alovelace
```

The output will ask for confirmation:

```
Triggering tests for project1 in class cs100f22 for the following students:
ghopper
alovelace
Proceed? (Y/n) y
Tests triggered successfully
```


