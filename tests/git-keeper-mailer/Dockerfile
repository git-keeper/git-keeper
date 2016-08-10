FROM ubuntu

RUN apt-get update && \
    apt-get -y install  python3

RUN mkdir /email

ADD ./mysmtpd.py /usr/bin
RUN chmod +x /usr/bin/mysmtpd.py

EXPOSE 25
CMD ["/usr/bin/mysmtpd.py", "25", "/email"]
