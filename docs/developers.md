# Developers

This page has information for those who would like to contribute to the
development of git-keeper.

## Project Organization

There are 3 distributions in this project:

* `git-keeper-client`
* `git-keeper-core`
* `git-keeper-server`

Both `git-keeper-client` and `git-keeper-server` depend on `git-keeper-core`.

## Developer Setup

The preferred development environment is PyCharm on OSX or Linux.  The following steps will ensure that your development environment is isolated from the system Python and other Python projects.

### Prerequisites

* [Python 3.8 or greater](https://www.python.org/downloads/)

### Setup Process


* Fork the `git-keeper/git-keeper` repo to your personal GitHub account.
* Clone the repo from your GitHub account
* `cd git-keeper`
* Create a virtual environment named `.env`.  The `.gitignore` file ensures that the `.env` folder is ignored.

```no-highlight
python3 -m venv .env
```
 
* Activate the virtual environment.

```no-highlight
source .env/bin/activate
```
 
* Install the `mkdocs` dependencies:

```no-highlight
pip install -r requirements.txt
```
 
* Install the project modules `git-keeper-core`, `git-keeper-client`,
  `git-keeper-server`, and `git-keeper-robot` as editable.  This will allow the
  IDE to recognize the `git-keeper` modules.

```no-highlight
pip install -e git-keeper-core
pip install -e git-keeper-client
pip install -e git-keeper-server
pip install -e git-keeper-robot
```

* Open the project in PyCharm, and wait for it to index the packages.

If you clone the repo from within PyCharm, you will have to change the project interpreter after you create the virtual environment.  Also, if you have the project open in PyCharm when you install the `git-keeper` modules, you will have to restart PyCharm before it will recognize the names (this is a known bug in PyCharm).


## Style

We strive for consistent style within this project. Contributions may not be
accepted if they do not follow these guidelines.

* Project filenames
    * Most filenames should be all lowercase with words separated by
    underscores
    * Use all uppercase for files like `README.md` and `COPYING`
* Documentation
    * Place documentation in the `docs` directory. If you add a new file, add
    it to the table of contents in `mkdocs.yml`.
    * Use markdown
    * Limit lines of text to 80 characters
* Python
    * Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) whenever
    possible
    * Variable names
        * Avoid abbreviations unless the meaning remains clear or length gets
        way out of hand
            * `cls` is not ok for class
            * `config` is ok for configuration
        * Quantities
            * Use `item_count` vs `num_items`
        * Dictionaries
            * Use `<value>s_by_<key>` (i.e. `students_by_class`)
        * Indexes
            * For an index into a single list, use `i`
            * For nested loops and other situations with multiple indexes, use a
            variable name ending in `_i` (i.e. `student_i` and `class_i`)
        * Filenames, directory names, and full paths
            * File and directory basenames (no path)
                * End filename variable names with `_filename`
                * End directory name variable names with `_dir`
            * Full paths
                * End the variable name with `_path`. If it is ambiguous
                whether it is a file or directory, end it with `_file_path` or
                `_dir_path`
    * Type hinting
        * Use type hints for all parameters that are object references
    * Importing
        * Either import an entire module (`import os`) or import specific
        items (`from queue import Queue, Empty`) but do not import all items
        from a module (do not say `from os import *`)
        * Import system-level items first followed by imports that are
        internal to the project

## Acceptance Testing

Most of git-keeper's features are tested using our acceptance testing suite
which resides in `tests/acceptance`. New tests should be added when adding new
features, and the tests should pass before new changes are merged.

### Overview

Our acceptance tests use two virtual machines:

* `gkserver` - a server to run `gkeepd`. 
* `gkclient` - a machine where faculty and student actions can be executed.

