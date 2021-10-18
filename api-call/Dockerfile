# syntax=docker/dockerfile:1
FROM python:3.7-slim
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["tail", "-f", "/dev/null"]
