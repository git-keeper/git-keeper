
import sys
import pwd


def user_exists(user):
    try:
        pwd.getpwnam(user)
        return 'Yes'
    except:
        return 'No'


print(user_exists(sys.argv[1]))
