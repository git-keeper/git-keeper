#!/usr/bin/python3

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

import smtpd
import sys
import asyncore


class MySMTPD(smtpd.DebuggingServer):

    def __init__(self, port, directory):

        smtpd.DebuggingServer.__init__(self, ('localhost', port), None)
        self.directory = directory
        self.msg_num = 1

    def process_message(self, peer, mailfrom, rcpttos, data):
        with open(self.directory + '/email' + str(self.msg_num) + '.txt', 'w') as f:
            f.write(data)
            self.msg_num += 1


def main():

    if len(sys.argv) != 3:
        print("provide port and directory")
        return

    MySMTPD(int(sys.argv[1]), sys.argv[2])

    asyncore.loop()

main()