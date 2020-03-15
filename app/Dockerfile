FROM python:3.7-slim

# set work directory
WORKDIR /usr/src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Requirements
RUN pip3 install --upgrade pip
COPY ./requirements.txt /usr/src/requirements.txt
RUN pip3 install -r requirements.txt

# Download required spaCy models
RUN python -m spacy download es_core_news_md

# copy project
COPY . /usr/src/

