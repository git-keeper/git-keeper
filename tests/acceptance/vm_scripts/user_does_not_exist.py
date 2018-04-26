
from gkeeprobot.dectorators import polling
import sys
import pwd


@polling
def user_does_not_exist(user):
    try:
        pwd.getpwnam(user)
        return False
    except:
        return True


print(user_does_not_exist(sys.argv[1]))
