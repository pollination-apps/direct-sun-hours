FROM python:3.8-slim

WORKDIR /app

COPY . .
RUN pip3 --no-cache-dir install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 curl unzip -y