ARG IMAGE
FROM ${IMAGE}

COPY custom/pypi/requirements.txt .
# install requirements
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

ARG HOME
WORKDIR ${HOME}
