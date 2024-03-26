import os


class TempPaths:
    """
    Represents the various paths in a temporary testing directory.

    Attributes:

    temp_path - path to the temporary directory storing all items
    submission_path - path to the clone of the student's submission
    run_action_sh_path - path to run_action.sh that will be called ot initiate
                         tests
    assignment_cfg_path - path to assignment.cfg, which may or may not exist
    """

    def __init__(self, temp_path, assignment_name):
        self.temp_path = temp_path
        self.submission_path = os.path.join(temp_path, assignment_name)
        self.run_action_sh_path = os.path.join(temp_path, 'run_action.sh')
        self.assignment_cfg_path = os.path.join(temp_path, 'assignment.cfg')
