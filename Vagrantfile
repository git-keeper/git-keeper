
Vagrant.configure("2") do |config|

    config.vm.define "gkserver" do |gkserver|
        gkserver.vm.box = "git-keeper/gkserver"
        gkserver.vm.hostname = "gkserver"
        gkserver.vm.provision "shell", path: "vagrant-files/server-provision.sh"
        gkserver.vm.synced_folder "vagrant-files/email/", "/email/"
        gkserver.vm.synced_folder "vagrant-files/keeper-home/", "/home/keeper/"
        gkserver.ssh.username = "keeper"
        gkserver.ssh.password = "g1tk33p3r"
    end

    #config.vm.define "gkclient" do |gkclient|
    #    gkclient.vm.box = "ubuntu/trusty64"
    #end
end