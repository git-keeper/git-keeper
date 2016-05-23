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


"""
Provides a global interface for sending emails in a rate-limited fashion.

The email sender runs in a separate thread so that other threads do not need
to block when trying to send email due to rate limiting.

This module stores an EmailSenderThread instance in the module-level variable
named email_sender. Call start() on this instance to start the thread.

Example usage:

    from gkeepserver.server_configuration import config
    from gkeepserver.email_sender_thread import email_sender
    from gkeepserver.email import Email

    def main():
        config.parse()
        email_sender.start()

        email = Email('guy@domain.com', 'sup guy', 'Hi, guy!')
        email_sender.enqueue(email)

        email_sender.shutdown()
        email_sender.join()

"""


from threading import Thread
from queue import Queue, Empty
from time import time, sleep

from gkeepserver.email import Email, EmailException


class EmailSenderThread(Thread):
    """
    Provides a Thread which blocks waiting for new emails and sends them in a
    rate-limited fashion.

    Usage:

    Call the inherited start() method to start the thread.

    Shutdown the thread by calling shutdown(). The sender will keep sending
    emails until the queue is empty, and then shut down.

    Add emails to the thread by calling enqueue(email). Emails must be
    gkeepserver.email.Email objects.

    """
    def __init__(self, min_send_interval=2):
        """
        Construct the object.

        Constructing the object does not start the thread. Call start() to
        actually start the thread.

        :param min_send_interval: number of seconds between calling send() on
         each email
        """

        Thread.__init__(self)

        self._email_queue = Queue()

        self._min_send_interval = min_send_interval
        self._last_send_time = 0

        self._shutdown_flag = False

    def enqueue(self, email: Email):
        """
        Add a new email to the queue.

        Sending is rate-limited so the email will not be sent immediately.

        :param email: the email to send
        """

        self._email_queue.put(email)

    def shutdown(self):
        """
        Shutdown the thread once the queue is empty.

        It may take some time for all the emails in the queue to be sent. join()
        on this thread after calling shutdown() to make sure it has actually
        shut down.
        """

        self._shutdown_flag = True

    def run(self):
        """
        Send emails as they arrive in the queue.

        This method should not be called directly. Call the start() method
        instead.

        Sends at most 1 email every _min_send_interval seconds.

        Loops until someone calls shutdown().
        """

        while not self._shutdown_flag:
            try:
                while True:
                    email = self._email_queue.get(block=True, timeout=0.5)

                    if isinstance(email, Email):
                        self._send_email_with_rate_limiting(email)
                    else:
                        # FIXME - log this
                        pass
            except Empty:
                pass

    def _send_email_with_rate_limiting(self, email: Email):
        # Send the email. Sleep first if need be.
        #
        # :param email: the email to send

        # if _min_send_interval seconds have not elapsed since the last email
        # was sent, sleep until _min_send_interval seconds have elapsed
        current_time = time()
        if current_time - self._last_send_time < self._min_send_interval:
            elapsed_time = current_time - self._last_send_time
            sleep_time = self._min_send_interval - elapsed_time
            sleep(sleep_time)

        self._last_send_time = current_time

        try:
            email.send()
            # FIXME - log this instead
            print('EMAILER: Sent email to', email.to_address)
        except EmailException as e:
            # FIXME - log this instead
            print('EMAILER: Failed to send email to', email.to_address)
