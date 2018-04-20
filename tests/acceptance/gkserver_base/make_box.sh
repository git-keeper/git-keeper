#/bin/bash

vagrant up
echo 'Optimizing image...'
vagrant ssh -- sudo dd if=/dev/zero of=/EMPTY bs=1M
vagrant ssh -- sudo rm -f /EMPTY
rm gkserver.box
vagrant package --output gkserver.box
vagrant destroy -f
