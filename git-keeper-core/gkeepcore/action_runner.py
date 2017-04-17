from abc import ABCMeta, abstractmethod
import os
import difflib
import shutil
import re  # Reg expression
import sys
from gkeepcore.shell_command import run_command


class ErrorException(Exception):
    pass
# print warning right as soon as they come


class WarningException(Exception):
    pass


class ActionConstructorException(Exception):
    pass


class FatalActionException(Exception):
    pass


''''

all constructors should take in an error_message OR warning (can take on but
not both)


'''''


class ActionsBase(object):
    """
    Abstract class for ActionRunner
    """
    __metaclass__ = ABCMeta

    # errorString = []

    @abstractmethod
    def run(self):
        pass

# diff library, or command line diff


class FilesExist(ActionsBase):

    """
    Class to check if student files exist according to the names provided
    If any files don't exist, an error_message will be printed with name of
    file
    """

    # make sure either error_message or warning is set, otherwise throw other
    # kind of exception, default warning is needed, pass in the non essential
    # files list
    def __init__(self, student_dir, required_files, non_vital_files=None,
                 error='Fatal Error! {0} does not exist!',
                 warning='Warning: {0} does not exist'):
        """
        Creates class instance of files exist, which checks if the required
        files exist in the students submission

        :param student_dir: directory of student's files
        :param required_files: list of files needed to run the program to grade
        :param non_vital_files: list of extra files that can be used for the
        program to grade
        :param error: fatal error_message message which occurs if
        :param warning: non fatal warning message
        :return:
        """

        self.student_files = []
        self.student_dir = student_dir
        self.required_files = required_files
        self.nonessential_files = non_vital_files
        self.errorString = []
        self.error = error
        self.warning = warning

        # Checking if the error_message/warning message is correctly written
        try:
            self.error.format("")
        except ValueError:
            raise ActionConstructorException("Malformed error_message: "
                                             "{0}".format(self.error))

        try:
            self.warning.format("")
        except ValueError:
            raise ActionConstructorException("Malformed error_message message:"
                                             "{0}".format(self.warning))

    def run(self):
        """

        :return:
        """

        # Check if directory exists and if it does copies file names
        try:
            self.student_files = os.listdir(self.student_dir)
        except OSError as err:
            raise ErrorException("OS error: {0}".format(err))

        # Checks if required files are in the student files
        for fileName in self.required_files:
            if fileName not in self.student_files:
                if self.error is not None:
                    raise ErrorException(self.error.format(fileName))

        # Checks if non-essential files are in the student files
        if self.nonessential_files is not None:
            for fileName in self.nonessential_files:
                if fileName not in self.student_files:
                    if self.warning is not None:
                        # replace "" with the error_message message
                        print(self.warning.format(
                            fileName))


class RunCommand(ActionsBase):

    def __init__(self, command, output, bad_output, error_is_fatal,
                 error_message='Error : Your code doesnt compile correctly '
                               'with my '
                               'tests:\n{0}\n'):
        """
        Run a shell command

        :param command:
        :param bad_output:
        :param error_message:
        :return:
        """

        self.command = command
        if type(output) == str:
            self.output_filename = output
            self.print_output = False
        else:
            self.print_output = output
            self.output_filename = None
        self.bad_output_RE = bad_output
        self.error_message = error_message
        self.error_is_fatal = error_is_fatal
        self.student_output = ""

        # Checking if the error_message/warning message is correctly written
        try:
            self.error_message.format("")
        except ValueError:
            raise ActionConstructorException("Malformed error_message: "
                                             "{0}".format(self.error_message))

    def run(self):
        """

        :return: "Bad" or "Good" depending on if tests failed or not
        """

        error_occurred = False

        try:
            self.student_output = run_command(self.command)
        except Exception as e:  # occurs if non zero returned from above
            self.student_output = str(e)  # even stores errors that occured
            error_occurred = True

        if self.print_output:
            print(self.student_output)
        elif self.output_filename is not None:
            # save file by filename w. out
            text_file = open(self.output_filename, "w")
            text_file.write(self.student_output)
            text_file.close()

        # check if program output matches the RE
        if self.bad_output_RE is not None:
            bad_output = re.match(self.bad_output_RE, self.student_output)
            if bad_output is not None:
                raise ErrorException("The bad output RE does not match the"
                                     "Student's "
                                     "Output: {0}").format(self.error_message)

        if self.error_is_fatal and error_occurred:
            raise FatalActionException(self.error_message.format(
                                                         self.student_output))


