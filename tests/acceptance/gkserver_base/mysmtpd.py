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
import os
import smtpd
import sys
import asyncore
import email
from email.header import decode_header


########################################################################
#
#
# IF YOU CHANGE THIS FILE, YOU HAVE TO REBUILD THE DOCKER CONTAINER
# THE CURRENT manual_run.py will not detect changes
#
#
########################################################################


class MySMTPD(smtpd.DebuggingServer):
    """
    A mock email server to trap email in files.  Each email is saved to
    a file with the username and an integer (starting at 1), e.g.:

    colemanb_1.txt

    """

    def __init__(self, port, directory):
        """
        Initialize the mock server.

        :param port: the port to listen on
        :param directory: the directory to save files
        :return: None
        """

        smtpd.DebuggingServer.__init__(self, ('localhost', port), None)
        self.directory = directory

        self.users = {}

    def process_message(self, peer, mailfrom, rcpttos, data):
        """
        Process one message (save it to the appropriate file

        :param peer: the name of the sending server, string
        :param mailfrom: the from field, string
        :param rcpttos: the recipient(s), a list of string
        :param data: the message
        :return: None
        """

        # we only send to 1 user at a time, so this should be safe
        # take only the username so we don't have a @ in the filename
        user = rcpttos[0].split("@")[0]

        if user not in self.users:
            self.users[user] = 1

        filename = '{}_{:0>3}.txt'.format(user, self.users[user])

        self.users[user] += 1

        with open(os.path.join(self.directory, filename), 'w') as f:

            msg = email.message_from_string(data)

            f.write('From: ' + mailfrom + '\n')
            # The subject line is encoded. Read the docs for email.header
            # to understand the double [0]
            f.write('Subject: ' + decode_header(msg['Subject'])[0][0].decode() +
                    '\n\n')

            if msg.is_multipart():
                for payload in msg.get_payload():
                    f.write(payload.get_payload(decode=True).decode('utf-8'))
            else:
                f.write(msg.get_payload(decode=True).decode('utf-8'))


def main():

    if len(sys.argv) != 3:
        print("provide port and directory")
        return

    MySMTPD(int(sys.argv[1]), sys.argv[2])

    asyncore.loop()

main()