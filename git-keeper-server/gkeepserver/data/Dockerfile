FROM ubuntu

RUN apt-get update && apt-get install -y \
    sudo \
    python3 \
    python3-pip \
    nano \
    git \
    expect

ADD ./go /go
RUN chmod +x /go