class CopyFiles(ActionsBase):
    """
    Action to copy students files to test dir
    """

    def __init__(self, required_files, optional_files, student_dir, dest_dir):
        """

        :param required_files:
        :param optional_files:
        :param student_dir:
        :param dest_dir:
        :return:
        """
        self.required_files = required_files
        self.optional_files = optional_files
        self.student_dir = student_dir  # default is the current working dir
        self.test_dir = dest_dir
        self.error = ""
        self.warning = ""

    def run(self):

        source = self.student_dir

        # print(self.required_files)
        # print(self.test_dir)
        # if not os.path.exists(self.test_dir):
        #     os.makedirs(self.test_dir)
        #
        # try:

        try:
            for f in self.required_files:
                shutil.copy((os.path.join(source, f)), self.test_dir)

        except Exception as e:
            self.error = ("There was an error copying required "
                          "files: {0}").format(e)
            raise ErrorException(self.error)

        try:
            for f in self.optional_files or []:
                # if optional files dont exist, then empty list []
                shutil.copy((os.path.join(source, f)), self.test_dir)
        except Exception as e:
            self.warning = \
                "There was a warning copying optional files: {0}".format(e)
            raise WarningException(self.warning)
            pass


class Diff(ActionsBase):
    """
    Determine if the contents of 2 files are different or the same
    """

    def __init__(self, filename1, filename2, output=False,
                 different_is_fatal=True, different_message='',
                 same_message='', directory=None):
        """

        :param filename1: Relative path of the first file
        :param filename2: Relative path of the second file
        :param output: Throws the output away if false, prints it if True, writes it to a file
                 if it is a string
        :param different_is_fatal: If True, all actions will halt if the files are different
        :param different_message: Message to print if the files' contents are different
        :param same_message: Message to print if the files' contents are the same
        :return:
        """

        self.filename1 = filename1
        self.filename2 = filename2
        if type(output) == str:
            self.output_filename = output
            self.print_output = False
        else:
            self.print_output = output
            self.output_filename = None
        self.different_is_fatal = different_is_fatal
        self.different_message = different_message
        self.same_message = same_message
        self.directory = directory

    def run(self):
        differences_string = difflib.SequenceMatcher(None,
                                                     self.filename1.read(),
                                                     self.filename2.read())

        if self.print_output:
            print(differences_string)
        elif self.output_filename is not None:
            # save file by filename w. out
            text_file = open(self.output_filename, "w")
            text_file.write(differences_string)
            text_file.close()

        if differences_string != '':
            if self.different_is_fatal:
                print(self.different_message)
                return
        else:
            print(self.same_message)


class Search(ActionsBase):
    """
    Try to match a regular expression against the contents of a file
    """

    def __init__(self, pattern, desired_result, filename,
                 success_message, fail_message, directory=None):
        """

        :param pattern: A regular expression suitable for use with the Python's
                re module
        :param filename: The relative path of the file in which to search

        """

        self.filename = filename
        self.pattern = pattern   # probably do not need to do: re.compile()
        # pattern)
        self.directory = directory
        if directory is None:
            self.directory = os.getcwd()
        if desired_result == "Match":
            self.match_expected = True
            self.mismatch_expeted = False
        elif desired_result == "Mismatch":
            self.match_expected = False
            self.mismatch_expeted = True
        else:
            # this should never happen!
            self.match_expected = False
            self.mismatch_expeted = False
        self.success_message = success_message
        self.fail_message = fail_message

    def run(self):

        file = open(self.filename, "r")
        data = file.read()
        match = re.search(self.pattern, data)

        if (self.mismatch_expeted and match is None) or \
                (self.match_expected and match is not None):
            # there is  no mismatch/a match  which is what is expected!
            print(self.success_message)
        elif (self.mismatch_expeted and match is not None) or \
                (self.match_expected and match is None):
            # EITHER: Did not want to see something in output, but found it
            # OR: wanted to see something in output, but cannot find it
            # Thus this is an error
            print(self.fail_message.format(pattern=self.pattern, output=data))

        # do a search through the entire document rather than line by line
        # set MATCH bool to true
        # re.search through one string

        # returns a match object, otherwise none.

        # MATCH :
        # Scan through string looking for the first location where the
        # regular expression pattern produces a match, and return a
        # corresponding MatchObject instance. Return None if no position in
        #  the string matches
        # the pattern; note that this is different from finding a zero-length
        # match at some point in the string.

        # if it does match, say nothing
        # if not present then say {Custom Message}.format0...i
        # expected to find ___
        # but your output was ____

            # MAKE a test assignment code with  student code to print out
            # stings
            # info on structure in Wiki
            # Edit search, more testing

'''

        if self.mismatch_expeted and not MATCH:
            if search_results == "":
                print success_message
            else:
                return "Some lines matched: " + search_results
                if error

        if self.match_expected and MATCH:
            if search_results == "":
                print success
            else:
                return "blah {out} and {file}".format(out = self.out,
                                                      results = search_results)
                print success
        return


"blah {out} and {file}".format(out = self.out)
'''


