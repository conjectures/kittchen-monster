FROM python:3.8-slim

RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc -y

WORKDIR /app

COPY ./app/requirements /app/requirements
RUN pip install --no-cache-dir -r requirements/prod.txt


COPY ./app /app

EXPOSE 8000

COPY ./docker/prod/python/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "kittchen.pwsgi", "-b 0.0.0.0:8000"]
