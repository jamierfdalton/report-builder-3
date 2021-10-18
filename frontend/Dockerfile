# syntax=docker/dockerfile:1
FROM python:3.8-slim
WORKDIR /code
RUN apt update && apt install build-essential -y
COPY requirements.txt requirements.txt
RUN pip install --upgrade pop && pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]
