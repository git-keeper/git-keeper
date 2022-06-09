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

from queue import PriorityQueue, Empty
from threading import Thread
from time import time, sleep

from gkeepserver.gkeepd_logger import gkeepd_logger as logger
from gkeepserver.server_configuration import config
from gkeepserver.server_email import Email


class EmailSenderThread(Thread):
    """
    Provides a Thread which blocks waiting for new emails and sends them in a
    rate-limited fashion.

    Usage:

    Call the inherited start() method to start the thread.

    Shutdown the thread by calling shutdown(). The sender will keep sending
    emails until the queue is empty, and then shut down. Call join() after
    shutdown() in the main thread to allow all the enqueued emails to be sent
    before proceeding.

    Add emails to the thread by calling enqueue(email). Emails must be
    gkeepserver.email.Email objects.

    """
    def __init__(self):
        """
        Construct the object.

        Constructing the object does not start the thread. Call start() to
        actually start the thread.
        """

        Thread.__init__(self)

        self._email_queue = PriorityQueue()

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
        Shutdown the thread.

        The run loop will not exit until all queued messages have been sent.

        This method blocks until the thread has died.
        """

        self._shutdown_flag = True
        self.join()

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
                    email = self._email_queue.get(block=True, timeout=0.1)

                    if not isinstance(email, Email):
                        warning = ('Item dequeued for emailing that is '
                                   'not an email: {0}'.format(email))
                        logger.log_warning(warning)
                    else:
                        self._send_email_with_rate_limiting(email)
            except Empty:
                pass
            except Exception as e:
                logger.log_error('Error in email sender thread: {0}'
                                 .format(e))

    def _send_email_with_rate_limiting(self, email: Email):
        # Send the email. Sleep first if need be.
        #
        # :param email: the email to send

        # if _min_send_interval seconds have not elapsed since the last email
        # was sent, sleep until _min_send_interval seconds have elapsed
        current_time = time()
        if current_time - self._last_send_time < config.email_interval:
            elapsed_time = current_time - self._last_send_time
            sleep_time = config.email_interval - elapsed_time
            sleep(sleep_time)

        self._last_send_time = current_time

        try:
            email.send()
            logger.log_info('Sent email: {0}'.format(email))
        except Exception as e:
            if not email.max_send_attempts_reached():
                logger.log_warning('Email sending failed, will retry')
                self._email_queue.put(email)
            else:
                error = ('Failed to send email ({0}) after several '
                         'attempts: {1}'.format(email, e))
                logger.log_error(error)


# module-level instance for global email sending
email_sender = EmailSenderThread()
