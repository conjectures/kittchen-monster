FROM python:3.8-slim

RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc -y
COPY ./app /app

WORKDIR /app

RUN pip install -r requirements/dev.txt

COPY ./docker/dev/python/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
