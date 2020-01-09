#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
# Note this base image is based on debian
FROM kartoza/django-base:3.7
MAINTAINER Dimas Ciputra<dimas@kartoza.com>

#RUN  ln -s /bin/true /sbin/initctl
RUN apt-get update && apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev
ADD REQUIREMENTS.txt /REQUIREMENTS.txt
RUN pip install -r /REQUIREMENTS.txt
RUN pip install uwsgi

# https://docs.docker.com/examples/running_ssh_service/
# Sudo is needed by pycharm when it tries to pip install packages
RUN apt-get install -y openssh-server sudo
RUN mkdir /var/run/sshd
RUN echo 'root:docker' | chpasswd
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

RUN rm -rf /uwsgi.conf
ADD uwsgi.conf /uwsgi.conf

# Open port 8080 as we will be running our uwsgi socket on that
EXPOSE 8080

# Open port 22 as we will be using a remote interpreter from pycharm
EXPOSE 22

RUN mkdir -p /var/log/uwsgi
WORKDIR /home/web/django_project
CMD ["/usr/sbin/sshd", "-D"]
