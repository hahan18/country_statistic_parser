FROM python:3.10

COPY ./requirements.txt /requirements.txt

RUN pip install --upgrade pip &&  \
    pip install -r /requirements.txt && \
    mkdir /app

COPY . /app

WORKDIR /app
