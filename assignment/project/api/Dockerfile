
FROM python:3.8.13 as base

ENV PYTHONPATH=$PYTHONPATH:/src/


COPY ./requirements.txt /src/requirements.txt


WORKDIR /src

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt


RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY ./ /src/


FROM base as build


CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 main:app
