import time


def polling(func):
    def polling_wrapper(*args, **kwargs):
        for count in range(10):
            if func(*args, **kwargs):
                return True
            time.sleep(.1)
        return False
    return polling_wrapper
