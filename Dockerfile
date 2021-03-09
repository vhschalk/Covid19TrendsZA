FROM python:3.7.6

ENV PYTHONUNBUFFERED=1

ARG SECRET_KEY=${SECRET_KEY}
ARG DJANGO_DEBUG=${DJANGO_DEBUG}
ARG ALLOWED_HOSTS=${ALLOWED_HOSTS}
ARG DB_ENGINE=${DB_ENGINE}
ARG DB_HOST=${DB_HOST}
ENV DB_NAME=${DB_NAME}
ENV DB_USER=${DB_USER}
ARG DB_PASSWORD=${DB_PASSWORD}
ARG DB_PORT=${DB_PORT}
ARG G_ANALYTICS_ID=${G_ANALYTICS_ID}
ARG SCRIPT_ID=${G_ANALYTICS_ID}
ARG SECRET_KEY=${SECRET_KEY}

WORKDIR /
COPY . /

RUN mkdir -p /staticfiles

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate 

EXPOSE 8000
# For production
CMD ["gunicorn", "Covid19TrendsZA.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
# For localhost testing
#CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000" ]
