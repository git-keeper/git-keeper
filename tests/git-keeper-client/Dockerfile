
FROM ubuntu

# NOTE: all the following commands run as root

RUN apt-get update

RUN apt-get install -y ssh

# Set up python and the necessary libraries
RUN apt-get install python3
RUN apt-get install -y python3-pip
RUN apt-get install -y libffi-dev
RUN apt-get install -y libssl-dev
RUN pip3 install paramiko

RUN apt-get install -y git

RUN useradd -ms /bin/bash prof
RUN echo 'prof:prof' | chpasswd

EXPOSE 22
