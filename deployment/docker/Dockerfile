#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
# Note this base image is based on debian
FROM kartoza/django-base
MAINTAINER Tim Sutton<tim@kartoza.com>

#RUN  ln -s /bin/true /sbin/initctl

# Use local cached debs from host (saves your bandwidth!)
# Change ip below to that of your apt-cacher-ng host
# Or comment this line out if you do not with to use caching
ADD 71-apt-cacher-ng /etc/apt/apt.conf.d/71-apt-cacher-ng


# Pandoc needed to generate rst dumps
RUN apt-get update -y; apt-get -y --force-yes install yui-compressor pandoc
RUN apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev

ADD REQUIREMENTS.txt /REQUIREMENTS.txt
RUN pip install -r /REQUIREMENTS.txt
RUN pip install uwsgi


# Open port 8080 as we will be running our uwsgi socket on that
EXPOSE 8080

WORKDIR /home/web/django_project
CMD ["uwsgi", "--ini", "/uwsgi.conf"]
