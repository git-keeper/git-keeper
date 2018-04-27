#!/bin/bash
mkdir -p .config/git-keeper
cat > .config/git-keeper/client.cfg <<EOL
[server]
host = gkserver
username = $1
EOL