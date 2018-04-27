from gkeepcore.shell_command import run_command, CommandError


def check_sudo():
    try:
        run_command('sudo -nv')
        return True
    except CommandError:
        return False


print(check_sudo())