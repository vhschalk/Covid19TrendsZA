# Covid19 Trends ZA Dashboard Project

## Introduction

This is a Covid-19 analytics dashboard for South Africa. The focus is on the Effective Reproduction Number (Rt).

This project was inspired by analytics on USA data, [Rt.live](https://rt.live). The South African model was refined by the [Data Science for Social Impact research group](https://github.com/dsfsi/covid19za/blob/master/notebooks/covid-model/rtlive-model-za.ipynb) (DFSI).

The dashboard is build with Django. The analytics engine currently runs from a Github Actions pipeline at the [DFSI](https://github.com/dsfsi/covid19za) repo.

## Contributing

1. Fork the repo
1. Open a new issue
1. Make changes and commit code
1. Submit a pull request

### TODOs

1. Use a cron job to store the latest Rt data
1. Run the Rt analytics engine directly in this project
1. Change loading animation
1. Consider optimising page loading by using a daily shared cache in db
1. Use a faster front-end plotting framework/method

## Local install

### Setup

1. `brew install postgresql`
1. `pip install virtualenv`
1. `cd /your_project_folder` 
1. `virtualenv env`
1. `cd env/bin`
1. `activate`
1. `cd ../..`
1. `pip install -r requirements.txt`

### Run Local

After adding new static file images, js, etc:
`python manage.py collectstatic --noinput`

Setup DB:
Mac
1. `initdb /usr/local/var/postgres`
1. `pg_ctl -D /usr/local/var/postgres -l logfile start`
1. `createdb <db_name>`
1. `psql <db_name>`

Ubuntu
1. `sudo apt-get install postgresql postgresql-contrib`
1. `sudo su - postgres`
1. `psql`
1. CTRL + D
1. `createdb <db_name>`

General
1. `CREATE USER <db_user> WITH PASSWORD '<db_password>';`
1. `GRANT ALL PRIVILEGES ON DATABASE <db_name> to <db_user>;`

Local run:
`python manage.py runserver`

After local session changes (due to WSGI config): 
`touch Covid19TrendsZA/wsgi.py`

## Production Install

Nginx:
Include this in your Nginx config
```Nginx
        location ^/static {
            autoindex on;
            alias /static/;
        }
```

Docker build:
`docker build --rm -t covid19trends .`

Docker migration (complete your params):
`docker run --rm -e SECRET_KEY="" -e DJANGO_DEBUG="0" -e ALLOWED_HOSTS="" -e DB_ENGINE="django.db.backends.postgresql_psycopg2" -e DB_NAME="" -e DB_USER="" -e DB_PASSWORD="" -e DB_HOST="" -e DB_PORT="5432" -e RUN_MIGRATE="1" --network <correct_docker_network> covid19trends python manage.py migrate`

**Caprover**:
Self host with Caprover! See the simple captain-definition config file, linked to Docker.
