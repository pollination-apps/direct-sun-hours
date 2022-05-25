FROM python:3.8-slim

WORKDIR /app

COPY . .
RUN pip3 --disable-pip-version-check --no-cache-dir install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 curl unzip -y

ENV RAYPATH=/home/lib
ENV PATH="/home/bin:${PATH}"
RUN curl -L https://github.com/LBNL-ETA/Radiance/releases/download/947ea88a/Radiance_947ea88a_Linux.zip --output radiance.zip \
&& unzip -p radiance.zip | tar xz \
&& mkdir /home/bin \
&& mkdir /home/lib \
&& mv ./radiance-5.4.947ea88a29-Linux/usr/local/radiance/bin/* /home/bin \
&& mv ./radiance-5.4.947ea88a29-Linux/usr/local/radiance/lib/* /home/lib \
&& rm -rf radiance-5.4.947ea88a29-Linux \
&& rm radiance.zip \
&& cat config.json > /usr/local/lib/python3.8/site-packages/honeybee_radiance/config.json

# UPDATE with latest honeybee-radiance to use honeybee-radiance set-config radiance-path [PATH_TO_RADIANCE]