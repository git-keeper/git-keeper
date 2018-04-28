import os
from gkeepcore.shell_command import run_command


def remove_users():
    # remove everyone but vagrant, ubuntu, and keeper
    expected = ['keeper', 'vagrant', 'ubuntu']

    for user in os.listdir('/home'):
        if user not in expected:
            run_command('sudo userdel -r {}'.format(user))

remove_users()