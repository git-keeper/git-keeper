
FROM ubuntu

# NOTE: all the following commands run as root

RUN apt-get update

# It's not installed by default any more!
RUN apt-get install -y sudo


RUN apt-get install -y openssh-server
RUN mkdir /var/run/sshd

# disallow these because older versions of paramiko don't support them
RUN sed -e '/ssh_host_ecdsa_key/ s/^#*/#/' -i /etc/ssh/sshd_config
RUN sed -e '/ssh_host_ed25519_key/ s/^#*/#/' -i /etc/ssh/sshd_config

# Set up python and the necessary libraries
RUN apt-get install python3
RUN apt-get install -y python3-pip
RUN apt-get install -y libffi-dev
RUN apt-get install -y libssl-dev
RUN pip3 install paramiko

# Useful for debugging
RUN apt-get install nano

RUN apt-get install -y git

RUN useradd -ms /bin/bash prof
RUN echo 'prof:prof' | chpasswd

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

