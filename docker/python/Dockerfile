FROM python:3.8-slim

COPY ./app /app

WORKDIR /app

RUN pip install -r requirements/base.txt

COPY ./docker/python/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
