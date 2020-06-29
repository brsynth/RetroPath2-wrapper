ARG IMAGE
FROM ${IMAGE}

COPY publish/pypi/docker/requirements.txt .
# install requirements
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

ARG HOME
WORKDIR ${HOME}

# ARG PKG
# COPY custom/src ${PKG}
# COPY custom/pypi .
# RUN mv requirements.txt __init__.py ${PKG}
# COPY LICENSE .
# COPY README.md .
