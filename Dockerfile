FROM python:3.7.6

ARG SECRET_KEY=${SECRET_KEY}
ARG DJANGO_DEBUG=${DJANGO_DEBUG}
ARG ALLOWED_HOSTS=${ALLOWED_HOSTS}
ARG DB_ENGINE=${DB_ENGINE}
ARG DB_HOST=${DB_HOST}
ENV DB_NAME=${DB_NAME}
ENV DB_USER=${DB_USER}
ARG DB_PASSWORD=${DB_PASSWORD}
ARG DB_PORT=${DB_PORT}
ARG RUN_MIGRATE=${RUN_MIGRATE}
ARG G_ANALYTICS_ID=${G_ANALYTICS_ID}
ARG SCRIPT_ID=${G_ANALYTICS_ID}
ARG SECRET_KEY=${SECRET_KEY}

RUN apk update
RUN apk upgrade
RUN apk add --no-cache make g++ bash git openssh postgresql-dev curl

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
COPY ./ /usr/src/app
RUN mkdir -p /usr/src/app/staticfiles

RUN python manage.py collectstatic --noinput

EXPOSE 8000
# For production
CMD ["gunicorn", "Covid19TrendsZA.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
# For localhost testing
#CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000" ]
