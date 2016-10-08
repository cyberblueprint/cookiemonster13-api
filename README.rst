Filtering Football Matchs
=========================

Available filters:
------------------

* date__gt: greater than
* date__gte: greater than or equeal
* date__lt: lower than
* date__lte: lower than or equal
* date__in: between in 2 dates

Examples
--------
* localhost:8001/football/?date__gt=01-12-2016
* localhost:8001/football/?date__gte=01-12-2016
* localhost:8001/football/?date__lt=06-12-2016
* localhost:8001/football/?date__lte=06-12-2016
* localhost:8001/football/?date__in=01-12-2016,10-12-2106


Getting Up and Running Locally With Docker
==========================================

.. index:: Docker

The steps below will get you up and running with a local development environment.
All of these commands assume you are in the root of your generated project.

Project will run **localhost:8001**.

Prerequisites
-------------

You'll need at least Docker 1.10.

If you don't already have it installed, follow the instructions for your OS:

 - On Mac OS X, you'll need `Docker for Mac`_
 - On Windows, you'll need `Docker for Windows`_
 - On Linux, you'll need `docker-engine`_
.. _`Docker for Mac`: https://docs.docker.com/engine/installation/mac/
.. _`Docker for Windows`: https://docs.docker.com/engine/installation/windows/
.. _`docker-engine`: https://docs.docker.com/engine/installation/

Install Docker, docker-compose for Linux
----------------------------------------

* wget -qO- https://get.docker.com/ | sh
* sudo usermod -aG docker $(whoami)
* sudo pip install docker-compose

Build the Stack
---------------

This can take a while, especially the first time you run this particular command
on your development system::

    $ docker-compose -f dev.yml build

If you want to build the production environment you don't have to pass an argument -f, it will automatically use docker-compose.yml. Also check **Deployment with Docker**

Boot the System
---------------

This brings up both Django and PostgreSQL.

The first time it is run it might take a while to get started, but subsequent
runs will occur quickly.

Open a terminal at the project root and run the following for local development::

    $ docker-compose -f dev.yml up

You can also set the environment variable ``COMPOSE_FILE`` pointing to ``dev.yml`` like this::

    $ export COMPOSE_FILE=dev.yml

And then run::

    $ docker-compose up

Running management commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~

As with any shell command that we wish to run in our container, this is done
using the ``docker-compose run`` command.

To migrate your app and to create a superuser, run::

    $ docker-compose -f dev.yml run django python manage.py migrate
    $ docker-compose -f dev.yml run django python manage.py createsuperuser

Here we specify the ``django`` container as the location to run our management commands.

Production Mode
~~~~~~~~~~~~~~~

Instead of using `dev.yml`, you would use `docker-compose.yml`.

Other Useful Tips
-----------------

Make a machine the active unit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tells our computer that all future commands are specifically for the dev1 machine.
Using the ``eval`` command we can switch machines as needed.

::

    $ eval "$(docker-machine env dev1)"

Detached Mode
~~~~~~~~~~~~~

If you want to run the stack in detached mode (in the background), use the ``-d`` argument:

::

    $ docker-compose -f dev.yml up -d

Debugging
~~~~~~~~~~~~~

