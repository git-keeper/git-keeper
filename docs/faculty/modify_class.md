
Faculty can use the `gkeep modify` command to:

* Add new students to a class
* Remove students from a class
* Change a student's name (e.g. fix a typo)
* Change a student's email address

The system uses the email address to identify the student, so it will 
consider a change of email address as removing the old account and
adding a new account.

Faculty can make multiple changes to the CSV file and then run `gkeep modify`
to make all the changes at once.  The system will show you the changes and prompt 
you for confirmation.

## Examples

In the following examples, assume you have a class named `cs1f22` based on the 
file `cs1f22.csv`:

```
Hamilton,Margaret,mhamilton@example.edu
Hopper,Grace,ghopper@example.edu
Lovelace,Ada,alovelace@example.edu
```

### Example: Add a New Student to a Class

Edit the class CSV file to add the student information:

```
Hamilton,Margaret,mhamilton@example.edu
Hopper,Grace,ghopper@example.edu
Lovelace,Ada,alovelace@example.edu
Turing,Alan,turninga@example.edu
```

Modify the class enrollment and confirm the changes

```
gkeep modify cs1f22 cs1f22.csv
```

The output will be:

```
Modifying class cs1f22

The following students will be added to the class:
Turing, Alan, turninga@example.edu

Proceed? (Y/n) y
Students added successfully
```

### Example: Remove a Student from a Class

Edit the class CSV file to remove the student information (removing Grace Hopper in this example):

```
Hamilton,Margaret,mhamilton@example.edu
Lovelace,Ada,alovelace@example.edu
```

Modify the class enrollment and confirm the changes

```
gkeep modify cs1f22 cs1f22.csv
```

The output will be:

```
Modifying class cs1f22

The following students will be removed from the class:
Hopper, Grace, ghopper@example.edu

Proceed? (Y/n) y
Students removed successfully
```

### Example: Change the Name of a Student

Edit the class CSV file to update the student name (change "Margaret" to "Maggie" in this example):

```
Modifying class cs1f22

The following student names will be updated:
Hamilton, Margaret -> Hamilton, Maggie

Proceed? (Y/n) y
Students modified successfully
```

### Example: Change the Email Address of a Student

Edit the class CSV file to update the student email address (change Ada's email 
to "alovelace@babbage.edu" in this example):

Modify the class enrollment and confirm the changes:

```
gkeep modify cs1f22 cs1f22.csv
```

The output will be:

```
Modifying class cs1f22

The following students will be added to the class:
Lovelace, Ada, alovelace@babbage.edu

The following students will be removed from the class:
Lovelace, Ada, alovelace@example.edu

Proceed? (Y/n) y
Students added successfully
Students removed successfully
```

A new account was created because `git-keeper` uses the email address to identify the student.

NOTE: In this example, the new account on the `git-keeper` server will be `alovelace1` because
the username `alovelace` is associated with the `alovelace@example.edu` email address.

