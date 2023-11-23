#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
# Note this base image is based on debian
FROM kartoza/django-base:3.7 as prod
MAINTAINER Dimas Ciputra<dimas@kartoza.com>

#RUN  ln -s /bin/true /sbin/initctl
RUN apt-get clean all

# Debian stretch/updates release issue. please see https://serverfault.com/a/1130167
RUN echo "deb http://archive.debian.org/debian stretch main contrib non-free" > /etc/apt/sources.list

RUN apt-get update && apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev

RUN rm -rf /uwsgi.conf
ADD dockerize/docker/uwsgi.conf /uwsgi.conf
ADD qgis-app /home/web/django_project
ADD dockerize/docker/REQUIREMENTS.txt /REQUIREMENTS.txt
RUN pip install --upgrade pip && pip install -r /REQUIREMENTS.txt
RUN pip install uwsgi

# Open port 8080 as we will be running our uwsgi socket on that
EXPOSE 8080

RUN mkdir -p /var/log/uwsgi

WORKDIR /home/web/django_project
CMD ["uwsgi", "--ini", "/uwsgi.conf"]


FROM prod as dev

# This section taken on 2 July 2015 from
# https://docs.docker.com/examples/running_ssh_service/
# Sudo is needed by pycharm when it tries to pip install packages
RUN apt-get update && apt-get install -y openssh-server sudo
RUN mkdir /var/run/sshd
RUN echo 'root:docker' | chpasswd
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

# Install freezegun for feedback test
RUN pip install freezegun

# --------------------------------------------------------
# Open ports as needed
# --------------------------------------------------------

# Open port 8080 as we will be running our django dev server on
EXPOSE 8080
# Open port 22 as we will be using a remote interpreter from pycharm
EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