ipdb
"""""

If you are using the following within your code to debug:

::

    import ipdb; ipdb.set_trace()

Then you may need to run the following for it to work as desired:

::

    $ docker-compose run -f dev.yml --service-ports django


django-debug-toolbar
""""""""""""""""""""

In order for django-debug-toolbar to work with docker you need to add your docker-machine ip address (the output of `Get the IP ADDRESS`_) to INTERNAL_IPS in local.py


Deployment with Docker (Production)
===================================

.. index:: Docker, deployment

Prerequisites
-------------

* Docker (at least 1.10)
* Docker Compose (at least 1.6)

Understand the Compose Setup
--------------------------------

Before you start, check out the `docker-compose.yml` file in the root of this project. This is where each component
of this application gets its configuration from. Notice how it provides configuration for these services:

* `postgres` service that runs the database
* `redis` for caching
* `nginx` as reverse proxy
* `django` is the Django project run by gunicorn

If you chose the `use_celery` option, there are two more services:

* `celeryworker` which runs the celery worker process
* `celerybeat` which runs the celery beat process

If you chose the `use_letsencrypt` option, you also have:

* `certbot` which keeps your certs from letsencrypt up-to-date

Populate .env With Your Environment Variables
---------------------------------------------

Some of these services rely on environment variables set by you. There is an `env.example` file in the
root directory of this project as a starting point. Add your own variables to the file and rename it to `.env`. This
file won't be tracked by git by default so you'll have to make sure to use some other mechanism to copy your secret if
you are relying solely on git.

Optional: nginx-proxy Setup
---------------------------

By default, the application is configured to listen on all interfaces on port 80. If you want to change that, open the
`docker-compose.yml` file and replace `0.0.0.0` with your own ip.

If you are using `nginx-proxy`_ to run multiple application stacks on one host, remove the port setting entirely and add `VIRTUAL_HOST=example.com` to your env file. Here, replace example.com with the value you entered for `domain_name`.

This pass all incoming requests on `nginx-proxy`_ to the nginx service your application is using.

.. _nginx-proxy: https://github.com/jwilder/nginx-proxy

Optional: Postgres Data Volume Modifications
---------------------------------------------

Postgres is saving its database files to the `postgres_data` volume by default. Change that if you wan't
something else and make sure to make backups since this is not done automatically.

Optional: Certbot and Let's Encrypt Setup
------------------------------------------

If you chose `use_letsencrypt` and will be using certbot for https, you must do the following before running anything with docker-compose:

Replace dhparam.pem.example with a generated dhparams.pem file before running anything with docker-compose. You can generate this on ubuntu or OS X by running the following in the project root:

::

    $ openssl dhparam -out /path/to/project/compose/nginx/dhparams.pem 2048

If you would like to add additional subdomains to your certificate, you must add additional parameters to the certbot command in the `docker-compose.yml` file:

Replace:

::

    command: bash -c "sleep 6 && certbot certonly -n --standalone -d {{ cookiecutter.domain_name }} --text --agree-tos --email mjsisley@relawgo.com --server https://acme-v01.api.letsencrypt.org/directory --rsa-key-size 4096 --verbose --keep-until-expiring --standalone-supported-challenges http-01"

With:

::

    command: bash -c "sleep 6 && certbot certonly -n --standalone -d {{ cookiecutter.domain_name }} -d www.{{ cookiecutter.domain_name }} -d etc.{{ cookiecutter.domain_name }} --text --agree-tos --email {{ cookiecutter.email }} --server https://acme-v01.api.letsencrypt.org/directory --rsa-key-size 4096 --verbose --keep-until-expiring --standalone-supported-challenges http-01"

Please be cognizant of Certbot/Letsencrypt certificate requests limits when getting this set up. The provide a test server that does not count against the limit while you are getting set up.

The certbot certificates expire after 3 months.
If you would like to set up autorenewal of your certificates, the following commands can be put into a bash script:

::

    #!/bin/bash
    cd <project directory>
    docker-compose run --rm --name certbot certbot bash -c "sleep 6 && certbot certonly --standalone -d {{ cookiecutter.domain_name }} --text --agree-tos --email {{ cookiecutter.email }} --server https://acme-v01.api.letsencrypt.org/directory --rsa-key-size 4096 --verbose --keep-until-expiring --standalone-supported-challenges http-01"
    docker exec pearl_nginx_1 nginx -s reload

And then set a cronjob by running `crontab -e` and placing in it (period can be adjusted as desired)::

    0 4 * * 1 /path/to/bashscript/renew_certbot.sh

Run your app with docker-compose
--------------------------------

To get started, pull your code from source control (don't forget the `.env` file) and change to your projects root
directory.

You'll need to build the stack first. To do that, run::

    docker-compose build

Once this is ready, you can run it with::

    docker-compose up

To run a migration, open up a second terminal and run::

   docker-compose run django python manage.py migrate

To create a superuser, run::

   docker-compose run django python manage.py createsuperuser

If you need a shell, run::

   docker-compose run django python manage.py shell

To get an output of all running containers.

To check your logs, run::

   docker-compose logs

If you want to scale your application, run::

   docker-compose scale django=4
   docker-compose scale celeryworker=2

.. warning:: Don't run the scale command on postgres, celerybeat, certbot, or nginx.

If you have errors, you can always check your stack with `docker-compose`. Switch to your projects root directory and run::

    docker-compose ps


Supervisor Example
-------------------

Once you are ready with your initial setup, you wan't to make sure that your application is run by a process manager to
survive reboots and auto restarts in case of an error. You can use the process manager you are most familiar with. All
it needs to do is to run `docker-compose up` in your projects root directory.

If you are using `supervisor`, you can use this file as a starting point::

    [program:{{project_slug}}]
    command=docker-compose up
    directory=/path/to/project
    redirect_stderr=true
    autostart=true
    autorestart=true
    priority=10

Place it in `/etc/supervisor/conf.d/{{project_slug}}.conf` and run::

    supervisorctl reread
    supervisorctl start {{project_slug}}

To get the status, run::

    supervisorctl status


============================
Database Backups with Docker
============================

The database has to be running to create/restore a backup. These examples show local examples. If you want to use it on a remote server, remove ``-f dev.yml`` from each example.

Running Backups
================

Run the app with `docker-compose -f dev.yml up`.

To create a backup, run::

    docker-compose -f dev.yml run postgres backup


To list backups, run::

    docker-compose -f dev.yml run postgres list-backups


To restore a backup, run::

    docker-compose -f dev.yml run postgres restore filename.sql

Where <containerId> is the ID of the Postgres container. To get it, run::

    docker ps

To copy the files from the running Postgres container to the host system::

    docker cp <containerId>:/backups /host/path/target

Restoring From Backups
======================

To restore the production database to a local PostgreSQL database::

    createdb NAME_OF_DATABASE
    psql NAME_OF_DATABASE < NAME_OF_BACKUP_FILE

