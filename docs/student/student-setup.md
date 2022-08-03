
## Account Creation 

When a faculty uses `gkeep add` to create a new class, the `git-keeper`
server creates an account for any student who does not already have an 
account.  When account is made, the system will email the student an email
containing their username and password.

Usernames are generally the username of the email, but if a duplicate
occurs (e.g. two students with the same username on different email 
servers), the system will append a digit to the end of the second
student to ensure distinct usernames.

Passwords are randomly generated for each student.

If a student already has an account when `gkeep add` is run, no
email is generated.

## Sample email

```
From: git-keeper@gitkeeper.edu
Subject: New git-keeper account

Hello Sharon,

An account has been created for you on the git-keeper server. Here are your credentials:

Username: colemans
Password: 1ZEZfx3x

If you have any questions, please contact your instructor rather than responding to this email directly.

Enjoy!
```

## Student Server Access

Student acounts on the `git-keeper` server are not intended to support normal interactive 
sessions. If a student connects to the server using SSH, their account is configured to use the 
[git-shell](https://git-scm.com/docs/git-shell), 
which will only allow them use `passwd` to change their password.

### Student SSH Keys

Most IDEs allow users to store login credentials for remote `git` servers.  If students wish,
they can create an SSH key and copy it to the `git-keeper` server.  Run

```
ssh-keygen
```

Use the default filename, and do **NOT** set a password for the key.

Next, copy your public key to your git-keeper server:

```
ssh-copy-id <username>@<hostname>
```
