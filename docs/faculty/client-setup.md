# Client Setup

This guide details how to set up a faculty machine to use the git-keeper
client. The client has been used successfully in OS X and Linux. It may work in
Windows using Cygwin or the Windows Subsystem for Linux but that has not been
fully tested.

## Requirements

The client requires [Git](https://git-scm.com/downloads) and [
Python 3.8 or greater](https://www.python.org/downloads/).

In addition, you need the username and password sent to you by the 
`git-keeper` server.  This account must be created by the `git-keeper`
server.  For the faculty admin, your account is created the first time
you run `gkeepd`.  For other faculty, the faculty admin must use
`gkeep add_faculty` to create the account.

## Installing the Client

To install the client system-wide, run the following command:

```
sudo python3 -m pip install git-keeper-client
```

Alternatively, you may want to install the client in a
[Python virtual environment](https://docs.python.org/3/tutorial/venv.html) if
you do not want to clutter your system's Python packages.

## Configuration

There must be a configuration file at `~/.config/git-keeper/client.cfg`. The easiest
way to create this file is to run `gkeep config`, which will prompt you for various
values and then create the file.

If you create `client.cfg` manually, you must include a section called `[server]` which 
defines the hostname of the server, your faculty username on the server, and optionally the SSH
server's port number which defaults to 22.

You may also include an optional section `[local]` in which you can define a directory
into which `gkeep` will fetch submissions and the directory where assignment templates
are stored.  If present, these *must* be an absolute path.

Here is an example `client.cfg`:

```
[server]
host = gitkeeper.myhostname.com
username = myfacultyusername
# optional
ssh_port = 22

# optional section
[local]
submissions_path = ~/submissions
template_path = ~/gkeep_templates
```

## SSH Key

The client communicates with the server over SSH, and it requires SSH keys so that you 
can make SSH connections without a password.

If you have never generated a public key, do so now:

```
ssh-keygen
```

Use the default filename, and do **NOT** set a password for the key.

Next, copy your public key to your git-keeper server:

```
ssh-copy-id <username>@<hostname>
```

## Check Your Configuration

To verify that everything is configured correctly, run

```
gkeep check
```

The output should something look like:

```
/home/turing/.config/git-keeper/client.cfg parsed without errors

Successfully communicated with gkserver

Server information:
  Version: 0.3.1
  gkeepd uptime: 29m21s
  Firejail installed: True
  Docker installed: True
```

## Getting Help

Run `gkeep` with no arguments to see a usage message.  Run `gkeep` with a subcommands
and no additional arguments to see a usage message for that subcommand.
