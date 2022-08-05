# User Accounts

The two main categories of users that are created by `gkeepd` on the server
are *faculty users* and *student users*. Additionally there are two
special users used by `gkeepd`: `tester` and `keeper`.

## The `keeper` User

The `keeper` user is the user that runs `gkeepd`. This user is created manually
during [Server Setup](). The `keeper` user has full `sudo` privileges and
creates all of the other accounts on the server.

## The `tester` User

The `tester` user is used for running tests. It has no `sudo` permissions, and
cannot access any other users' home directories. The `tester` user is created
automatically when running `gkeepd` for the first time.

## Faculty Users

A faculty user is created by an admin faculty user, and a new faculty user will
receive an email with the username and password for their account.

All facutly users can create and modify classes and assignments using the
[`gkeep` client](). *Admin* faculty users can create additional faculty users
using [`gkeep add_faculty`](), promote other faculty users to admin using
[`gkeep admin_promote`](), and demote other faculty users from admin using
[`gkeep admin_demote`](). The first admin user is defined in the
[Server Configuration]().

Facutly users can log into their accounts on the server normally using SSH, but
should refrain from manually modifying any of the files in their home
directories that are managed by `gkeepd`.

If a facutly user is added to a class owned by another faculty user, then they
become both a faculty and student user, without the [Git shell]() restrictions
placed on normal student users.

## Student Users

A student user is created by `gkeepd` when a class is added or modified to
contain a student that does not yet have an account. A new student user will
receive an email with the username and password for their account.

### Git Shell

Students can use SSH to log into their accounts on the server, but the Git
shell limits them to only being able to run the `passwd` command.

If a student user becomes a faculty user, this restriction is lifted.

## Account Usernames

The username of a new user is based on the user's email address. If the
username portion of a new user's email address is not a valid Linux username,
normalization is performed to create a username with characters omitted, or
substituted with approximations. If a user is added with an email address whose
username portion matches that of another user (say `jsmith@xavier.edu` is added
when `jsmith@moravian.edu` already exists), then a number is added at the end
of the username to make it unique.
