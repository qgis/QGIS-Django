## Development Environment Deployment

- Clone git repo `git clone https://github.com/qgis/QGIS-Django.git`
> run `$ pwd` in order to get your current directory
>
>your repo path should be `<your current directory>/QGIS-Django `
- Go to dockerize directory
`$ cd QGIS-Django/dockerize`

- Build and spin docker-compose
```
$ docker-compose build
$ docker-compose up -d
```

- Run migrate in web container
`docker-compose exec web python manage.py migrate`

- Set up python interpreter in PyCharm or just runserver from devweb container:
`$ docker-compose exec devweb python manage.py runserver 0.0.0.0:8080`
and now, you can see your site at `http://0.0.0.0:62202`

---

### Setting up a remote interpreter in pycharm
- PyCharm -> Preferences -> Project: QGIS-Django
- Click on the gear icon next to project interpreter -> add
- SSH Interpreter -> New server configuration
- Host : `localhost`
- Port : `62203`
- Username: `root`
- Click next button
- Auth type: password (and tick 'save password')
- Click next button
- password : `docker`
- Interpreter : ``/usr/local/bin/python``
- Sync folders -> click on the folder icon
  - local : `<path to your repo>/dockerize/qgis-app`
  - remote : `/home/web/django_project`
  After that you should see something like this in sync folder:
   `<Project root>/django_project→/home/web/django_project`
- Automatically upload project files to the server -> untick the checkbox to avoid overwriting in your files.
- Click the Apply button


### In settings, django support:

- Language & Framework -> Django
- tick to Enable Django Support.
- Django project root: ``<path to your repo>/qgis_app``
- Settings: setting_docker.py
- Click the Apply button


### Create the django run configuration

- Run -> Edit configurations
- Click the `+` icon in the top left corner
- Choose ``Django server`` from the popup list

Now set these options:

* **Name:** Django Server
* **Host:** 0.0.0.0
* **Port:** 8080
* **Additional options:** ``--settings=settings._docker``
* **Run browser** If checked, it will open the url after you click run. You should be able to access the running on 0.0.0.0:62202 (the port that mapped to 8080)

* **Environment vars** , you can add the variables value one-by-one by clicking on browse icon at right corner in the input field, or just copy-paste this value:
`PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=settings_docker;RABBITMQ_HOST=rabbitmq;DATABASE_NAME=gis;DATABASE_USERNAME=docker;DATABASE_PASSWORD=docker;DATABASE_HOST=db`
* **Python interpreter:** Ensure it is set you your remote interpreter (should be
  set to that by default)

* **Path mappings:** Here you need to indicate path equivalency between your host
  filesystem and the filesystem in the remote (docker) host. Click the ellipsis
  and add a run that points to your git checkout on your local host and the
  /home/web directory in the docker host. e.g.
  * **Local path:** <path to your git repo>/QGIS-Django/qgis-app
  * **Remote path:** /home/web/django_project
* click OK to save your run configuration

Now you can run the server using the green triangle next to the Django server
label in the run configurations pull down. Debug will also work and you will be
able to step through views etc as you work.