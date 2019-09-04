# first stage build
FROM python:3.7 AS base
MAINTAINER KELVIN
# copy requirements
# install requirements dynamically
ARG dependencies=requirements
ENV dependencies=${dependencies}
COPY ${dependencies}.txt ./
RUN pip install -r ${dependencies}.txt
# create app dir
WORKDIR /app
# copy everything to app dir
COPY . /app

# second stage build
FROM python:3.7-slim AS release
# needed to able run make command
RUN apt-get update && apt-get install make
# set work dir
WORKDIR /app
# copy everything from base
ARG dependencies=requirements
ENV dependencies=${dependencies}
COPY --from=base /app/${dependencies}.txt ./
COPY --from=base /root/.cache /root/.cache
# install requirements
RUN pip install -r ${dependencies}.txt
# copy again
COPY --from=base /app ./