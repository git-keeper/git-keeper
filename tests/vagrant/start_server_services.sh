#!/usr/bin/env bash

mkdir email
sudo python3 mysmtpd.py 25 email &
gkeepd &
