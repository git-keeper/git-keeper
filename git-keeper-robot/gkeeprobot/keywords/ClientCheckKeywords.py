
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

    def gkeep_modify_succeeds(self, faculty, class_name):
        client_control.run(faculty, 'gkeep modify {} {}.csv'.format(class_name, class_name))

    def gkeep_modify_fails(self, faculty, class_name):
        try:
            client_control.run(faculty, 'gkeep modify {} {}.csv'.format(class_name, class_name))
            raise CommandError('gkeep modify should have non-zero return')
        except CommandError:
            pass

    def gkeep_query_contains(self, faculty, sub_command, *expected_strings):
        results = client_control.run(faculty, 'gkeep query {}'.format(sub_command))
        for expected in expected_strings:
            assert expected in results