
FROM ubuntu

RUN apt-get update && apt-get install -y \
    sudo \
    openssh-server \
    python3 \
    python3-pip \
    libffi-dev \
    libssl-dev \
    nano \
    git \
    expect

RUN pip3 install paramiko

RUN mkdir /var/run/sshd

# disallow these because older versions of paramiko don't support them
RUN sed -e '/ssh_host_ecdsa_key/ s/^#*/#/' -i /etc/ssh/sshd_config
RUN sed -e '/ssh_host_ed25519_key/ s/^#*/#/' -i /etc/ssh/sshd_config

RUN useradd -ms /bin/bash prof
RUN echo 'prof:prof' | chpasswd

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

