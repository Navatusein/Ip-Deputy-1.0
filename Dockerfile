FROM python:3.10.6-buster

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
COPY . /app
