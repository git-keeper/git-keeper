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
Provides bash and zsh completion for gkeep client.
"""

import os
import shlex
import string
import tempfile
import getpass
import pickle
from datetime import datetime

from gkeepclient.client_configuration import config
from gkeepclient.server_interface import server_interface
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.faculty_class_info import FacultyClassInfo


def completion():
    """Completion function for bash."""
    # Available environment variables:
    # COMP_LINE: the current command line
    # COMP_POINT: the index of the cursor in the command line
    # COMP_CWORD: the index of the current word (the one the cursor is on)
    # COMP_WORDS: an array of all the words in the command line
    # and others...

    # # Get command line using COMP_LINE and COMP_POINT
    #point = int(os.environ['COMP_POINT'])
    #line = os.environ['COMP_LINE'][:point]
    # try:
    #     words = shlex.split(line)
    # except ValueError:
    #     # We may have an unmatched quote in the final token
    #     # Try to add either a ' or " at the end
    #     try: words = shlex.split(line + '"')
    #     except ValueError: words = shlex.split(line + "'")

    # # If we ended with an un-quoted space add a new blank word to the end
    # if line[-1].isspace() and words[-1][-1] != line[-1]: words.append('')
    # words = words[1:] # Remove the "gkeep" command

    # Get command line using COMP_WORDS and COMP_CWORD
    cword = int(os.environ["COMP_CWORD"])
    words = os.environ["COMP_WORDS"].split("\v")[1:cword+1]
    words = [__unquote(word) for word in words]
    if not words: return

    # Handle optional arguments
    words = __handle_opts(words)
    if not words: return

    # Name of one of the sub-commands
    if len(words) == 1:
        __results(key+' ' for key in __SUBCOMMANDS if key.startswith(words[0]))

    # Use the sub-command to do the remainder of the command line arguments
    __subcommand_completion = __SUBCOMMANDS.get(words[0])
    if __subcommand_completion is not None:
        __results(__subcommand_completion(words[1:]))


def __results(words: list[str]):
    """Emits the results found for the completion."""
    print('\v'.join(words))


ALLOWED_CHARS = string.ascii_letters + string.digits + '_@%+=:,./-'


def __escape(word: str) -> str:
    """
    Escape a word for the bash command line. The shlex.quote() could be used, but quoting sometimes
    confuses the bash completion function. This function instead add escapes for disallowed chars.
    """
    return ''.join(c if c in ALLOWED_CHARS else '\\'+c for c in word)


def __unquote(word: str) -> str:
    """Remove quotes from a shell "word"."""
    word = shlex.split(word)
    return word[0] if word else ''


OPT_SHORT_ARGS = ('-h', '-v', '-y', '-f')
OPT_LONG_ARGS = ('--help', '--version', '--yes', '--config_file')


def __handle_opts(words: list[str]) -> list[str]:
    """Handle the options with - and -- for the completion function."""
    active = words[-1]

    # Help option always exits
    if '-h' in words or '--help' in words:
        return []
    
    # Check if the active word is a - or -- argument
    if active == '--':
        __results(OPT_LONG_ARGS)
        return []
    if active == '-':
        __results(OPT_SHORT_ARGS + OPT_LONG_ARGS)
        return []
    if active[:2] == '--':
        __results(opt for opt in OPT_LONG_ARGS if opt.startswith(active))
        return []
    if active[:1] == '-':
        __results(opt for opt in OPT_SHORT_ARGS if opt.startswith(active))
        return []

    # Check if the active word is the config file path
    if len(words) >= 2 and words[-2] in ('-f', '--config_file'):
        __results(__complete_file(active))
        return []

    # Get the config file from the command line if it exists
    if '-f' in words:
        config.set_config_path(words[words.index('-f')+1])
    elif '--config_file' in words:
        config.set_config_path(words[words.index('--config_file')+1])

    # Remove all options from the command line
    return [arg for arg in words if arg[:1] != '-']


def __config_parsed():
    """
    Try to parse the config file if it hasn't been parsed yet. Returns True if the config file was
    parsed successfully and False otherwise.
    """
    if not config.is_parsed():
        try:
            config.parse()
        except GkeepException as e:
            return False
    return True


def __server_interface_connected():
    """
    Try to have the server interface connected returning True if successful and False otherwise.
    """
    if not server_interface.is_connected():
        if __config_parsed():
            try:
                server_interface.connect()
            except GkeepException as e:
                return False
    return True


def __add(words: list[str]) -> list[str]:
    """Completion for the command line gkeep add <new class name> <csv file>"""
    if len(words) == 2: return __complete_csv(words[1])
    return [] # either a new class name (which could be anything) or an unknown argument


def __modify(words: list[str]) -> list[str]:
    """Completion for the command line gkeep modify <class name> <csv file>"""
    if len(words) == 1: return __complete_class_name(words[0])
    if len(words) == 2: return __complete_csv(words[1])
    return [] # an unknown argument


def __new(words: list[str]) -> list[str]:
    """Completion for the command line gkeep new <new directory> [<template name>]"""
    if len(words) == 1: return __complete_directory(words[0], False)
    if len(words) == 2:
        template_path = (config.templates_path if __config_parsed() else
            os.path.expanduser('~/.config/git-keeper/templates'))
        if not os.path.isdir(template_path): return []
        files = sorted(f for f in os.listdir(template_path) if os.path.isdir(f))
        return __complete_word(words[1], files)
    return [] # an unknown argument


def __upload(words: list[str]) -> list[str]:
    """Completion for the command line gkeep upload <class name> <directory>"""
    if len(words) == 1: return __complete_class_name(words[0])
    if len(words) == 2: return __complete_directory(words[1])
    return [] # an unknown argument


def __update(words: list[str]) -> list[str]:
    """
    Completion for the command line
    gkeep update <class name> <directory> { base_code | email | tests | config | all }
    """
    if len(words) == 1: return __complete_class_name(words[0])
    if len(words) == 2: return __complete_directory(words[1])
    if len(words) == 3:
        return __complete_word(words[2], ('base_code', 'email', 'tests', 'config', 'all'))
    return [] # an unknown argument


def __publish(words: list[str]) -> list[str]:
    """Completion for the command line gkeep publish <class name> <assignment>"""
    if len(words) == 1: return __complete_class_name(words[0])
    if len(words) == 2: return __complete_assignment(words[0], words[1], unpublished=True)
    return [] # an unknown argument


def __delete(words: list[str]) -> list[str]:
    """Completion for the command line gkeep delete <class name> <assignment>"""
    if len(words) == 1: return __complete_class_name(words[0])
    if len(words) == 2: return __complete_assignment(words[0], words[1], unpublished=True)
    return [] # an unknown argument


def __disable(words: list[str]) -> list[str]:
    """Completion for the command line gkeep disable <class name> <assignment>"""
    if len(words) == 1: return __complete_class_name(words[0])
    if len(words) == 2: return __complete_assignment(words[0], words[1], published=True)
    return [] # an unknown argument


def __fetch(words: list[str]) -> list[str]:
    """Completion for the command line gkeep fetch <class name> <assignment> <directory>"""
    if len(words) == 1: return __complete_class_name(words[0])
    if len(words) == 2: return __complete_assignment(words[0], words[1], published=True)
    if len(words) == 3: return __complete_directory(words[2], False)
    return [] # an unknown argument


def __query(words: list[str]) -> list[str]:
    """
    Completion for the command line
    gkeep query { classes | assignments | recent | students } [<#>]
    """
    if len(words) == 1:
        return __complete_word(words[0], ('classes', 'assignments', 'recent', 'students'))
    return [] # either a number of days for recent or an unknown argument


def __trigger(words: list[str]) -> list[str]:
    """Completion for the command line gkeep trigger <class name> <assignment> [<student> ...]"""
    if len(words) == 1: return __complete_class_name(words[0])
    if len(words) == 2: return __complete_assignment(words[0], words[1], published=True)
    # List possible students but remove any already listed
    possible_students = __complete_student(words[0], words[-1])
    already_listed = set(words[2:-1])
    return [student for student in possible_students if student[:-1] not in already_listed]


def __passwd(words: list[str]) -> list[str]:
    """Completion for the command line gkeep passwd <student>"""
    if len(words) == 1: return __complete_any_student(words[0])
    return [] # an unknown argument


def __test(words: list[str]) -> list[str]:
    """Completion for the command line gkeep test <class name> <assignment> <solution path>"""
    if len(words) == 1: return __complete_class_name(words[0])
    if len(words) == 2:
        return __complete_assignment(words[0], words[1], unpublished=True, published=True)
    if len(words) == 3: return __complete_directory(words[2], False)
    return [] # an unknown argument


def __local_test(words: list[str]) -> list[str]:
    """Completion for the command line gkeep local_test <assignment directory> <solution path>"""
    if len(words) == 1: return __complete_directory(words[0])
    if len(words) == 2: return __complete_directory(words[1], False)
    return [] # an unknown argument


def __status(words: list[str]) -> list[str]:
    """Completion for the command line gkeep status <class name> { open | closed }"""
    if len(words) == 1: return __complete_class_name(words[0])
    if len(words) == 2: return __complete_word(words[1], ('open', 'closed'))
    return [] # an unknown argument


__SUBCOMMANDS = {
    'check': None, # no arguments
    'add': __add,
    'modify': __modify,
    'new': __new,
    'upload': __upload,
    'update': __update,
    'publish': __publish,
    'delete': __delete,
    'disable': __disable,
    'fetch': __fetch,
    'query': __query,
    'trigger': __trigger,
    'passwd': __passwd,
    'test': __test,
    'local_test': __local_test,
    'config': None, # no arguments
    'status': __status,
    'add_faculty': None, # all arguments can be anything so just don't have a completion function
    'admin_promote': None, # the one argument is an email address
    'admin_demote': None, # the one argument is an email address
}


def __complete_file(path: str) -> list[str]:
    """
    Complete a filename partial path. This uses __get_files. Directory names end with a '/'. File
    names end with a space ' '. All directory / file names are escaped for the bash command line.
    """
    files = __get_files(path)
    dirs = [__escape(f+os.path.sep) for f in files if os.path.isdir(f)]
    files = [__escape(f)+' ' for f in files if os.path.isfile(f)]
    return dirs + files


def __complete_csv(path: str) -> list[str]:
    """
    Complete a CSV filename partial path. This uses __get_files and then filters to only return
    directories or files that end with .csv (ignoring case). Directory names end with a '/'. File
    names end with a space ' '. All directory / file names are escaped for the bash command line.
    """
    files = __get_files(path)
    dirs = [__escape(f+os.path.sep) for f in files if os.path.isdir(f)]
    csvs = [__escape(f)+' ' for f in files
            if os.path.isfile(f) and os.path.splitext(f)[1].lower() == '.csv']
    return dirs + csvs


def __complete_directory(path: str, assignment_dir: bool = True) -> list[str]:
    """
    Complete directory names from partial path. This uses __get_files and then filters to only
    return directories (which end with a /). If assignment_dir is True (the default) then assignment
    directories end with a space instead of a /. All directory names are escaped for the bash
    command line.
    """
    # Path is already an assignment directory
    if path and path[-1] != '/' and __is_assignment_dir(os.path.expanduser(path)):
        return [__escape(path) + ' ']
    # Get all directories
    dirs = [f for f in __get_files(path) if os.path.isdir(f)]
    if not assignment_dir:
        # Always end with just a /
        return [__escape(d+os.path.sep) for d in dirs]
    # End with a space if the directory could be an assignment (contains base_code/email.txt/tests)
    return [__escape(d) + ' ' if __is_assignment_dir(d) else __escape(d+os.path.sep)
            for d in dirs]


def __is_assignment_dir(path: str) -> bool:
    """
    Return True if the path represents an assignment directory (i.e. contains base_code, tests, and
    email.txt) and False otherwsie.
    """
    return (os.path.isdir(os.path.join(path, 'base_code')) and
            os.path.isdir(os.path.join(path, 'tests')) and
            os.path.isfile(os.path.join(path, 'email.txt')))


def __complete_word(word: str, possibilities: list[str]) -> list[str]:
    """
    Return a list of the complete words from a partial word given the list of possibilities. The
    return possible words have a space added to the end of them.
    """
    return [__escape(w)+' ' for w in possibilities if w.startswith(word)]


def __get_info(max_age: int|float = 15) -> FacultyClassInfo:
    """
    Get the faculty class info from the server. This will create a persistent cache (even in
    between runs of this program) for faster access.
    
    The max_age of the cache in seconds can be set and defaults to 15 seconds.
    """
    user = getpass.getuser()
    filename = os.path.join(tempfile.gettempdir(), 'gkeep-info-'+user)

    # Attempt to get the results from the cache
    try:
        age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(filename))
        if age.total_seconds() <= max_age:
            with open(filename, 'rb') as file:
                return FacultyClassInfo(pickle.load(file))
    except OSError:
        # file doesn't exist or similar
        pass

    if not __server_interface_connected():
        return FacultyClassInfo({})

    # Get the info from the server
    info = server_interface.get_info()

    # Cache the results
    os.makedirs(os.path.dirname(filename), 0o700, True)
    with open(filename, 'wb') as file:
        pickle.dump(info.info_dict, file)
    os.chmod(filename, 0o600)

    # Return the info
    return info


def __complete_class_name(class_name: str) -> list[str]:
    """
    Return a list of the complete class names (with spaces at the end) from a partial class name.
    This requires running `gkeep query classes`.
    """
    words = __complete_word(class_name, __get_info().class_list())
    if not words:
        words = __complete_word(class_name, __get_info(0.5).class_list())
    return words


def __complete_assignment(class_name: str, assignment: str, unpublished: bool = False,
                          published: bool = False, disabled: bool = False) -> list[str]:
    """
    Return a list of the complete assignment names (with spaces at the end) from a partial
    assignment name from a particular class. This also filters out unpublished, published, and
    disabled assignments.
    """
    assignments = __get_assignments(class_name, unpublished, published, disabled)
    words = __complete_word(assignment, assignments)
    if not words:
        assignments = __get_assignments(class_name, unpublished, published, disabled, 0.5)
        words = __complete_word(assignment, assignments)
    return words


def __get_assignments(class_name: str, unpublished: bool, published: bool, disabled: bool,
                      max_age: int|float = 15) -> list[str]:
    info = __get_info(max_age)
    assignments = info.assignment_list(class_name)
    if not unpublished:
        assignments = [a for a in assignments if not info.is_published(class_name, a)]
    if not published:
        assignments = [a for a in assignments if info.is_published(class_name, a)]
    if not disabled:
        assignments = [a for a in assignments if not info.is_disabled(class_name, a)]
    return assignments


def __complete_student(class_name: str, student: str) -> list[str]:
    """
    Return a list of the complete student names (with spaces at the end) from a partial student name
    from a particular class.
    """
    words = __complete_word(student, __get_students(class_name))
    if not words:
        words = __complete_word(student, __get_students(class_name, 0.5))
    return words


def __get_students(class_name: str, max_age: int|float = 15) -> list[str]:
    try:
        return __get_info(max_age).student_list(class_name)
    except KeyError:
        return []


def __complete_any_student(student: str) -> list[str]:
    """
    Return a list of the complete student names (with spaces at the end) from a partial student name
    from any class.
    """
    words = __complete_word(student, __get_all_students())
    if not words:
        words = __complete_word(student, __get_all_students(0.5))
    return words


def __get_all_students(max_age: int|float = 15) -> list[str]:
    info = __get_info(max_age)
    return list(set(student for class_name in info.class_list()
                    for student in info.student_list(class_name)))


def __get_files(path: str) -> list[str]:
    """
    Gets all of the files from a path where the final component of the path may only be part of a
    filename / directory name. Uses the directory components available and then the files /
    directories in that final directory must start with the given partial path.

    Hidden files are not returned in the list unless the partial filename starts with a '.'.
    The .. directory is always returned as the first item in the list if the partial path is empty
    or a directory.

    Paths that begin with ~ have the user's home directory expanded.
    """
    path = os.path.expanduser(path)

    # Blank path, list everything but hidden files
    if path == '':
        return ['..'] + [name for name in os.listdir('.') if name[0] != '.']

    # A complete path to a directory, list all files in it except hidden
    elif os.path.isdir(path):
        return [os.path.join(path, '..')] + [
            os.path.join(path, name) for name in os.listdir(path) if name[0] != '.']

    # Only part of a filename - get the directory part of the path
    directory = os.path.dirname(path)
    if directory == '':
        # Only part of a file name with no directory in it
        return [name for name in os.listdir('.') if name.startswith(path)]
    elif os.path.isdir(directory):
        # Only part of a file name with a directory in it
        basename = os.path.basename(path)
        return [os.path.join(directory, name) for name in os.listdir(directory)
                if name.startswith(basename)]

    # Invalid path
    return []
