
from gkeepcore.shell_command import run_command, CommandError


def server_running():
    try:
        run_command('screen -S gkserver -Q select .')
        return 'Yes'
    except CommandError:
        return 'No'


print(server_running())