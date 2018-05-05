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
sudo cp /vagrant/$2/$1_rsa.pub /home/$1/.ssh/authorized_keys
sudo chown -R $1 /home/$1/.ssh
sudo chgrp -R $1 /home/$1/.ssh
sudo chmod -R 600 /home/$1/.ssh/*
