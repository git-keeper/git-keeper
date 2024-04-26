# Copyright 2016 Nathan Sommer and Ben Coleman
# Copyright 2024 Jeffrey Bush
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
import html.parser
import os
from email.header import Header
from email.mime.base import MIMEBase
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


def _use_rn_lines(text) -> str:
    """
    Takes a string or list of strings and returns a list of strings with
    trailing whitespace removed from each line and \r\n newlines.
    """
    if isinstance(text, list):
        if any(not isinstance(line, str) for line in text):
            raise EmailException('Email body lines must be strings')
        lines = [line.rstrip() for line in text]
    elif isinstance(text, str):
        lines = [line.rstrip() for line in text.split('\n')]
    else:
        raise EmailException('Email body must be a string or a list of strings')
    return '\r\n'.join(lines)


def _create_alternative(contents: dict) -> MIMEMultipart:
    """
    Create a multipart/alternative email message with the given contents. The
    keys of the MIME text subtypes and the values are the contents.

    The order of the contents is important and the last content type is
    considered the best representation of the email.
    """
    alternative = MIMEMultipart('alternative')
    for subtype, content in contents.items():
        alternative.attach(MIMEText(content, subtype, _charset='utf-8'))
    return alternative


def _truncate_email_body(body: str, max_character_count: int,
                         start: str = '\r\n\r\n', end: str = '\r\n') -> str:
    """
    Truncate the email body if it is longer than max_character_count and 
    appends a message to the end of the email.
    """
    if len(body) > max_character_count:
        body = body[:max_character_count].rstrip()
        body += start
        body += ('ATTENTION: This email was truncated due to its '
                 'long length. If important information seems '
                 'missing, contact your instructor.')
        body += end
    return body


class HTML2Text(html.parser.HTMLParser):
    """
    HTML Parser that converts an HTML string to plain text. This filters out
    "invisible" elements and inline styles. This is very basic and does not
    attempt to format the text besides removing tags and whitespace and adding
    newlines.
    """
    REMOVE_TAGS = {'script', 'style', 'head', 'title', 'meta', 'link', 'base'}
    BLOCK_TAGS = {'div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol',
                    'li', 'dl', 'dt', 'dd', 'table', 'td', 'th', 'caption',
                    'pre', 'address', 'blockquote', 'center', 'dir',
                    'fieldset', 'form', 'isindex', 'menu', 'noframes',
                    'noscript', 'article', 'aside', 'details', 'figcaption',
                    'figure', 'footer', 'header', 'main', 'nav', 'section',
                    'summary'}

    text = ''
    __ignoring_level = 0

    def handle_starttag(self, tag: str, attrs: list):
        if tag in self.REMOVE_TAGS:
            self.__ignoring_level += 1
            return
        self.__possibly_line_break(tag)

    def handle_endtag(self, tag: str):
        if tag in self.REMOVE_TAGS:
            self.__ignoring_level -= 1
            return

    def handle_startendtag(self, tag: str, attrs: list):
        self.__possibly_line_break(tag)

    def __possibly_line_break(self, tag):
        if self.__ignoring_level <= 0:
            if tag == 'br': self.text += '\n'
            if tag == 'hr': self.text += '\n' + ('-' * 50) + '\n'
            if tag in self.BLOCK_TAGS:
                self.text += '\n\n'

    def handle_data(self, data: str):
        self.text += data

    # Ignore the others:
    #def handle_comment(self, data: str): pass
    #def handle_decl(self, decl: str): pass
    #def handle_pi(self, data: str): pass
    #def unknown_decl(self, data: str): pass


def _html_to_text(html_body: str) -> str:
    """
    Convert an HTML string to plain text. This filters out "invisible" elements
    and inline styles. This is very basic and does not attempt to format the
    text besides removing tags and whitespace and adding newlines.

    :param html_body: the HTML string to convert
    :return: the plain text representation of the HTML string
    """
    parser = HTML2Text()
    parser.feed(html_body)
    return parser.text.strip()


