
FROM ubuntu

# This file is based on the Dockerfile at
# https://github.com/jpetazzo/dind
# and is protected under the Apache 2.0 license.

# NOTE: all the following commands run as root

RUN apt-get update

# The following taken from the "Docker in Docker (dind)" Dockerfile
# See https://github.com/jpetazzo/dind
RUN apt-get install -qqy \
    apt-transport-https \
    ca-certificates \
    curl \
    lxc \
    iptables

# Install Docker from Docker Inc. repositories.
RUN curl -sSL https://get.docker.com/ | sh

# Install the magic wrapper.
ADD ./wrapdocker /usr/local/bin/wrapdocker
RUN chmod +x /usr/local/bin/wrapdocker

# Define additional metadata for our image.
VOLUME /var/lib/docker


RUN apt-get install -y openssh-server
RUN mkdir /var/run/sshd

# Set up python and the necessary libraries
RUN apt-get install python3
RUN apt-get install -y python3-pip
RUN apt-get install -y libffi-dev
RUN apt-get install -y libssl-dev
RUN pip3 install paramiko
RUN pip3 install pyinotify

# It's not installed by default any more!
RUN apt-get install -y sudo

# Set up git - it is a git-based application, after all!
RUN apt-get install -y git

# Create the gitkeeper group and the main gitkeeper account in that group
RUN groupadd gitkeeper
RUN useradd -ms /bin/bash keeper
RUN usermod -a -G keeper keeper
# keeper must be in the docker group to be able to run docker commands
RUN usermod -aG docker keeper
RUN echo "keeper ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo 'keeper:g1tk33p3r' | chpasswd

# Create a dummy student account
RUN useradd -ms /bin/bash student
RUN echo 'student:student' | chpasswd

RUN chown student:keeper /home/student
RUN chmod 770 /home/student

ADD ./ssh_server /etc/ssh
RUN chmod 600 /etc/ssh/*_key

# Since we are adding the /etc/ssh folder, we already did this in those local files
# Disallow ssh connections unless they are RSA/DSA
#RUN sed -e '/ssh_host_ecdsa_key/ s/^#*/#/' -i /etc/ssh/sshd_config
#RUN sed -e '/ssh_host_ed25519_key/ s/^#*/#/' -i /etc/ssh/sshd_config

# This will run the docker command and then all the sshd command to run
ENTRYPOINT ["wrapdocker"]

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
