# Server Setup

This guide details how to set up a server to run git-keeper. The guide assumes
you are starting with a Debian Jessie minimal netinstall
installation. git-keeper should work with any Linux distribution, but the setup
details might be slightly different.

## Quick Start

Here is an overview of the steps necessary to get a git-keeper server up and
running. Follow these if you have done it before and just need a
refresher. Skip to the next section for more detailed instructions.

These instructions assume you have a dedicated server with a Debian
installation and a working SSH server.

* Create the following users:
    * `keeper`. Must be in the `keeper` group.
* Add a line to `/etc/ssh/sshd_config` to disallow the user `keeper` to log in via SSH: `DenyUsers keeper`
* Install `sudo`, `python3`, and `git`
* Clone the git-keeper repository and install both `git-keeper-core` and
`git-keeper-server`
* Configure `sudo` so that `keeper` can run any command without a password
* Create `server.cfg`
* Create a user systemd service to automatically start gkeepd
* Add faculty members

### Requirements

git-keeper requires a server running a Linux operating system which is
dedicated to running git-keeper. The server must allow incoming SSH traffic 
and it must have access to an SMTP server. 

The guide assumes you have installed Debian from the minimal network
installation media and that you have enabled the SSH server.

Other Linux distributions will work as well but some of the following steps may
be a little different.

### Create the Keeper User

The `keeper` user is the user that will run the git-keeper server
process. **This user will have root privileges.**

Create the user. Be sure to choose a strong password:
 
```
adduser keeper
```

Ensure that `keeper` is also in the group `keeper`. This command shows the
groups that `keeper` is in:

```
groups keeper
```

### Configure SSH

The `keeper` user has elevated privileges, so nobody should be able to SSH to
the server as that user. Add this line to `/etc/ssh/sshd_config` to prevent
this:
 
```
DenyUsers keeper
```

Now restart the SSH server:

```
systemctl restart ssh.service
```

### Install Dependencies

Install the following packages:

```
apt-get install python3 sudo git
```

### Configure `sudo`

The `keeper` user needs to be able to run a number of commands as root and
the tester user. To allow this, create a `sudo` configuration for `keeper`:

```
visudo -f /etc/sudoers.d/keeper
```

Add the following line to the configuration:

```
keeper ALL = (ALL) NOPASSWD: ALL
```

### Install the Server Package

The git-keeper server can be installed using `pip` like so:

```
sudo python3 -m pip install git-keeper-server
```

### Create `server.cfg`

There must be a file named `server.cfg` in the `keeper` user's home
directory. This is the configuration file for the server.

`server.cfg` has four sections: `[server]`, `[email]`, `[admin]`, and `[gkeepd]`.

#### `[server]`

The `[server]` section has a single required parameter `hostname`, which is the
hostname of the server. This will be used to build Git URLs.

#### `[email]`

The `[email]` section is also required. The following parameters are required:

```
from_name: <name that the emails will be from>
from_address: <email address that the emails come from>
smtp_server: <hostname of the SMTP server>
smtp_port: <SMTP server port>
```

The following parameters are optional:

```
use_tls: <true or false, defaults to true>
email_username: <username for the SMTP server>
email_password: <password for the SMTP server>
email_interval: <seconds to wait between sending emails>
use_html: <true or false, defaults to false>
```

If `use_html` is true, submission test results will be sent as an HTML email,
placing the contents within pre tags so that they appear in a fixed width font.

#### `[admin]`

The `[admin]` section is also required. The section defines an admin user. The admin user will automatically be added as a faculty user when the server first starts, and then the admin user will be able to add additional faculty members.

The following parameters are required:

```
admin_email: <email address of the admin user>
admin_first_name: <first name of the admin user>
admin_last_name: <last name of the admin user>
```

#### `[gkeepd]`

The `[gkeepd]` section is optional. Below are the allowed parameters and their
defaults:

```
keeper_user: keeper
keeper_group: keeper
tester_user: tester
faculty_group: faculty
student_group: student
tests_timeout: 300
tests_memory_limit: 1024
```

The `tests_timeout` parameter specifies a global timeout for tests in case an assignment's tests fail to properly account for infinite loops. The default is 300 seconds. If this timeout occurs the student and faculty member will be notified that there was an error in the tests, so one should not depend on this timeout to cleanly catch infinite loops.

Similar to `tests_timeout`, the `tests_memory_limit` sets a global memory limit for tests. The default limit is 1024 MB.

#### Template

Here is a template `server.cfg`. Required parameters must be defined, optional
parameters are commented out with their default values, if they exist.

```
[server]
hostname: 

[email]
from_name: 
from_address: 
smtp_server: 
smtp_port: 
#use_tls: true
#email_username: 
#email_password: 
#email_interval: 2

[admin]
admin_email: 
admin_first_name: 
admin_last_name: 

#[gkeepd]
#keeper_user: keeper
#keeper_group: keeper
#tester_user: tester
#faculty_group: faculty
#student_group: student
#tests_timeout: 300
#tests_memory_limit: 1024
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

```
systemctl enable gkeepd
```

Start:

```
systemctl start gkeepd
```

Check that it is running:

```
systemctl status gkeepd
```


You can also look at `~keeper/gkeepd.log` to check on the status of the daemon.

### Adding Faculty Members

Once the server is running, the admin user can use the [client](Client-setup) to add additional faculty members like so:

```
gkeep add_faculty <last name> <first name> <email address>
```