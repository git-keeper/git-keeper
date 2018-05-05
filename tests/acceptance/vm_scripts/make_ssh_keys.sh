#!/bin/bash

# Copyright 2018 Nathan Sommer and Ben Coleman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

sudo mkdir /home/$1/.ssh
sudo chown $1 /home/$1/.ssh
sudo chgrp $1 /home/$1/.ssh
sudo -u $1 ssh-keygen -t rsa -N "" -f /home/$1/.ssh/id_rsa
sudo cp /home/$1/.ssh/id_rsa.pub /vagrant/$2/$1_rsa.pub
sudo cp /home/$1/.ssh/id_rsa /vagrant/$2/$1_rsa
sudo cp /home/$1/.ssh/id_rsa.pub /home/$1/.ssh/authorized_keys
sudo sh -c "echo 'Host gkserver' >> /home/$1/.ssh/config"
sudo sh -c "echo 'StrictHostKeyChecking no' >> /home/$1/.ssh/config"
sudo sh -c "echo 'UserKnownHostsFile /dev/null' >> /home/$1/.ssh/config"
sudo sh -c "echo 'LogLevel=ERROR' >> /home/$1/.ssh/config"
sudo chown -R $1 /home/$1/.ssh/
sudo chgrp -R $1 /home/$1/.ssh/
sudo chmod 600 /home/$1/.ssh/*
