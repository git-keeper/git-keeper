# Copyright 2018 Nathan Sommer and Ben Coleman
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


from gkeeprobot.control.ClientControl import ClientControl
from gkeeprobot.control.ServerControl import ServerControl
from gkeeprobot.control.VMControl import ExitCodeException
from gkeeprobot.exceptions import GkeepRobotException

"""Provides keywords for robotframework to configure faculty and student
accounts before testing begins."""

client_control = ClientControl()
server_control = ServerControl()


class ClientSetupKeywords:

    def create_account(self, name):
        client_control.run_vm_bash_script('keeper',
                                          'make_user_with_password.sh',
                                          name)

    def establish_ssh_keys(self, name):
        temp_dir_name = client_control.vm_control.temp_dir.name
        client_control.run_vm_bash_script('keeper',
                                          'make_ssh_keys.sh',
                                          name,
                                          temp_dir_name)
        server_control.run_vm_bash_script('keeper',
                                          'make_authorized_keys.sh',
                                          name,
                                          temp_dir_name)

    def create_git_config(self, username):
        name_cmd = 'git config --global user.name "{}"'.format(username)
        client_control.run(username, name_cmd)
        email_cmd = 'git config --global user.email {}@school.edu'.format(username)
        client_control.run(username, email_cmd)

    def add_to_class_csv(self, faculty, class_name, username, last_name='Last',
                         first_name='First', email_domain='school.edu'):
        line = '{},{},{}@{}'.format(last_name, first_name, username,
                                    email_domain)
        client_control.run_vm_python_script(faculty, 'add_to_file.py',
                                            '{}.csv'.format(class_name), line)

    def remove_from_class(self, faculty, class_name, student):
        cmd = 'sed -i /{}/d {}.csv'.format(student, class_name)
        client_control.run(faculty, cmd)

    def add_file_to_client(self, username, filename, target_filename):
        client_control.copy(username, filename, target_filename)

    def delete_file_on_client(self, username, filename):
        cmd = 'rm {}'.format(filename)
        client_control.run(username, cmd)

    def make_empty_file(self, username, filename):
        client_control.run(username, 'touch {}'.format(filename))

    def make_empty_directory(self, username, directory_name):
        client_control.run(username, 'mkdir -p {}'.format(directory_name))

    def create_gkeep_config_file(self, faculty):
        client_control.run_vm_bash_script(faculty, 'make_gkeep_config.sh',
                                          faculty)

    def run_gkeep_command(self, faculty, *command):
        cmd = 'gkeep ' + ' '.join(command)
        client_control.run(faculty, cmd)

    def reset_client(self):
        client_control.close_user_connections()
        client_control.run_vm_python_script('keeper', 'reset_client.py')

    def add_assignment_to_client(self, faculty, assignment_name):
        cmd = 'cp -r /vagrant/assignments/{}/ ~'.format(assignment_name)
        client_control.run(faculty, cmd)

    def clone_assignment(self, student, faculty, class_name, assignment_name):
        client_control.run(student, 'mkdir -p assignments/{}'.format(class_name))
        url = '{}@gkserver:/home/{}/{}/{}/{}.git'.format(student, student, faculty, class_name, assignment_name)
        command = 'git clone {} assignments/{}/{}'.format(url, class_name, assignment_name)
        client_control.run(student, command)

    def student_submits(self, student, faculty, class_name, assignment_name,
                        solution_folder, expect_failure=False, branch=None):
        assignment_folder = '~/assignments/{}/{}'.format(class_name,
                                                         assignment_name)
        cp_cmd = ('cp /vagrant/assignments/{}/{}/* {}'
                  .format(assignment_name, solution_folder, assignment_folder))
        client_control.run(student, cp_cmd)

        if branch is not None:
            new_branch_cmd = ('cd {}; git checkout -b {}'
                              .format(assignment_folder, branch))
            client_control.run(student, new_branch_cmd)

        commit_cmd = 'cd {}; git commit -am "done"'.format(assignment_folder)
        client_control.run(student, commit_cmd)

        if branch is None:
            push_cmd = 'cd {}; git push'.format(assignment_folder)
        else:
            push_cmd = 'cd {}; git push origin {}'.format(assignment_folder,
                                                          branch)

        try:
            client_control.run(student, push_cmd)
            if expect_failure:
                raise GkeepRobotException('Expected push to have a non-zero '
                                          'exit code')
        except ExitCodeException as e:
            if not expect_failure:
                raise e

    def fetch_assignment(self, faculty, class_name, assignment_name, target_dir=None):
        if target_dir is not None:
            folder_name = '{}/{}'.format(target_dir, class_name)
            cmd = 'yes | gkeep fetch {} {} {}'.format(class_name, assignment_name, folder_name)
        else:
            # Yes to force directories to be created
            cmd = 'yes | gkeep fetch {} {}'.format(class_name, assignment_name)
        client_control.run(faculty, cmd)

    def add_submissions_folder_to_config(self, faculty, directory):
        client_control.run(faculty, 'echo [local] >> .config/git-keeper/client.cfg')
        client_control.run(faculty, 'echo submissions_path={} >> .config/git-keeper/client.cfg'.format(directory))

    def add_templates_folder_to_config(self, faculty, directory):
        client_control.run(faculty, 'echo [local] >> .config/git-keeper/client.cfg')
        client_control.run(faculty, 'echo templates_path={} >> .config/git-keeper/client.cfg'.format(directory))

    def add_assignment_template(self, faculty, source_name, destination_name, template_dir=None):
        if template_dir is None:
            template_dir = '~/.config/git-keeper/templates'

        cmd = 'mkdir -p {}'.format(template_dir)
        client_control.run(faculty, cmd)
        cmd = 'cp -r /vagrant/templates/{} {}/{}'.format(source_name, template_dir, destination_name)
        client_control.run(faculty, cmd)
