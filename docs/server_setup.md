# Server Setup

This guide details how to set up a server to run git-keeper. The guide assumes
you are starting with a Debian Jessie minimal netinstall
installation. git-keeper should work with any Linux distribution, but the setup
details might be slightly different.

## Quick Start

Here is an overview of the steps necessary to get a git-keeper server up and
running. Follow these if you have done it before and just need a refresher, or
you are experienced with Linux system administration and do not need specific
instructions. Skip to the next section for more detailed instructions.

These instructions assume you have a dedicated server with a Debian
installation and a working SSH server.

* Create the following users:
    * `keeper`. Must be in the `keeper` group.
    * One account for each faculty member. Add the accounts to the `keeper`
    group.
* Edit `/etc/ssh/sshd_config`
    * Remove ecdsa and ed25519 host keys. They do not work with paramiko.
    * Disallow the user `keeper` to log in via SSH: `DenyUsers keeper`
* Install `python3`, `python3-pip`, `libffi-dev`, `libssl-dev`, and `sudo`
* Install `git-keeper` using `pip3`
* Configure `sudo` so that `keeper` can run `useradd`, `usermod`, `chpasswd`,
`groupadd`, `chown`, and `chmod` without a password.


### Requirements

git-keeper requires a server running a Linux operating system which is
dedicated to running git-keeper.

A minimal Debian installation provides a stripped down and stable system which
is well suited to running git-keeper. Tests are run within Docker containers,
so any dependencies required for testing student code will be handled by Docker.
 
The guide assumes you have installed Debian from the minimal network
installation media and that you have enabled the SSH server.

Other Linux distributions will work as well but some of the following steps may
be a little different.

### Create Users

As root, you will need to create at least 2 users.

#### Keeper User

The `keeper` user is the user that will run the git-keeper server process. This
user will have elevated privileges.
 
Create the user. Be sure to choose a strong password:
 
```
adduser keeper
```

Ensure that `keeper` is also in the group `keeper`. This command shows the
groups that `keeper` is in:

```
groups keeper
```

#### Faculty Users

Each faculty member that will be using git-keeper needs an account. For this
guide we will assume there is only one faculty member, and we will create the
user `faculty` for this person to use.

Create the user:

```
adduser faculty
```

Add the user to the `keeper` group:

```
usermod -a -G keeper faculty
```

Repeat for each additional faculty member.

### Configure SSH

Edit the file `/etc/ssh/sshd_config`. You can edit it with the editor `nano`
like so:

```
nano /etc/ssh/sshd_config
```

git-keeper clients use paramiko for communication over SSH, and paramiko only
works with RSA and DSA host keys. So you will need to comment the others
out. Edit the HostKeys section so that it looks like this:

```
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_dsa_key
#HostKey /etc/ssh/ssh_host_ecdsa_key
#HostKey /etc/ssh/ssh_host_ed25519_key
```

The `keeper` user has elevated privileges, so nobody should be able to SSH to
the server as that user. Add this line to the file to prevent this:
 
```
DenyUsers keeper
```

Now restart the SSH server:

```
systemctl restart ssh.service
```

### Install Software

Install the following Debian packages:

```
apt-get install python3 python3-pip libffi-dev libssl-dev sudo
```

Install git-keeper:

```
pip3 install git-keeper
```

### Configure `sudo`

The `keeper` user needs to be able to run a number of commands as root. Create
a `sudo` configuration for `keeper` by running this command:

```
visudo -f /etc/sudoers.d/keeper
```

Add the following lines to the configuration:

```
keeper ALL = (root) NOPASSWD: /usr/sbin/useradd
keeper ALL = (root) NOPASSWD: /usr/sbin/usermod
keeper ALL = (root) NOPASSWD: /usr/sbin/chpasswd
keeper ALL = (root) NOPASSWD: /usr/sbin/groupadd
keeper ALL = (root) NOPASSWD: /bin/chown
keeper ALL = (root) NOPASSWD: /bin/chmod
```
