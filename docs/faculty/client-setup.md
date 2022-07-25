# Client Setup

This guide details how to setup a faculty machine to use the git-keeper
client. The client has been used successfully in OS X and Linux. It may work in
Windows using Cygwin or the Windows Subsystem for Linux but that has not been
tested.

## Requirements

The client requires Git and Python3.

### OS X

If you run `git` in a terminal it will prompt you to install the Xcode tools
(which contain Git) if they are not already installed.

Download and install Python3 from [python.org](https://www.python.org/).

### Linux

Git and Python3 should be straightforward to install on a Linux system through
your distribution's package manager.

## Installing the Client

To install the client system-wide, run the following command:

```
sudo python3 -m pip install git-keeper-client
```

Alternatively, you may want to install the client in a
[Python virtual environment](https://docs.python.org/3/tutorial/venv.html) if
you do not want to clutter your system's Python packages.

## Configuration

There must be a configuration file at `~/.config/git-keeper/client.cfg`. You
may create this file manually, or use the `gkeep config` command to generate it
for you.

`client.cfg` requires a section called `[server]` which defines the hostname of
the server, your faculty username on the server, and optionally the SSH
server's port number which defaults to 22.

There is also an optional section `[local]` in which you can define a directory
into which `gkeep` will fetch submissions.  If present, this *must* be an
absolute path.

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
```

## SSH Key

The client communicates with the server over SSH. You will need to copy your
SSH public key to the git-keeper server so that you can make SSH connections
without a password.

If you have never generated a public key, do so now:

```
ssh-keygen
```

All the defaults should be fine, you can press enter repeatedly to step through
the menus.

Now you need to copy your public key to your git-keeper server. If your faculty
username on the server is `<username>` and the hostname of your server is
`<hostname>`, run this:

```
ssh-copy-id <username>@<hostname>
```

## Usage

Now you should be able to run `gkeep` commands. Running `gkeep` without any
arguments will display a usage message.