We use Vangrant(https://www.vagrantup.com/) (backed by VirtualBox) to launch the machines and [Robot Framework](https://robotframework.org/) to write the tests.

The `git-keeper-robot` package contains a library of functions to control the VMs and to implement "verbs" for Robot Framework.

The `gkserver` machine has all the dependencies installed, and.  When you run `vagrant up`, Vagrant will mount `git-keeper-core` and `git-keeper-server` on within `gkserver` and then `pip install -e` both packages.  Note that this means that any changes you make to the code will be used within the VM even after this step completes.

Similarly, `vagrant up` will install `git-keeper-core` and `git-keeper-client` on the `gkclient` VM, making local changes usable within the VM.

The `gkserver` VM contains a mock email server that saves files to `/email` instead of actually sending email messages.

### Setup

Before you can run the test, you must build the VirtualBox images:

* Goto `tests/acceptance/gkserver_base` and run `make_box.sh`.  This will create an image with the basic setup steps complete.  See the `Vagrantfile` in this directory for the steps.
* Run `vagrant box add --name gkserver gkserver.box`.  This will allow Vagrant to launch the `gkserver` image.  See `tests/acceptance/Vagrantfile`.
* Goto `tests/acceptance/gkclient_base` and run `make_box.sh`.  This will install the necessary software to run `gkeep`, and it will create a use named `keeper` (password `keeper`) that has `sudo` rights.
* Run `vagrant box add --name gkclient gkclient.box`.  This will allow Vagrant to launch the `gkclient` image.  See `tests/acceptance/Vagrantfile`.

### Running the VMs


* Launch both VMs by running `vangrant up` in `/tests/acceptance`.  This will use `tests/acceptance/Vagrantfile` to launch both VMs and install the `git-keeper` code.
* Destroy both VMs by running `vagrant destroy -f`


### Running Robot Framework Tests

Once you have built `gkserver` and `gkclient`, you can run the tests.  Run `robot .` to tell Robot Framework to run all tests in the current directory.

When you run tests, Robot Framework has two behaviors:

* If `gkserver` and `gkclient` are already up, it will use these machines for testing - and then leave them running when done.  This saves time when you have to run tests multiple times.
* If `gkserver` and `gkclient` are not running, it will lauch both machines for testing - and then destroy them when done.

In order to avoid side effects, Robot Framework will reset `gkserver` and `gkclient` before each test.  See `vmscripts/reset_server.py` and `vmscripts/reset_client.py` to see what is reset.

#### Run Subset of Tests

We use a `__init__.robot` file to setup the VMs, and so you have to be careful when you want to run a subset of tests.  In the following commands, note the period at the end of the commands.  This tells Robot Framework to  look in the current directory when it runs tests, and this causes it to find the `__init__.robot` file.

* To run one test, use `robot -t "<test_name>" .` - For example, `robot -t "Valid Class" .`. 
* To run one suite (file) of tests, use `robot -s <suite_name> .` - For example, `robot -s gkeepd_launch .` to run all the tests in the `gkeepd_launch.robot` file.

### Manual Execution

You can also use `gkserver` and `gkclient` to do manually testing.  

If you want a "clean" system where you can configure and run `gkeepd`:

* Run `vagrant up` in `tests/acceptance` to launch both VMs.
* Run `vagrant ssh gkserver` to connect to the server
* On the server, run `su - keeper` to become the keeper account.  The password is "keeper"
* You can also connect to `gkclient`, where there is also a `keeper` account (password is "keeper").

For convienence, the script `manual_configure.py` will:

* Create a valid `server.cfg`
* Create an `admin_prof` account on `gkclient` and make that account the admin of `git-keeper`
* Create a `prof1` account on `gkclient` and make it a non-admin faculty member of `git-keeper`
* Create a course named `cs1` for `prof1` that contains students `student1` and `student2`. 
* Create accounts for `student1` and `student2`
* Have `prof1` upload and publish a simple assignment
* Have `student1` clone and submit the assignment
* Have `prof1` fetch the submissions.

To reset the system, run `manual_reset.py`.  This will:

* [Server]: Stop `gkeepd`
* [Server]: Remove all `git-keeper` files
* [Server]: Delete all email files in `/email`
* [Server]: Remove all users except `keeper` and `vagrant`
* [Client]: Remove all users exept `keeper`


### Notes

* This testing system is finicky!  If you suddently get errors, try `vagrant destroy -f` and `vagrant up` first.
* Once you get `gkserver.box` and `gkclient.box` built and added to Vagrant, you should not need to do this step again.
* If you get an error message, "The IP address configured for the host-only network is not within the allowed ranges. Please update the address used to be within the allowed ranges and run the command again" - add the line `* 20.0.0.0/8 192.168.0.0/16` (the asterisk matters!) to `/etc/vbox/networks.conf`.  Make sure this file is world readable.  See [this StackOverFlow Question](https://stackoverflow.com/questions/70704093/the-ip-address-configured-for-the-host-only-network-is-not-within-the-allowed-ra)
* The `tests/acceptance/vm_scripts` folder must be world readable for the tests to execute.  One one system the `umask` was set to 0077, and so all files had no group permissions allowed.  This caused the `reset_server.py` script to fail during `manual_configure.py`.  Run `umask 0022`, re-clone the repo, recreate the virtual enviroment, and then run the tests again.
* Robot Framework masks many error messages.  If tests are failing in weird ways, run `manual_configure.py`. If this succeeds, go into `gkserver` and/or `gkclient` and run your sequence of steps manually.

## Unit Testing

Unit tests for classes and functions reside in `tests/unit`. These tests can be
run by running `pytest` in the unit test directory.

To add tests for a new unit, create a new file in `tests/unit` that begins with
`test_`. Within the test file, each function that begins with `test_` is
considered a test. See the [pytest documentation](https://docs.pytest.org/) for
more information about writing tests for `pytest`.

## Release Checklist

To release version x.y.z of git-keeper, follow the steps below.

### GitHub

* Update the `VERSION` file with the new version number.
* Run `bump_version.py` to propagate the new version number to all
  packages
* Merge the newly versioned code with the `develop` branch via pull
  request
* Merge the `develop` branch with the `master` branch via pull request
* Create an annotated tag on the `master` branch like so:
  `git tag -a x.y.z -m "Version x.y.z"`
* Push the tag directly to the master branch with `git push --tags`
* Create a new release on GitHub from the new tag.

### PyPI

Follow the [official packaging documentation](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
to build and upload all 3 packages to PyPI.

## Server Filesystem Structure

Below is an example filesystem layout for a git-keeper server.

```no-highlight
/
└── home
    ├── faculty
    │   ├── faculty
    │   │   └── example_class
    │   │       └── hw01.git
    │   └── .gitkeeper
    │       ├── classes
    │       │   └── example_class
    │       │       └── hw01
    │       │           ├── base_code.git
    │       │           ├── email.txt
    │       │           ├── reports.git
    │       │           └── tests
    │       ├── faculty.log
    │       ├── gkeepd.log
    │       ├── info
    │       │   └── 1576784041.3908958.json
    │       └── uploads
    │           └── 1576784036.5428793
    │               └── students.csv
    ├── keeper
    │   ├── .gitconfig
    │   ├── gkeepd.lock
    │   ├── gkeepd.log
    │   ├── gkeepd_db.sqlite
    │   └── server.cfg
    ├── student
    │   ├── faculty
    │   │   └── example_class
    │   │       └── hw01.git
    │   ├── .gitkeeper
    │   │   └── student.log
    │   └── git-shell-commands
    │       └── passwd
    └── tester
```

## Log Events

Each faculty and student user has a file named `<username>.log` in the
`.gitkeeper` folder within their home directory on the server.  Requests to
`gkeepd` are made by appending events to these log files. Each line of the log
is an event, and is structured like this:

```no-highlight
<timestamp> <event type> <payload>
```

For example, if a student with the username `student` pushes to an assignment
repository, there is a git hook which appends an event of the following form to
`~student/.gitkeeper/student.log`:

```no-highlight
1463892789 SUBMISSION /home/student/faculty/class/assignment.git
```

Event types are used to determine what event handler should handle the
event. See `gkserver/event_handlers`. The `handler_registry.py` file in that
directory maps event types to handlers.

### Log Event Responses

Confirmations and error messages from `gkeepd` are also placed in log
files. Each faculty user has a file `.gitkeeper/gkeepd.log` for this purpose.

## Info JSON Structure

Many client operations fetch the contents of the latest info file from the
server in the `.gitkeeper/info` directory in the faculty's home directory. An
info file contains information about a faculty member's classes and
assignments. Here is the structure of an example info file:

```json
{
   "class_name":{
      "assignments":{
         "assignment_name":{
            "name":"assignment_name",
            "published":true,
            "reports_repo":{
               "hash":"202585432b8ff21ff4f93a886fff9b09c46eb18e",
               "path":"/home/faculty/classes/class_name/assignment_name/reports.git"
            },
            "students_repos":{
               "alovelace":{
                  "first":"Ada",
                  "hash":"76f608acf4d08ccd1bf07955e2600bdce3f80774",
                  "last":"Lovelace",
                  "path":"/home/alovelace/faculty/class_name/assignment_name.git",
                  "submission_count":0,
                  "time":1476986981
               }
            }
         }
      },
      "students":{
         "alovelace":{
            "email_address":"alovelace@example.edu",
            "first":"Ada",
            "home_dir":"/home/alovelace",
            "last":"Lovelace",
            "last_first_username":"lovelace_ada_alovelace",
            "username":"alovelace"
         }
      }
   }
}
```
