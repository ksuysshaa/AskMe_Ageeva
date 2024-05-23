FROM container-registry.oracle.com/mysql/enterprise-server:latest

ENV MYSQL_ROOT_PASSWORD pass
COPY ./data.sql /docker-entrypoint-initdb.d/data.sql