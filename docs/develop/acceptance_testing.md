
## Overview

Our acceptance tests use two virtual machines:

* `gkserver` - a server to run `gkeepd`. 
* `gkclient` - a machine where faculty and student actions can be executed.

We use Vangrant(https://www.vagrantup.com/) (backed by VirtualBox) to launch the machines and [Robot Framework](https://robotframework.org/) to write the tests.

The `git-keeper-robot` package contains a library of functions to control the VMs and to implement "verbs" for Robot Framework.

The `gkserver` machine has all the dependencies installed, and.  When you run `vagrant up`, Vagrant will mount `git-keeper-core` and `git-keeper-server` on within `gkserver` and then `pip install -e` both packages.  Note that this means that any changes you make to the code will be used within the VM even after this step completes.

Similarly, `vagrant up` will install `git-keeper-core` and `git-keeper-client` on the `gkclient` VM, making local changes usable within the VM.

The `gkserver` VM contains a mock email server that saves files to `/email` instead of actually sending email messages.

## Setup

Before you can run the test, you must build the VirtualBox images:

* Goto `tests/acceptance/gkserver_base` and run `make_box.sh`.  This will create an image with the basic setup steps complete.  See the `Vagrantfile` in this directory for the steps.
* Run `vagrant box add --name gkserver gkserver.box`.  This will allow Vagrant to launch the `gkserver` image.  See `tests/acceptance/Vagrantfile`.
* Goto `tests/acceptance/gkclient_base` and run `make_box.sh`.  This will install the necessary software to run `gkeep`, and it will create a use named `keeper` (password `keeper`) that has `sudo` rights.
* Run `vagrant box add --name gkclient gkclient.box`.  This will allow Vagrant to launch the `gkclient` image.  See `tests/acceptance/Vagrantfile`.

## Running the VMs


* Launch both VMs by running `vangrant up` in `/tests/acceptance`.  This will use `tests/acceptance/Vagrantfile` to launch both VMs and install the `git-keeper` code.
* Destroy both VMs by running `vagrant destroy -f`


## Running Robot Framework Tests

Once you have built `gkserver` and `gkclient`, you can run the tests.  Run `robot .` to tell Robot Framework to run all tests in the current directory.

When you run tests, Robot Framework has two behaviors:

* If `gkserver` and `gkclient` are already up, it will use these machines for testing - and then leave them running when done.  This saves time when you have to run tests multiple times.
* If `gkserver` and `gkclient` are not running, it will lauch both machines for testing - and then destroy them when done.

In order to avoid side effects, Robot Framework will reset `gkserver` and `gkclient` before each test.  See `vmscripts/reset_server.py` and `vmscripts/reset_client.py` to see what is reset.

### Run Subset of Tests

We use a `__init__.robot` file to setup the VMs, and so you have to be careful when you want to run a subset of tests.  In the following commands, note the period at the end of the commands.  This tells Robot Framework to  look in the current directory when it runs tests, and this causes it to find the `__init__.robot` file.

* To run one test, use `robot -t "<test_name>" .` - For example, `robot -t "Valid Class" .`. 
* To run one suite (file) of tests, use `robot -s "file_name> .` - For example, `robot -s gkeepd_launch .`

## Manual Execution

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


## Notes

* This testing system is finicky!  If you suddently get errors, try `vagrant destroy -f` and `vagrant up` first.
* Once you get `gkserver.box` and `gkclient.box` built and added to Vagrant, you should not need to do this step again.
* If you get an error message, "The IP address configured for the host-only network is not within the allowed ranges. Please update the address used to be within the allowed ranges and run the command again" - add the line `* 20.0.0.0/8 192.168.0.0/16` (the asterisk matters!) to `/etc/vbox/networks.conf`.  Make sure this file is world readable.  See [this StackOverFlow Question](https://stackoverflow.com/questions/70704093/the-ip-address-configured-for-the-host-only-network-is-not-within-the-allowed-ra)
* The `tests/acceptance/vm_scripts` folder must be world readable for the tests to execute.  One one system the `umask` was set to 0077, and so all files had no group permissions allowed.  This caused the `reset_server.py` script to fail during `manual_configure.py`.  Run `umask 0022`, re-clone the repo, recreate the virtual enviroment, and then run the tests again.
* Robot Framework masks many error messages.  If tests are failing in weird ways, run `manual_configure.py`. If this succeeds, go into `gkserver` and/or `gkclient` and run your sequence of steps manually.

