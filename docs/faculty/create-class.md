To create a class you first need to create a CSV file with the names and email
addresses of the students in the class.  Class names are unique for each faculty
member and cannot be changed.  We recommend you use a naming scheme that includes
information that identifies the course and the term.  For example, `cs100f22`.

To create a class named `cs100f22`, create a file named `cs100f22.csv` containing
something like the following:

```
Hamilton,Margaret,mhamilton@example.edu
Hopper,Grace,ghopper@example.edu
Lovelace,Ada,alovelace@example.edu
```

Now you can add the class on the server using `gkeep`:

```
gkeep add cs100f22 cs100f22.csv
```

An Account will be created for any student in the class that does not already
have an account on the server. The account name will be the username portion of
the student's email address. In the case of a duplicate, a number will be added 
after the username to create a unique account.  Passwords are randomly generated. 
An email containing the student's username and password will be sent to the student.

NOTE: Faculty should save the CSV file in case they need to make changes to
the enrollment of the class on the `git-keeper` server.
