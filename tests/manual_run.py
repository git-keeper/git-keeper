
from tests.docker_gkeepserver import start_docker_gkeepserver, stop_docker_gkeepserver

print("Starting server")
start_docker_gkeepserver(debug_output=True)

input("\n\nServer running.  Hit return to stop it.")

stop_docker_gkeepserver(debug_output=True)


