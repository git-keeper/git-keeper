#!/bin/bash

sudo useradd -ms /bin/bash $1
echo "$1:$1" | sudo chpasswd
