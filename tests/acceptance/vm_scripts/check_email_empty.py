from os import listdir


def check_email_dir():
    files = listdir('/email')
    expected = ['mysmtpd.py']
    return set(files) == set(expected)


print(check_email_dir())