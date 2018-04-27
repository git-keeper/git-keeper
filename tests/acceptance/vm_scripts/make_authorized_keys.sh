#!/bin/bash

sudo mkdir /home/$1/.ssh
sudo cp /vagrant/$2/$1_rsa.pub /home/$1/.ssh/authorized_keys
sudo chown -R $1 /home/$1/.ssh
sudo chgrp -R $1 /home/$1/.ssh
sudo chmod -R 600 /home/$1/.ssh/*
