# Admin Users

This page contains a guide for setting up a server to run git-keeper. For more
details about the different server configuration options see
[Server Configuration](reference.md#server-configuration).

## Server Setup

This guide assumes you are starting with an Ubuntu Server minimal
installation. git-keeper should work with any Linux distribution, but the setup
details might be slightly different.

### Quick Start

Here is an overview of the steps necessary to get a git-keeper server up and
running. Follow these if you have done it before and just need a
refresher. Skip to the next section for more detailed instructions.

These instructions assume you have a dedicated server with an Ubuntu Server
installed and a working SSH server.

* Create the `keeper` user, which must be in the `keeper` group
* Add a line to `/etc/ssh/sshd_config` to disallow the user `keeper` to log in via SSH: `DenyUsers keeper`
* Install `sudo`, `python3`, `git`, `firejail` (optional), and `docker`
  (optional)
* Install `git-keeper-server` with `pip`
* Configure `sudo` so that `keeper` can run any command without a password
* Create `server.cfg`
* Create a user systemd service to automatically start gkeepd
* Add faculty users

### Requirements

git-keeper requires a server running a Linux operating system which is
dedicated to running git-keeper. The server must allow incoming SSH traffic 
and it must have access to an SMTP server. 

The guide assumes you have installed the Ubuntu Server minimal installation and
that you have enabled the SSH server and selected `docker` to install during
installation.

Other Linux distributions will work as well but some of the following steps may
be a little different.

### Create the Keeper User

The `keeper` user is the user that will run the git-keeper server
process. **This user will have root privileges.** 

Create the user. Be sure to choose a strong password:
 
```no-highlight
adduser keeper
```

Ensure that `keeper` is also in the group `keeper`. This command shows the
groups that `keeper` is in:

```no-highlight
groups keeper
```

### Configure SSH

The `keeper` user has elevated privileges, so nobody should be able to SSH to
the server as that user. Add the line below to `/etc/ssh/sshd_config` to
prevent this. If you are only able to access your server via SSH, be sure you
have another less privileged user you can still use to SSH in.
 
```no-highlight
DenyUsers keeper
```

Now restart the SSH server:

```no-highlight
systemctl restart ssh.service
```

### Install Dependencies

The required dependencies are `sudo`, `git`, and `python3` >= 3.8 with
`pip`. Installing `firejail` is highly recommended for test
sandboxing. Installing `docker` allows for even more flexible sandboxing.

The Ubuntu Server minimal install comes with `sudo` and `python3`, and
installing `docker` can be done during the setup process. That leaves the
following to install:

```no-highlight
sudo apt install git python3-pip firejail
```

### Configure `sudo`

The `keeper` user needs to be able to run a number of commands as root and
the tester user. To allow this, create a `sudo` configuration for `keeper`:

```no-highlight
sudo visudo -f /etc/sudoers.d/keeper
```

Add the following line to the configuration:

```no-highlight
keeper ALL = (ALL) NOPASSWD: ALL
```

### Install the Server Package

The git-keeper server can be installed using `pip` like so:

```no-highlight
sudo python3 -m pip install git-keeper-server
```

### Create `server.cfg`

There must be a file named `server.cfg` in the `keeper` user's home
directory. This is the configuration file for the server. See below for a
template `server.cfg`, or see the
[Server Configuration](reference.md#server-configuration) reference for more
detailed descriptions of each section and field.

#### Template `server.cfg`

Here is a template `server.cfg`. Required parameters must be defined, optional
parameters are commented out with their default values, if they exist.

```
[server]
hostname = 

[email]
from_name = 
from_address = 
smtp_server = 
smtp_port = 
#use_tls = true
#email_username = 
#email_password = 
#email_interval = 2
#use_html = true

[admin]
admin_email = 
admin_first_name = 
admin_last_name = 

#[gkeepd]
#test_thread_count = 1
#tests_timeout = 300
#tests_memory_limit = 1024
#default_test_env = firejail
```

### Using a `systemd` service

You can run `gkeepd` in a `screen` or `tmux` session but it is recommended that
you run `gkeepd` as a `systemd` service so that it automatically starts on
boot.

#### Creating the Service

Create the file `/etc/systemd/system/gkeepd.service` with the
following contents:

```
[Unit]
Description=git-keeper server

[Service]
Type=simple
User=keeper
Group=keeper
ExecStart=/usr/local/bin/gkeepd

[Install]
WantedBy=default.target
```

This assumes that `gkeepd` was installed at `/usr/local/bin/gkeepd`. Type
`which gkeepd` to see where the executable is on your system and adjust the
path if necessary.


#### Enabling and Starting the Service

Enable:

```no-highlight
sudo systemctl enable gkeepd
```

Start:

```no-highlight
sudo systemctl start gkeepd
```

Check that it is running:

```no-highlight
sudo systemctl status gkeepd
```

You can also look at `~keeper/gkeepd.log` to check on the status of the daemon.

### Adding Faculty Members

Once the server is running, the admin user can use the
[client](faculty-users.md#client-setup) to add additional faculty members with
[`gkeep add_faculty`](reference.md#add_faculty) like so:

```no-highlight
gkeep add_faculty <last name> <first name> <email address>
```
