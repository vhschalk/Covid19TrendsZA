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

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /
COPY . /

RUN mkdir -p /staticfiles

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python manage.py collectstatic --noinput
RUN echo "Secret: "$SECRET_KEY
RUN echo "Debug: "$DJANGO_DEBUG
RUN echo "DB: "$DB_ENGINE
#RUN python manage.py migrate #TODO: does not load all env params correctly in caprover

EXPOSE 8000
# TODO: switch to a batch script
CMD ["gunicorn", "Covid19TrendsZA.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
# For localhost testing
#CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000" ]
