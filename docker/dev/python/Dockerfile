FROM python:3.8-slim

RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc -y
COPY ./app /app

WORKDIR /app

RUN pip install -r requirements/prod.txt

COPY ./docker/dev/python/entrypoint.sh /entrypoint.sh
# COPY .env /.env

RUN chmod +x /entrypoint.sh
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