def create_text_email_body(body, max_character_count=1000000,
                           html_pre_body=False) -> MIMEBase:
    """
    Construct a plain text email message. The body may be a single string or a
    list of strings. If the body is a list of strings, the final email message
    body will be each of those strings joined together by newlines.

    If the email is longer than max_character_count characters, it will be
    truncated and a message will be appended to the end of the email.

    :param body: the body of the email
    :param max_character_count: if the email is longer than this number of
        characters it will be truncated
    :param html_pre_body: if True, the body of the email will be sent both
        as plain text and HTML, and for the latter the code will be escaped
        and wrapped in <pre></pre> tags

    :return: the email message, either a MIMEText or MIMEMultipart object
    """
    body = _use_rn_lines(body)

    # truncate the email with a message if need be
    body = _truncate_email_body(body, max_character_count)

    # create the body
    if html_pre_body:
        template = '<html><head></head><body><pre>{}</pre></body></html>'
        html_body = template.format(html.escape(body))
        return _create_alternative({'plain': body, 'html': html_body})
    else:
        return MIMEText(body, _charset='utf-8')


def create_html_email_body(html_body, plain=None, max_character_count=1000000):
    """
    Construct an email object with HTML and plain text content.

    The HTML and plain text bodies may be a single string or a list of
    strings. If the body is a list of strings, the final email message
    body will be each of those strings joined together by newlines.

    :param to_address: the email address to send the email to
    :param subject: the subject of the email
    :param html_body: the HTML body of the email as a string or list of strings
    :param plain: the plain text body of the email as a string or list of
        strings, defaults to generating it based on the text
    :param files_to_attach: a list of file paths to attach to the email
    :param max_character_count: if the email is longer than this number of
        characters it will be truncated
    :param priority: an EmailPriority representing the email's priority
        in the send queue
    """
    html_body = _use_rn_lines(html_body)
    html_body = _truncate_email_body(html_body, max_character_count,
                                     '<p>', '</p>')
    if not plain:
        plain = _html_to_text(html_body)
        plain = _use_rn_lines(plain)
    else:
        plain = _use_rn_lines(plain)
        plain = _truncate_email_body(plain, max_character_count)
    return _create_alternative({'text': plain, 'html': html_body})


def create_email_body_from_markdown(md: str, max_character_count=1000000):
    """
    Construct an email object with HTML and plain text content from a markdown
    string. The plain text body will be the literal markdown text.

    This requires the optional markdown library to be installed.

    :param markdown: the markdown string to convert to HTML and plain text
    :param max_character_count: if the email is longer than this number of
        characters it will be truncated
    """
    import markdown
    md = _truncate_email_body(_use_rn_lines(md), max_character_count)
    html_body = markdown.markdown(md)
    return create_html_email_body(html_body, md, max_character_count)


class Email:
    """
    An email that can be sent using smtplib and provides a method to send the
    email.
    """
    def __init__(self, to_address, subject, body, files_to_attach=None,
                 max_character_count=1000000, priority=EmailPriority.NORMAL,
                 html_pre_body=False):
        """
        Construct an email object.

        The body may be one of:
            - a single string
            - a list of strings
            - an email.base.MIMEBase object (likely MIMEText or MIMEMultipart)

        If the body is a list of strings, the final email message body will be
        each of those strings joined together by newlines.

        If the body is a MIMEBase object, it will be used as the email body
        directly without modification. In this case, the max_character_count
        and html_pre_body parameters are ignored.

        :param to_address: the email address to send the email to
        :param subject: the subject of the email
        :param body: the body of the email
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

        # Create the final message by building up a MIMEMultipart object and
        # then storing the final message as a string in message_string

        # encode headers
        from_header = Header('{0}'.format(config.from_name), 'utf-8')
        to_header = Header('{0}'.format(to_address), 'utf-8')
        subject_header = Header('{0}'.format(subject), 'utf-8')
        reply_to_header = Header('{0}'.format(config.from_address), 'utf-8')

        # put the headers in the message
        message = MIMEMultipart()
        message['Subject'] = subject_header
        message['From'] = from_header
        message['To'] = to_header
        message['reply-to'] = reply_to_header

        # attach the body
        if not isinstance(body, MIMEBase):
            body = create_text_email_body(body, max_character_count,
                                          html_pre_body)
        message.attach(body)

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
                raise EmailException('Error reading {0}: {1}'.format(file_path, e))

        # store the message as a string
        self.message_string = message.as_string()

    def __repr__(self):
        repr_string = 'To: {0}, Subject: {1}'.format(self.to_address,
                                                     self._subject)
        return repr_string

    def __lt__(self, other):
        # Provide < comparison for use by the PriorityQueue
        return self.priority < other.priority

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
