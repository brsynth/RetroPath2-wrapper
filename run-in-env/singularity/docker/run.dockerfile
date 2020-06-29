FROM python:3-slim

RUN apt-get update -qqq \
 && apt-cache policy singularity-container \
 && apt-get install -y wget gnupg \
 && wget -O- http://neuro.debian.net/lists/xenial.us-ca.full | tee /etc/apt/sources.list.d/neurodebian.sources.list \
 && apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9 \
 && apt-get update \
 && apt-get install -y singularity-container


COPY custom/pypi/requirements.txt .
# install requirements
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

ARG HOME
WORKDIR ${HOME}
