from abc import ABCMeta,abstractmethod
import os
import shutil
#import Reg expression
import sys
from gkeepcore.shell_command import run_command


class ErrorExeption( Exception):
    pass


# print warnining right as soon as they come
class WarningExeption( Exception):
    pass

class ActionConstructorExeption( Exception):
    pass




''''

all constructors should take in an error OR warning (can take on but not both)


'''''

class ActionsBase(object):
    __metaclass__ = ABCMeta

    errorString = []

    @abstractmethod
    def run(self):
        pass





'''

 Check if student files exist according to the names provided
 If any files dont exist, error will be printed with name of file substituted for the {0}
'''
class FilesExist(ActionsBase):


    # make sure either error or warning is set, otherwise throw other kind of exception
    # default warning is needed
    # pass in the non essential files list
    def __init__(self, studentDIR, requiredFiles, nonEssentialFiles , error='Fatal Error! {0} does not exist!', warning='Warning: {0} does not exist' ):
        self.student_files = os.listdir(studentDIR)

        self.required_files = requiredFiles
        self.nonessential_files = nonEssentialFiles

        self.errorString = []
        self.error = error
        self.warning = warning

        # Checking if the error/warning message is correctly written
        try:
            self.error.format("")
            self.warning.format("")
        except ValueError:
            raise ActionConstructorExeption("Malformed error message: {0}".format(self.error))
            raise ActionConstructorExeption("Malformed error message: {0}".format(self.warning))


    def run(self):

        # Checks if required files are in the student files
        for fileName in self.required_files:
            if fileName not in self.student_files:
                if self.error is not None:
                    raise ErrorExeption (self.error.format(fileName))

        # Checks if non-essential files are in the student files
        for fileName in self.nonessential_files:
            if fileName not in self.student_files:
                if self.error is not None:
                    raise ErrorExeption (self.error.format(fileName)) # replace "" with the error message,


class runCommad(ActionsBase):

    def __init__(self, command, bad_output_pattern, error='Your code does not compile correctly with my tests:\n\n{0}'):
        self.command = command
        self.bad_output_pattern = bad_output_pattern
        self.error = error


    def run(self):

        prog_output = ""
        try:
            prog_output = run_command(self.command)
        except Exception as e:
            prog_output = str(e)
            #self.error = "There was an error: {0}".format(e)
            #print (self.error)
        #import Reg expression and check if output



'''
 Action to copy students files to test dir
'''
class CopyFiles(ActionsBase):

    def __init__(self, requiredFiles, nonEssentialFiles, student_dir):
        self.required_files = list(requiredFiles)
        self.nonessential_files = list(nonEssentialFiles)
        self.student_dir = student_dir

    def run(self):

        test_dir = os.getcwd()
        source = self.student_dir

        try:
            for f in self.required_files:
                shutil.copy((os.path.join(source, f)), test_dir)
        except Exception as e:
            self.error = "There was an error: {0}".format(e)
            raise ErrorExeption (self.error)

        try:
            for f in self.nonessential_files or []: #if non essential files dont exist, then empty list []
                shutil.copy((os.path.join(source, f)), test_dir)
        except Exception as e:
            pass





class ActionRunner(ActionsBase):

    def __init__(self, timeout=10, timeout_error= "Time limit exceeded.", memlimit=1024, memlimit_error="Memory limit exceeded"):
        self.actionList = []
        self.timeout = timeout
        self.timeout_error = timeout_error
        self.memlimit = memlimit
        self.memlimit_error = memlimit_error

        self.student_dir = sys.argv[1]

    def files_exist(self, required_files, error='Fatal Error! {0} does not exist!', warning='Warning: {0} does not exist', nonessential_files=None):
        self.actionList.append(FilesExist(self.student_dir, required_files, nonessential_files, error, warning))

    def copy_files(self, required_files, nonessential_files=None):
        self.actionList.append(CopyFiles(self.student_dir, required_files, nonessential_files))

    def run_command(self,  command, bad_output=None, error='Your code does not compile correctly with my tests:\n\n{0}'):
        self.actionList.append(runCommad(command, bad_output, error))

    def run(self, success='All tests passed!'):
        try:
            for action in self.actionList:
                action.run()  #perform action
        except Exception as e:
            error = "There was an error: {0}".format(e)
            print (error)

        print (success)