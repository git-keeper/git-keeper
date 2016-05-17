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

import smtplib
import sys
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from queue import Queue, Empty
from time import sleep

from configuration import GraderConfiguration


class EmailException(Exception):
    pass


class Email:
    def __init__(self, to_address, subject, body, max_char_count=10000,
                 files_to_attach=None):
        self.to_address = to_address
        self.subject = subject
        self.files_to_attach = files_to_attach

        if isinstance(body, list):
            body_lines = body
        elif isinstance(body, str):
            body_lines = body.split('\n')
        else:
            error = 'Email body must be a string or a list of strings'
            raise EmailException(error)

        self.body_lines = []

        char_count = 0

        for i, line in enumerate(body_lines):
            if not isinstance(line, str):
                raise EmailException('Email body lines must be strings')

            char_count += len(line)

            if char_count <= max_char_count:
                self.body_lines.append(line)
            else:
                break

        if len(self.body_lines) < len(body_lines):
            self.body_lines.extend(['', '...', ''])
            warning_lines = [
                'WARNING!! This email was truncated due to length.',
                'If it appears that important information is missing,',
                'please contact your instructor.',
                ''
            ]
            self.body_lines = warning_lines + self.body_lines


class EmailSender:
    def __init__(self, class_name, config: GraderConfiguration):
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.from_name = config.from_name
        self.from_address = config.from_address
        self.class_name = class_name
        self.username = config.email_username
        self.password = config.email_password

    def send_email(self, email: Email):
        user, domain = self.from_address.split('@')
        reply_to_address = '{0}+{1}@{2}'.format(user, self.class_name, domain)

        subject = '[{0}] {1}'.format(self.class_name, email.subject)

        from_header = Header('{0}'.format(self.from_name), 'utf-8')
        to_header = Header('{0}'.format(email.to_address), 'utf-8')
        subject_header = Header('{0}'.format(subject), 'utf-8')
        reply_to_header = Header('{0}'.format(reply_to_address), 'utf-8')

        message = MIMEMultipart()

        message['Subject'] = subject_header
        message['From'] = from_header
        message['To'] = to_header
        message['reply-to'] = reply_to_header

        message.attach(MIMEText('\r\n'.join(email.body_lines),
                                _charset='utf-8'))

        for filename in email.files_to_attach or []:
            with open(filename, 'rb') as f:
                message.attach(MIMEApplication(
                    f.read(),
                    Content_Disposition='attachment; filename="{0}"'
                                        .format(basename(filename)),
                    Name=basename(filename)
                ))

        if self.username is not None:
            try:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.ehlo()
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_address, email.to_address,
                                message.as_string())
                server.quit()
            except OSError as e:
                print('Sending email failed:\n{0}'.format(e), file=sys.stderr)
                raise EmailException(e)
        else:
            print('SMTP username not defined. Would have sent this email:')
            print(message.as_string())
            print('Original body:')
            print('\n'.join(email.body_lines))


def process_email_queue(email_queue, class_name, config: GraderConfiguration,
                        min_send_interval=2):
    assert isinstance(email_queue, Queue)

    email_sender = EmailSender(class_name, config)

    while True:
        try:
            new_email = email_queue.get(block=True, timeout=0.5)

            if new_email is None:
                break

            assert isinstance(new_email, Email)

            try:
                email_sender.send_email(new_email)
                print('EMAILER: Sent email to', new_email.to_address)
            except EmailException:
                print('EMAILER: Failed to send email to', new_email.to_address)

            sleep(min_send_interval)
        except Empty:
            pass
