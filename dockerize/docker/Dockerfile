# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim as prod

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    git python3-dev libxml2-dev \
    libsasl2-dev libldap2-dev libssl-dev \
    libxslt1-dev zlib1g-dev \
    build-essential \
    libffi-dev \
    libjpeg-dev libpq-dev \
    liblcms2-dev libblas-dev libatlas-base-dev

RUN rm -rf /uwsgi.conf
ADD dockerize/docker/uwsgi.conf /uwsgi.conf
ADD qgis-app /home/web/django_project
ADD dockerize/docker/REQUIREMENTS.txt /REQUIREMENTS.txt

RUN pip install --upgrade pip && pip install -r /REQUIREMENTS.txt

RUN apt-get update && apt-get install -y gdal-bin

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
