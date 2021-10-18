# syntax=docker/dockerfile:1
FROM mysql:8.0.25
ENV MYSQL_DATABASE="%%%%"
ENV MYSQL_ROOT_PASSWORD="%%%%"
ENV MYSQL_ROOT_HOST=%
RUN apt-get update && apt-get install
RUN apt-get install expect -y
RUN apt-get install sudo -y
WORKDIR /code
ADD maxmem.sh /code
ADD mysql.cnf /etc/mysql/conf.d/
ADD report-builder.sql /docker-entrypoint-initdb.d
