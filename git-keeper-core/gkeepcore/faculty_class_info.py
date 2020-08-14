# Copyright 2017 Thuy Dinh
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
Provides functionality for extracting information from the faculty's info
dictionary.

The structure of this dictionary is as follows:
{
 "class_name":{
  "open": true,
  "assignments":{
   "assignment_name":{
    "name":"assignment_name",
    "published":true,
    "reports_repo":{
     "hash":"202585432b8ff21ff4f93a886fff9b09c46eb18e",
     "path":"/home/faculty/classes/class_name/assignment_name/reports.git"
    },
    "students_repos":{
     "alovelace":{
      "first":"Ada",
      "hash":"76f608acf4d08ccd1bf07955e2600bdce3f80774",
      "last":"Lovelace",
      "path":"/home/alovelace/faculty/class_name/assignment_name.git",
      "submission_count":0,
      "time":1476986981
    }
   }
  }
 },
 "students":{
  "alovelace":{
    "email_address":"alovelace@example.edu",
    "first":"Ada",
    "home_dir":"/home/alovelace",
    "last":"Lovelace",
    "last_first_username":"lovelace_ada_alovelace",
    "username":"alovelace"
   }
  }
 }
}
"""

from time import localtime


class FacultyClassInfo:
    """
    Provides methods for extracting information from a faculty's info
    dictionary from the server.
    """

    def __init__(self, info_dict: dict):
        """
        Create the object
        :param info_dict: dictionary of information about the faculty's classes
        """

        self.info_dict = info_dict

    def class_count(self) -> int:
        """
        Get the number of classes.

        :return: number of classes
        """

        return len(self.info_dict)

    def class_list(self) -> list:
        """
        Get the list of classes.

        :return: list of classes
        """

        return list(self.info_dict.keys())

    def is_open(self, class_name) -> bool:
        """
        Determine if a class is open.

        :param class_name: name of a class
        :return: True if the class is open, False if not
        """

        return self.info_dict[class_name]['open']

    def student_count(self, class_name: str) -> int:
        """
        Get the number of students in a class.

        :param class_name: name of a class
        :return: number of students in the class
        """

        return len(self.info_dict[class_name]['students'])

    def student_list(self, class_name: str) -> list:
        """
        Get a list of the usernames of the students in a class.

        :param class_name: name of a class
        :return: list of usernames of students in the class
        """

        return list(self.info_dict[class_name]['students'])

    def class_students(self, class_name: str) -> dict:
        """
        Get a dictionary representing the students in a class. The dictionary
        maps student usernames to dictionaries representing individual
        students.

        :param class_name: name of a class
        :return: dictionary of students in the class
        """

        return self.info_dict[class_name]['students']

    def assignment_count(self, class_name: str) -> int:
        """
        Get the number of assignments for a class.

        :param class_name: name of a class
        :return: number of assignments for the class
        """

        return len(self.info_dict[class_name]['assignments'])

    def assignment_list(self, class_name: str) -> list:
        """
        Get the list of assignments for a class.

        Returns an empty list if the class does not exist, or if the class
        has no assignments.

        :param class_name: name of a class
        :return: list of assignments for a class
        """

        try:
            return list(self.info_dict[class_name]['assignments'])
        except KeyError:
            return []

    def is_published(self, class_name: str, assignment: str) -> bool:
        """
        Determine if an assignment is published.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: True if the assignment is published, False otherwise
        """

        assignment_info = self.info_dict[class_name]['assignments'][assignment]
        return assignment_info['published']

    def is_disabled(self, class_name: str, assignment: str) -> bool:
        """
        Determine if an assignment is disabled.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: True if the assignment is disabled, False otherwise
        """

        if assignment not in self.info_dict[class_name]['assignments']:
            return False

        assignment_info = self.info_dict[class_name]['assignments'][assignment]
        return assignment_info['disabled']

    def reports_hash(self, class_name: str, assignment: str) -> str:
        """
        Get the reports hash of an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: the reports hash of an assignment
        """

        assignment_info = self.info_dict[class_name]['assignments'][assignment]
        return assignment_info['reports_repo']['hash']

    def reports_path(self, class_name: str, assignment: str) -> str:
        """
        Get the reports path of an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: the reports path of an assignment
        """

        assignment_info = self.info_dict[class_name]['assignments'][assignment]
        return assignment_info['reports_repo']['path']

    def student_submitted_count(self, class_name: str, assignment: str) -> int:
        """
        Get the number of students who submitted an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: number of students who submitted the assignment
        """

        students_submitted = 0
        for student in self.student_list(class_name):
            submission_count = \
                self.student_submission_count(class_name, assignment, student)
            if submission_count != 0:
                students_submitted += 1
        return students_submitted

    def students_submitted_list(self, class_name: str, assignment: str) \
            -> list:
        """
        Get the list of students who submitted an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :return: list of students who submitted an assignment
        """

        students_submitted = []
        for student in self.student_list(class_name):
            submission_count = \
                self.student_submission_count(class_name, assignment, student)
            if submission_count != 0:
                students_submitted.append(student)
        return students_submitted

    def student_email_address(self, class_name: str, username: str) -> str:
        """
        Get the email address of a student.

        :param class_name: name of a class
        :param username: username of a student
        :return: student's email address
        """

        student_info = self.info_dict[class_name]['students'][username]
        return student_info['email_address']

    def student_first_name(self, class_name: str, username: str) -> str:
        """
        Get the first name of a student.

        :param class_name: name of a class
        :param username: username of a student
        :return: student's first name
        """

        return self.info_dict[class_name]['students'][username]['first']

    def student_home_dir(self, class_name: str, username: str) -> str:
        """
        Get the home directory of a student.

        :param class_name: name of a class
        :param username: username of a student
        :return: student's home directory
        """

        return self.info_dict[class_name]['students'][username]['home_dir']

    def student_last_name(self, class_name: str, username: str) -> str:
        """
        Get the last name of a student.

        :param class_name: name of a class
        :param username: username of a student
        :return: student's last name
        """

        return self.info_dict[class_name]['students'][username]['last']

    def student_assignments(self, class_name: str, username: str) \
            -> list:
        """
        Get all the assignments for a student.

        :param class_name: name of a student
        :param username: username of a student
        :return: an info dict of all the assignments for a student
        """

        student_assignments = []
        for an_assignment in self.assignment_list(class_name):
            student_assignment = self.info_dict[class_name]['assignments'][
                an_assignment]['students_repos'][username]
            if student_assignment is not None:
                student_assignments.append(an_assignment)
        return student_assignments

    def student_assignment_hash(self, class_name: str, assignment: str,
                                username: str) -> str:
        """
        Get the hash of a student's assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :param username: username of a student
        :return: the hash of a student's assignment
        """

        assignment_info = self.info_dict[class_name]['assignments'][assignment]
        return assignment_info['students_repos'][username]['hash']

    def student_assignment_path(self, class_name: str, assignment: str,
                                username: str) -> str:
        """
        Get the path of a student's assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :param username: username of a student
        :return: the path of a student's assignment
        """

        assignment_info = self.info_dict[class_name]['assignments'][assignment]
        return assignment_info['students_repos'][username]['path']

    def student_submission_count(self, class_name: str, assignment: str,
                                 username: str) -> int:
        """
        Get the submission count of a student for an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :param username: username of a student
        :return: student's submission count for an assignment
        """

        assignment_info = self.info_dict[class_name]['assignments'][assignment]
        return assignment_info['students_repos'][username]['submission_count']

    def student_submission_time(self, class_name: str, assignment: str,
                                username: str):
        """
        Get the Unix time a student last submitted an assignment.

        :param class_name: name of a class
        :param assignment: name of an assignment
        :param username: username of a student
        :return: the Unix time a student last submitted an assignment.
        """

        assignment_info = self.info_dict[class_name]['assignments'][assignment]
        return assignment_info['students_repos'][username]['time']

    def submission_time_string(self, class_name: str, assignment: str,
                               username: str,
                               format_string='{1}/{2}/{0} {3}:{4}:{5}') -> str:
        """
        Get a string of the time a student last submitted an assignment.
        You can pass your own format string. These are the fields:
        {0}: year, {1}: day, {2}: month, {3}: hour, {4}: minute, {5}: second

        :param class_name: name of a class
        :param assignment: name of an assignment
        :param username: username of a student
        :param format_string: the format of the time string
        :return: a string of the time a student last submitted an assignment
        """

        time = localtime(self.student_submission_time(class_name, assignment,
                                                      username))
        return format_string.format(time.tm_year, time.tm_mon, time.tm_mday,
                                    time.tm_hour, time.tm_min, time.tm_sec)

    def get_username_from_name(self, class_name: str, name: str) -> str:
        """
        Get the username of a student from his/her full name.

        :param class_name: name of a class
        :param name: a student's full name in the format
        "last name, first name"
        :return: student's username
        """

        for username in self.student_list(class_name):
            name_form = '{0}, {1}'.format(
                self.student_last_name(class_name, username),
                self.student_first_name(class_name, username))
            if name_form == name:
                return username

    def student_last_first_username(self, class_name: str, username: str) \
            -> str:
        """
        Get the last name, first name, and username of a student.

        :param class_name: name of a class
        :param username: username of a student
        :return: a string in the format "last name, first name, username"

        """

        student_info = self.info_dict[class_name]['students'][username]
        return student_info['last_first_username']
