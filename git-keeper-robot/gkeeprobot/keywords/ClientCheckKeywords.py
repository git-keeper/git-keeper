
from gkeeprobot.control.ClientControl import ClientControl
from gkeepcore.shell_command import CommandError

client_control = ClientControl()


class ClientCheckKeywords:

    def gkeep_add_succeeds(self, faculty, class_name):
        client_control.run(faculty, 'gkeep add {} {}.csv'.format(class_name, class_name))

    def gkeep_add_fails(self, faculty, class_name):
        try:
            client_control.run(faculty, 'gkeep add {} {}.csv'.format(class_name, class_name))
            raise CommandError('gkeep add should have non-zero return')
        except CommandError:
            pass

