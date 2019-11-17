
pip3 install -e /vagrant/git-keeper-core
pip3 install -e /vagrant/git-keeper-server
python3 /email/mysmtpd.py 25 /email &
su - keeper -c "nohup gkeepd &"