#!/bin/bash

sudo mkdir /home/$1/.ssh
sudo chown $1 /home/$1/.ssh
sudo chgrp $1 /home/$1/.ssh
sudo -u $1 ssh-keygen -t rsa -N "" -f /home/$1/.ssh/id_rsa
sudo cp /home/$1/.ssh/id_rsa.pub /vagrant/$2/$1_rsa.pub
sudo cp /home/$1/.ssh/id_rsa /vagrant/$2/$1_rsa
sudo cp /home/$1/.ssh/id_rsa.pub /home/$1/.ssh/authorized_keys
sudo sh -c "echo 'Host gkserver' >> /home/$1/.ssh/config"
sudo sh -c "echo 'StrictHostKeyChecking no' >> /home/$1/.ssh/config"
sudo sh -c "echo 'UserKnownHostsFile /dev/null' >> /home/$1/.ssh/config"
sudo sh -c "echo 'LogLevel=ERROR' >> /home/$1/.ssh/config"
sudo chown -R $1 /home/$1/.ssh/
sudo chgrp -R $1 /home/$1/.ssh/
sudo chmod 600 /home/$1/.ssh/*
