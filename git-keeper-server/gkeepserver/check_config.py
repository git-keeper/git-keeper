# Copyright 2022 Nathan Sommer and Ben Coleman
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


from gkeepcore.gkeep_exception import GkeepException
from gkeepserver.server_configuration import config, ServerConfigurationError
from gkeepserver.server_email import Email


def check_config():
    """
    Check the gkeepd server configuration file for syntax errors, and attempt
    to send an email to the admin user defined in the configuration file.

    If there are any errors, a GkeepException is raised.
    """

    try:
        config.parse()
    except ServerConfigurationError as e:
        error = ('There was an error parsing the gkeepd configuration file:\n{}'
                 .format(e))
        raise GkeepException(error)

    print('{} was parsed without errors'.format(config.config_path))

    test_email_subject = 'git-keeper test email'
    test_email_body = ('This is a test email to check that the git-keeper '
                       'server with the configured hostname {} is able to '
                       'send email. This message was sent to {}, which is the '
                       'configured admin email address. If this '
                       'message reaches its intended destination, then the '
                       'git-keeper server is able to send email.'
                       .format(config.hostname, config.admin_email))

    print('Attempting to send an email to {} with the subject "{}"'
          .format(config.admin_email, test_email_subject))

    try:
        email = Email(config.admin_email, test_email_subject, test_email_body)
        email.send()
    except Exception as e:
        error = 'There was an error in sending the email:\n{}\n'.format(e)
        error += 'Please check your email configuration'
        raise GkeepException(error)

    print('The test email was sent without errors.\n'
          'Please confirm that the email was received.')
