vagrant up
echo 'Optimizing image...'
vagrant ssh -- sudo dd if=/dev/zero of=/EMPTY bs=1M
vagrant ssh -- sudo rm -f /EMPTY
rm gkclient.box
vagrant package --output gkclient.box
vagrant destroy -f
