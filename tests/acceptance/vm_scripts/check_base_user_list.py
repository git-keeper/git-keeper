from os import listdir


def check_users():
    users = listdir('/home')
    expected = ['keeper', 'vagrant', 'ubuntu']
    return set(users) == set(expected)


print(check_users())