FROM python:3.10.11-slim-buster

WORKDIR /evalquiz-client-flask
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt