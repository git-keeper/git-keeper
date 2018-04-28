
from gkeepcore.shell_command import run_command, CommandError
import os


def server_running():
    try:
        run_command('screen -S gkserver -Q select .')
        return True
    except CommandError:
        return False


def stop_gkeepd():
    if server_running():
        run_command('screen -S gkserver -X quit')


def remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def remove_gkeepd_files():
    # remove gkeepd.log, snapshot.json, server.cfg, and faculty.csv
    remove('gkeepd.log')
    remove('snapshot.json')
    remove('server.cfg')
    remove('faculty.csv')


def delete_email():
    # delete all files except mysmtpd.py
    run_command('sudo find /email ! -name "mysmtpd.py" -type f -exec rm -f {} +')


def remove_users():
    # remove everyone but vagrant, ubuntu, and keeper
    expected = ['keeper', 'vagrant', 'ubuntu']

    for user in os.listdir('/home'):
        if user not in expected:
            run_command('sudo userdel -r {}'.format(user))


stop_gkeepd()
remove_gkeepd_files()
delete_email()
remove_users()