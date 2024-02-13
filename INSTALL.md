# Installation

## Development Environment Deployment

- Clone git repo `git clone https://github.com/qgis/QGIS-Django.git`
- Run `$ pwd` in order to get your current directory
- Path to your repo should be `<your current directory>/QGIS-Django `
- Go to dockerize directory `cd QGIS-Django/dockerize`

- Build and spin container
```bash
$ make build
$ make web
$ make devweb
```

- Run migrate
```bash
$ make migrate
```

If you have a backup, you can restore it:

```bash
make dbrestore
```

otherwise, you can seed initial data from fixtures:
```
make dbseed
```

- Set up python interpreter in PyCharm or just runserver from devweb container:
```bash
$ make devweb-runserver
```
and now, you can see your site at `http://0.0.0.0:62202` (skip this step if you are using PyCharm interpreter)

- If 'None' appears in the search results, it indicates a misalignment between the search index and the database. This discrepancy often arises when a plugin is deleted from the model but persists in the search index. To rectify this issue, it is essential to synchronize the search index with the database by rebuilding it. Execute the following command to initiate the rebuilding process:

```bash
$ make rebuild_index
```
This command ensures that the search index accurately reflects the current state of the database, resolving the presence of 'None' in the search results. Automatic synchronization is currently managed in settings.py: `HAYSTACK_SIGNAL_PROCESSOR = "haystack.signals.RealtimeSignalProcessor"`.

---

### Setup git-hooks and local linting

In the root directory of the repo, run:

```bash
pip install -r REQUIREMENTS-dev.txt

pre-commit install --config .pre-commit-config.yaml
```

---

### Setting up a remote interpreter in PyCharm

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


#### In settings, django support:

- Language & Framework -> Django
- tick to Enable Django Support.
- Django project root: ``<path to your repo>/qgis_app``
- Settings: setting_docker.py
- Click the Apply button

#### Create the django run configuration

- Run -> Edit configurations
- Click the `+` icon in the top left corner
- Choose ``Django server`` from the popup list

Now set these options:

* **Name:** Django Server
* **Host:** 0.0.0.0
* **Port:** 8080
* **Additional options:** ``--settings=settings.docker``
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

---
## Setup Style Managers Group

The members of this group will receive style related emails.
Follow these steps for setting up:
- Open admin page: `http://0.0.0.0:62202/admin`, login with superuser account.
- Create new Group: `Authentication and Authorization > Groups > Add group`
- Set the options:
  - **Name:** `Style Managers`
  - **Permissions:**
    choose all styles | in **Available permissions** by typing `styles` in search input and click `Choose all`
    - styles | style | Can add style
    - styles | style | Can change style
    - styles | style | Can delete style
    - styles | style | Can view style
    - styles | style review | Can add style review
    - styles | style review | Can change style review
    - styles | style review | Can delete style review
    - styles | style review | Can view style review
    - styles | style type | Can add style type
    - styles | style type | Can change style type
    - styles | style type | Can delete style type
    - styles | style type | Can view style type

---
## Backup and Restore

- Go to repo directory and run backup.sh
```bash
$ ./backup.sh
```
- You will find dumps file in backups directory
```bash
$ tree -L 3 backups
backups
├── 2016
├── 2017
├── 2018
├── 2019
├── 2020
│   ├── April
│   │   └── PG_QGIS_PLUGINS_gis.07-April-2020.dmp
│   ├── August
│   ├── December
│   │   ├── PG_QGIS_PLUGINS_gis.01-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.02-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.03-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.04-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.05-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.06-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.07-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.08-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.09-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.10-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.11-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.12-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.13-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.14-December-2020.dmp
│   │   ├── PG_QGIS_PLUGINS_gis.15-December-2020.dmp
│   │   └── PG_QGIS_PLUGINS_gis.16-December-2020.dmp
│`
```

- Copy the dump file you wish to restore to dockerize/backups/latest.dmp file
```bash
$ cp backups/2020/December/PG_QGIS_PLUGINS_gis.16-December-2020.dmp dockerize/backups/latest.dmp
```

- Restore the dump file
```bash
$ cd dockerize
$ make dbrestore
```

---

## Email-sending setup

Create the file `settings_email.py` from the template:

```sh
cp settings_email.py.templ settings_email.py
```

Update the new file with your email settings variables:

```python title="settings_email.py"
EMAIL_HOST_PASSWORD = "your_email_app_password"
```

## Deploy Update with Rancher

- Go to [https://rancher.qgis.org](https://rancher.qgis.org)
- Click the home icon in the top left corner,  and choose the environment: `plugins.qgis.org`
- You will be redirected to User Stacks page, choose the plugins stack by clicking on `plugins` link
- Next, let's go inside the container, click on `uwsgi` link.

  ![image](https://user-images.githubusercontent.com/178003/99949715-65f55d00-2d73-11eb-929c-966a7b2877a7.png)

- In Containers tab, click on tripe-dot icon > `Execute Shell`

  ![image](https://user-images.githubusercontent.com/40058076/102454128-7352ee00-4078-11eb-80aa-f782c6ea9f6f.png)

  Now you are inside the container and ready to deploy your update.

  ![image](https://user-images.githubusercontent.com/40058076/102455185-1ce6af00-407a-11eb-8318-3e084b24c095.png)
- Pull the latest commit: `git pull origin master`
- Run migration: `python manage.py migrate`
- Run collectstatic: `python manage.py collectstatic`
- Reload uwsgi: `uwsgi --reload /tmp/django.pid`
