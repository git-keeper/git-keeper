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
Provides an Email class for storing and sending emails.

Supports file attachments and truncating long messages.

Emails should not be sent directly, but rather enqueued in the global
EmailSenderThread which provides rate limiting.

"""
import html
import os
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import IntEnum
from smtplib import SMTP

from gkeepcore.gkeep_exception import GkeepException
from gkeepserver.server_configuration import config


class EmailException(GkeepException):
    """Raised if anything goes wrong building or sending emails."""
    pass


class EmailPriority(IntEnum):
    """
    Enum used to specify an email's priority level for use by the priority
    queue in the email sending thread.
    """
    LOW = 2
    NORMAL = 1
    HIGH = 0


class Email:
    """
    Builds an email that can be sent using smtplib and provides a method
    to send the email.
    """
    def __init__(self, to_address, subject, body, files_to_attach=None,
                 max_character_count=1000000, priority=EmailPriority.NORMAL,
                 html_pre_body=False):
        """
        Construct an email object.

        The body may be a single string or a list of strings. If the body is a
        list of strings, the final email message body will be each of those
        strings joined together by newlines.

        :param to_address: the email address to send the email to
        :param subject: the subject of the email
        :param body: the body of the email as a string or list of strings
        :param files_to_attach: a list of file paths to attach to the email
        :param max_character_count: if the email is longer than this number of
         characters it will be truncated
        :param priority: an EmailPriority representing the email's priority
         in the send queue
        :param html_pre_body: if True, the body of the email will be sent both
         as plain text and HTML, and for the latter the code will be escaped
         and wrapped in <pre></pre> tags
        """

        self._send_attempts = 0
        self._max_send_attempts = 10
        self.last_send_error = ''

        self.to_address = to_address

        self._subject = subject
        self._files_to_attach = files_to_attach

        self.priority = priority

        # regardless of how the body is passed in, represent it by a list of
        # lines that have trailing whitespace removed
        if isinstance(body, list):
            body_lines = []

            for line in body:
                if not isinstance(line, str):
                    raise EmailException('Email body lines must be strings')

                body_lines.append(line.rstrip())
        elif isinstance(body, str):
            body_lines = [line.rstrip() for line in body.split('\n')]
        else:
            error = 'Email body must be a string or a list of strings'
            raise EmailException(error)

        # the final message body needs to have \r\n newlines
        self._body = '\r\n'.join(body_lines)

        # truncate the email with a message if need be
        if len(self._body) > max_character_count:
            self._body = self._body[:max_character_count].rstrip()
            self._body += '\r\n\r\n'

            self._body += ('ATTENTION: This email was truncated due to its '
                           'long length. If important information seems '
                           'missing, contact your instructor.\r\n')

        self._build_mime_message(files_to_attach, html_pre_body)

    def __repr__(self):
        repr_string = 'To: {0}, Subject: {1}'.format(self.to_address,
                                                     self._subject)
        return repr_string

    def __lt__(self, other):
        # Provide < comparison for use by the PriorityQueue
        return self.priority < other.priority

    def _build_mime_message(self, files_to_attach, html_pre_body):
        # Create the final message by building up a MIMEMultipart object and
        # then storing the final message as a string in _message_string

        # encode headers
        from_header = Header('{0}'.format(config.from_name), 'utf-8')
        to_header = Header('{0}'.format(self.to_address), 'utf-8')
        subject_header = Header('{0}'.format(self._subject), 'utf-8')
        reply_to_header = Header('{0}'.format(config.from_address), 'utf-8')

        if html_pre_body:
            message = MIMEMultipart('alternative')
        else:
            message = MIMEMultipart()

        # put the headers in the message
        message['Subject'] = subject_header
        message['From'] = from_header
        message['To'] = to_header
        message['reply-to'] = reply_to_header

        # attach the body
        if html_pre_body:
            template = '<html><head></head><body><pre>{}</pre></body></html>'
            html_body = template.format(html.escape(self._body))
            message.attach(MIMEText(self._body, 'plain', _charset='utf-8'))
            message.attach(MIMEText(html_body, 'html', _charset='utf-8'))
        else:
            message.attach(MIMEText(self._body, _charset='utf-8'))

        # attach any files
        for file_path in files_to_attach or []:
            if not os.path.isfile(file_path):
                raise EmailException('{0} is not a file'.format(file_path))

            filename = os.path.basename(file_path)
            content_disposition = 'attachment; filename="{0}"'.format(filename)

            try:
                with open(file_path, 'rb') as f:
                    message.attach(MIMEApplication(
                        f.read(),
                        Content_Disposition=content_disposition,
                        Name=filename
                    ))
            except OSError as e:
                raise EmailException('Error reading {0}: {1}'.format(file_path,
                                                                     e))
        # the final message is stored as a single string
        self.message_string = message.as_string()

    def max_send_attempts_reached(self) -> bool:
        """
        Determine whether or not we've already tried to send this email the
        maximum number of times.

        :return: True if we have reached the send attempt limit, False
         otherwise
        """

        return self._send_attempts >= self._max_send_attempts

    def send(self):
        """
        Send the email right now.

        Use the global EmailSenderThread to send emails with rate limiting
        rather than calling send() yourself.

        Uses the global ServerConfiguration object to obtain SMTP server
        information.

        """

        self._send_attempts += 1

        server = SMTP(config.smtp_server, config.smtp_port)
        server.ehlo()

        if config.use_tls:
            server.starttls()

        if config.email_username and config.email_password:
            server.login(config.email_username, config.email_password)

        server.sendmail(config.from_address, self.to_address,
                        self.message_string)
        server.quit()
