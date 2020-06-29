ARG IMAGE
FROM ${IMAGE}

COPY test/docker/requirements.txt requirements-test.txt
COPY custom/pypi/requirements.txt requirements-src.txt
# install requirements
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir --upgrade -r requirements-test.txt \
 && python3 -m pip install --no-cache-dir --upgrade -r requirements-src.txt

ARG HOME
WORKDIR ${HOME}
