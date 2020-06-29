ARG IMAGE
FROM ${IMAGE}

RUN apt-get update \
 && apt-get install -y python3-pip \
 && /usr/bin/python3 -m pip install pip-compile-multi

WORKDIR ${HOME}
