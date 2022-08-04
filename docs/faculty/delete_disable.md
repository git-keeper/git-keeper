## Delete or Disable an Assignment

In this tutorial, you will delete an unpublished assignment and disable a
published assignment.

### Prerequisites

* A working `git-keeper` server
* A faculty account on the server
* The `gkeep` client setup on your computer
* A class named `cs100f22` added to the server
* The [`project1` example assignment](new_assignment.md) created and uploaded (but not published)

## Overview

Before you publish an assignment, it is safe to delete it from the server because it only exists 
in your account.   After you publish an assignment, you can no longer delete it because each
student in the class has a copy of the repo (and they may have already cloned that repo).  In 
this case your only option is to disable the assignment.

## Example: Delete an Unpublished Assignment

At this point, the `project1` assignment is uploaded but not published.  The repo exists
in your faculty account, but it has not been copied to the students' accounts.  Therefore,
it is safe to delete the assignment:

```
gkeep delete cs100f22 project1
```

The output asks for confirmation:

```
Deleting assignment project3 in class cs100f22
Proceed? (Y/n) y
Assignment deleted successfully
```

## Example: Disable a Published Assignment

If you completed the first example, re-upload the assignment:

```
gkeep upload cs100f22 project3
```

The output should be:

```
uploading project3 in cs100f22
Assignment uploaded successfully
```

Regardless of whether you completed the previous example, publish the assignment:

```
gkeep publish cs100f22 project1
```

The output should be:

```
Publishing assignment project3 in class cs100f22
Assignment successfully published
```

Now try to delete the assignment:

```
gkeep delete cs100f22 project1
```

The output should be:

```
Assignment project1 is published and cannot be deleted.
Use gkeep disable if you wish to disable this assignment.
```

You cannot delete a published assignment because the students already received their
announcement emails, and they may have cloned the assignment.

Instead, you must disable the assignment:

```
gkeep disable cs100f22 project1
```

The output asks for confirmation:

```
Disabling assignment project1 in class cs100f22. This cannot be undone.
Students will be notified that the assignment has been disabled.
Tests will no longer be run on submissions to this assignment.
Proceed? (Y/n) y
Assignment disabled successfully
```

The students in the class receive an email:

```
Assignment project3 in class cs100f22 has been disabled. No tests will be run if you push to your repository for this assignment.
```

If the student pushes to the repo... FIXME this is a bug.
