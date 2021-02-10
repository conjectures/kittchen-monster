FROM python:3.8-slim

RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc -y

COPY ./docker/dev/python/entrypoint.sh /entrypoint.sh
WORKDIR /app

COPY ./app/requirements /app/requirements
RUN pip install -r requirements/dev.txt

COPY ./app /app

RUN chmod +x /entrypoint.sh
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
