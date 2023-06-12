#!/usr/bin/env python3
from subprocess import check_call

from livereload import Server, shell

BUILD_DIR = "/tmp/_build"

# initial make
check_call(["make", "build", f"BUILD_DIR={BUILD_DIR}"])

server = Server()
server.watch("..", shell(f"make build BUILD_DIR={BUILD_DIR}"))
server.serve(root=BUILD_DIR, liveport=35730, port=8001, host="0.0.0.0")
