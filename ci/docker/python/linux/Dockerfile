ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user
RUN pip install wheel
RUN apt update && apt install -y cmake ninja-build
USER user
WORKDIR /home/user