class ActionRunner(ActionsBase):
    """
    This is a working draft of an interface for a class ActionRunner which can
    run a sequence of actions to test a
    student submission.
    """

    """
    CONSTRUCTOR

    There is one constructor for ActionRunner
    """

    def __init__(self,
                 timeout=10,
                 timeout_error="Testing your submission took too long. "
                               "Maybe you have an infinite loop?",
                 memlimit=1024,
                 memlimit_error="Memory limit exceeded",
                 working_dir=os.getcwd(),
                 submission_dir=sys.argv[1]):

        """
       The ActionRunner constructor has no required parameters. It has the
       following optional parameters:

       :param timeout (default 10): Testing will run for at most timeout number
        of seconds, at which time it will kill
       the tests and print an error_message message.
       :param timeout_error (default 'Testing your submission took too long.
       Maybe you have an infinite loop?'): The error_message message to
       print when there is a timeout.
       :param memlimit (default 1024): Testing will use at most memlimit
       megabytes of memory, at which time it will kill the tests and print
       an error_message message.
       :param memlimit_error (default 'Testing your submission used too much
       memory.'): The error_message message to print when testing uses too
       much memory.
       :param working_dir (defaults to the current working directory): Path to
       the directory in which to run the tests.
       :param submission_dir (defaults to sys.argv[1]): The path to the
       directory containing the student's submission.

       :return: void
       """
        self.actionList = []
        self.timeout = timeout
        self.timeout_error = timeout_error
        self.memlimit = memlimit
        self.memlimit_error = memlimit_error
        self.working_dir = working_dir
        self.submission_dir = submission_dir

    """
    ACTION METHODS

    These methods add actions to the ActionRunner's internal list of actions.
    The actions will not be run immediately, but they will be run in the order
    in which they are added.
    There are four action methods

    files_exist(self, required_files, optional_files=None, error_message='Fatal
     Error! {0} does not exist!', warning='Warning: {0} does not exist')
    copy_files(self, required_files, optional_files=None)
    run_command(self,  command, bad_output=None, error_message='Your code does
     not compile correctly with my tests:\n\n{0}')
    run(self, success='All tests passed!')

    """

    def files_exist(self, required_files, optional_files=None,
                    error='Error: {0} does not exist.',
                    warning='Warning: {0} does not exist.'):
        """
         Check that files exist in submission_dir

        :param required_files: An iterable containing file names relative to
        submission_dir which must exist. If any do not exist,
        an error_message message is printed and all action halts.

        :param optional_files: An optional iterable containing filenames
        relative to submission_dir. A warning will be printed if any of the
        files do not exist. Action will not halt.

        :param error: The error_message message to print if a required file
        does not exist. Must contain {} or {0} so that the
        filename can be inserted with error_message.format(filename).

        :param warning: The warning message to print if an optional file does
        not exist. Must contain {} or {0} so that the filename can be
        inserted with error_message.format(filename).

        :return: void
        """

        self.actionList.append(FilesExist(self.submission_dir, required_files,
                                          optional_files, error, warning))

    def copy_files(self, required_files, optional_files=None,
                   dest=os.getcwd()):
        """
        Copy files from submission_dir to the the destination (by default the
        current working dir)

        :param required_files: An iterable containing filenames (without path)
        that will need to be copied)
        :param optional_files: An optional iterable containing filenames.
        :param dest: The directory to copy into. This will be working_dir if
        not provided. If provided it will be
        treated as a relative path to working_dir. It will will be created if
        it does not already exist.

        :return: void
        """

        self.actionList.append(CopyFiles(required_files,
                                         optional_files,
                                         self.submission_dir,
                                         dest))

    def run_command(self,  command, output=False, bad_output=None,
                    error_is_fatal=True,
                    error_message='Error running tests:\n\n{0}'):
        """
         Run a shell command

        :param command: The command to run as a list or a string
        :param output: If True, print the output of the command. If False, do
        nothing with the output. If it is a
        string, treat it as a filename relative to working_dir and write the
        output to that file
        :param bad_output: A regular expression suitable for Python's re
        module. If the pattern matches, treat it the
        same as if the command exited with a non-zero status
        :param error_is_fatal: If True and the command returns a non-zero
        exit \code, halt all actions
        :param error_message: The error_message message to print if the command
         returns a non-zero exit code. If the command contains a formatting
         specifier ({} or {0}) then the output of the command will be inserted
         into the message.

        :return: void
        """
        self.actionList.append(RunCommand(command, output, bad_output,
                                          error_is_fatal, error_message))

    def run(self, success_message='All tests passed!'):
        """
        The command that runs the action methods that were called

        :param success_message: The message to print if all actions have been
        run with no errors

        :return: None
        """

        success = True
        try:
            for action in self.actionList:
                action.run()
            # print( action, " finished running\n")

        # This occurs if an action fails fatally - still continue program,
        except FatalActionException as error:
            success = False
            print(error)  # We want to exit and send the student a message

        # Occurs if there is is an error running the action
        except Exception as e:
            error = "There was an error: {0}".format(e)
            print(e)
            # We want to exit and send the student a message
            exit(0)

        if success:
            print(success_message)
