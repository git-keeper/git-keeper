# Server

The server side of git-keeper is implemented by the `gkeepd` application. See
the [Server Setup]() guide for a walk-through of how to set up the server.

## Dependencies

`gkeepd`, must run on a Linux system. It is very highly recommended that the
Linux system be dedicated to running `gkeepd` and nothing else, since `gkeepd`
needs to create accounts on the machine and manage files in users' home
directories.

The system must be able to send emails, so access to an SMTP server is
required.

`gkeepd` also requires Git and Python 3.8 or higher. By default, the Firejail
sandboxing tool is used to run tests. This setting can be changed, but it is
highly recommended that Firejail be installed for added security. Docker may
also be used as a testing environment.
