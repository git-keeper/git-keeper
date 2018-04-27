from os import listdir


def check_keeper_files():
    files = listdir('/home/keeper')
    forbidden = ['faculty.csv', 'server.cfg', 'gkeepd.log', 'snapshot.json']
    return len(set(files) & set(forbidden)) is 0


print(check_keeper_files())