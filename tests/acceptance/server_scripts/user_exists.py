
import sys
import pwd


def user_exists(user):
    try:
        pwd.getpwnam(user)
        return True
    except:
        return False


print(user_exists(sys.argv[1]))
