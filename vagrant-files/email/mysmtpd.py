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
import email
import logging
import signal

from email.header import decode_header


logger = logging.getLogger('my_smtp')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/email/mail.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


class MySMTPD(smtpd.DebuggingServer):
    """
    A mock email server to trap email in files.  Each email is saved to
    a file with the username and an integer (starting at 1), e.g.:

    colemanb1.txt

    """

    def __init__(self, port, directory):
        """
        Initialize the mock server.

        :param port: the port to listen on
        :param directory: the directory to save files
        :return: None
        """

        logger.info('Initializing server')

        if sys.version_info[1] == 6:
            smtpd.DebuggingServer.__init__(self, ('localhost', port), None, decode_data=True)
        else:
            smtpd.DebuggingServer.__init__(self, ('localhost', port), None)
        self.directory = directory

        self.users = {}

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        """
        Process one message (save it to the appropriate file

        :param peer: the name of the sending server, string
        :param mailfrom: the from field, string
        :param rcpttos: the recipient(s), a list of string
        :param data: the message
        :return: None
        """

        logger.info('Processing message from {0} to {1}'.format(mailfrom, rcpttos))
        # we only send to 1 user at a time, so this should be safe
        # take only the username so we don't have a @ in the filename
        user = rcpttos[0].split("@")[0]

        if user not in self.users:
            self.users[user] = 1

        filename = user + str(self.users[user])

        self.users[user] += 1

        with open(self.directory + '/' + filename + '.txt', 'w') as f:

            logger.info('Processing message')

            msg = email.message_from_string(data)

            logger.info('Writing from to file')

            f.write('From: ' + mailfrom + '\n')
            # The subject line is encoded. Read the docs for email.header
            # to understand the double [0]

            logger.info('Writing subject to file')

            f.write(msg['Subject'] + '\n\n')
            #f.write('Subject: ' + decode_header(msg['Subject'][0][0]) + '\n\n')
            #[0][0].decode() +
            #        '\n\n')

            logger.info('Writing body to file')

            if msg.is_multipart():
                for payload in msg.get_payload():
                    f.write(payload.get_payload(decode=True).decode('utf-8'))
            else:
                f.write(msg.get_payload(decode=True).decode('utf-8'))

            logger.info('Done processing email')


def establish_signals():
    """
    Create signal handlers for all signals - all handlers simply exit.
    :return: None 
    """
    def signal_handler(signum, frame):
        sys.exit(0)

    signals = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)

    for sig in signals:
        signal.signal(sig, signal_handler)


def main():

    if len(sys.argv) != 3:
        print("provide port and directory")
        return

    establish_signals()

    MySMTPD(int(sys.argv[1]), sys.argv[2])
    asyncore.loop()


main()
