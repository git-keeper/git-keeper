
from gkeeprobot.control.VagrantControl import VagrantControl
from gkeeprobot.keywords.ServerSetupKeywords import ServerSetupKeywords
from gkeeprobot.keywords.ClientSetupKeywords import ClientSetupKeywords

vagrant = VagrantControl()
server = ServerSetupKeywords()
client = ClientSetupKeywords()

print('Checking that gkserver is running...')
if not vagrant.is_server_running():
    print("Server not running!")
    exit(1)

print('Checking that gkclient is running')
if not vagrant.is_client_running():
    print("Client not running!")
    exit(1)

# This also stops gkeepd
print("Resetting server...")
server.reset_server()
print('Resetting client...')
client.reset_client()

