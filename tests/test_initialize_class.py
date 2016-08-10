# Copyright 2016 Nathan Sommer and Ben Coleman
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

from tempfile import TemporaryDirectory
import shutil
import tests.docker_api as docker_api
from datetime import datetime
import os

# Write it so that the system either brings the server up or resets it
# the home directory space.  We can remove a mount
#
# and then add a new one.  This 2nd part is tricky. See
# https://jpetazzo.github.io/2015/01/13/docker-mount-dynamic-volumes/


# bring up the server container
# - mount home to temp directory
# - copy keeper home files into /home/keeper (from source to temp folder)
# install gkeepd
# start gkeepd

temp_home = TemporaryDirectory()
temp_home_dir = temp_home.name

# copy the git-keeper configuration file
shutil.copytree('server_files/config', temp_home_dir + '/keeper/.config/grader')
# copy ssh keys and known_host file
shutil.copytree('server_files/ssh', temp_home_dir + '/keeper/.ssh')

dapi = docker_api.DockerAPI()

if dapi.is_running('git-keeper-server'):
    print('yes')
else:
    print('no')

print(temp_home_dir)

input("return")

# bring up the client container
# install gkeep

# call initialize class

# check that it worked (look in temp directory)
# - student directories made with proper permissions
# - faculty folder contains course with proper permissions
