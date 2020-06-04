from functools import wraps

from gkeepserver.create_user import create_user, UserType
from gkeepserver.database import db
from gkeepserver.faculty import Faculty, FacultyError
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.server_configuration import config


def raise_if_faculty_does_not_exist(func):
    """
    Decorator for FacultyMembers class methods that should not be called if a
    certain faculty username does not exist. Raises a FacultyError if the given
    username does not exist.

    :param func: the function to decorate
    :return: the new wrapped function
    """
    @wraps(func)
    def wrapper(self, username, *args, **kwargs):
        """
        Check to see that the faculty username exists.

        :param self: reference to a FacultyMembers object
        :param username: faculty username to check
        :param args: positional arguments to pass on
        :param kwargs: keyword arguments to pass on
        :return:
        """

        if not db.faculty_username_exists(username):
            raise FacultyError('There is no faculty with the username {}'
                               .format(username))

        return func(self, username, *args, **kwargs)

    return wrapper


class FacultyMembers:
    """
    This class provides functionality for adding faculty members and getting
    information about existing faculty members.
    """

    def add_faculty(self, last_name, first_name, email_address, admin=False):
        """
        Add a faculty user.

        :param last_name: last name of the faculty member
        :param first_name: first name of the faculty member
        :param email_address: email address of the faculty member
        :param admin: True if the faculty member should be an admin
        """

        username = db.insert_user(email_address, first_name, last_name,
                                  'faculty')

        if admin:
            db.set_admin(username)

        gkeepd_logger.log_info('Adding faculty user {}'.format(username))

        groups = [config.keeper_group, config.faculty_group]

        create_user(username, UserType.faculty, first_name, last_name,
                    email_address=email_address, additional_groups=groups)

        gkeepd_logger.log_debug('User {} created'.format(username))

    def promote_to_admin(self, username):
        """
        Make a faculty member an admin user.

        :param username: username of the faculty member
        """
        db.set_admin(username)

    def demote_from_admin(self, username):
        """
        Make a faculty member not an admin.

        :param username: username of the faculty member
        """
        db.remove_admin(username)

    def faculty_exists(self, username) -> bool:
        """
        Check if a faculty username exists.

        :param username: username of the faculty member
        :return: True if the username exists, False otherwise
        """
        return db.faculty_username_exists(username)

    def is_admin(self, username) -> bool:
        """
        Determine if a faculty member is an admin.

        :param username: username of the faculty member
        :return: True if the faculty member is an admin, False if not
        """
        return db.is_admin(username)

    def get_faculty_object(self, username) -> Faculty:
        """
        Get a Faculty object representing the faculty member with the given
        username.

        :param username: username of the faculty member
        :return: Faculty object representing the faculty member
        """
        return db.get_faculty_by_username(username)

    def get_faculty_objects(self) -> list:
        """
        Get a list of Faculty objects representing all of the faculty members.

        :return: list of Faculty objects
        """

        return db.get_all_faculty()
