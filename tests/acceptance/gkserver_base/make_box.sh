vagrant up
rm gkserver.box
vagrant package --output gkserver.box
vagrant destroy -f
