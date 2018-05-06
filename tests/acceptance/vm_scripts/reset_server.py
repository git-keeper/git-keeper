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


from gkeepcore.shell_command import run_command, CommandError
import os


def server_running():
    try:
        run_command('screen -S gkserver -Q select .')
        return True
    except CommandError:
        return False


def stop_gkeepd():
    if server_running():
        run_command('screen -S gkserver -X quit')


def remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def remove_gkeepd_files():
    # remove gkeepd.log, snapshot.json, server.cfg, and faculty.csv
    remove('gkeepd.log')
    remove('snapshot.json')
    remove('server.cfg')
    remove('faculty.json')


def delete_email():
    # delete all files except mysmtpd.py
    run_command('sudo find /email ! -name "mysmtpd.py" '
                '-type f -exec rm -f {} +')


def remove_users():
    # remove everyone but vagrant, ubuntu, and keeper
    expected = ['keeper', 'vagrant', 'ubuntu']

    for user in os.listdir('/home'):
        if user not in expected:
            run_command('sudo userdel -r {}'.format(user))


stop_gkeepd()
remove_gkeepd_files()
delete_email()
remove_users()
