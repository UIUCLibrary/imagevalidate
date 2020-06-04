ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

ARG CMAKE_DOWNLOAD_URL=https://github.com/Kitware/CMake/releases/download/v3.17.3/cmake-3.17.3-Linux-x86_64.sh
RUN wget -O /tmp/install_cmake.sh $CMAKE_DOWNLOAD_URL
RUN chmod +x /tmp/install_cmake.sh  && /tmp/install_cmake.sh  --skip-license

RUN apt update && apt install -y ninja-build

ENV PIP_EXTRA_INDEX_URL="https://devpi.library.illinois.edu/production/release"
ADD requirements.txt /requirements.txt
USER user
WORKDIR /home/user
RUN python -m pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install wheel && \
    pip install pytest-cov lxml sphinx mypy flake8 tox devpi-client && \
    pip install -r /requirements.txt --pre
