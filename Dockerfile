FROM python:latest
    MAINTAINER Ben Chung <bchung@hpe.com>

WORKDIR /dir

COPY requirements.txt .
COPY main.py .

RUN pip install -r requirements.txt
RUN python3 -m main
