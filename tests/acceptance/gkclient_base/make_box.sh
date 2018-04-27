vagrant up
rm gkclient.box
vagrant package --output gkclient.box
vagrant destroy -f
