ARG PYTHON_VERSION=3.8

FROM python:${PYTHON_VERSION} as wheel_builder
ARG CMAKE_DOWNLOAD_URL=https://github.com/Kitware/CMake/releases/download/v3.17.3/cmake-3.17.3-Linux-x86_64.sh

RUN wget -O /tmp/install_cmake.sh $CMAKE_DOWNLOAD_URL && \
    chmod +x /tmp/install_cmake.sh  && \
    /tmp/install_cmake.sh  --skip-license

RUN apt update && apt install -y ninja-build \
    && rm -rf /var/lib/apt/lists/*

ARG PYTHON_INDEX=https://devpi.library.illinois.edu/production/release
ENV PIP_EXTRA_INDEX_URL=${PYTHON_INDEX}
ADD requirements.txt ci/docker/shared/python/requirements-ci.txt /requirements/
RUN python -m pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install wheel

RUN pip wheel --wheel-dir=/wheels  \
        -r /requirements/requirements.txt \
        -r /requirements/requirements-ci.txt \
         -i ${PYTHON_INDEX} -v

FROM python:${PYTHON_VERSION}

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

ARG CMAKE_DOWNLOAD_URL=https://github.com/Kitware/CMake/releases/download/v3.17.3/cmake-3.17.3-Linux-x86_64.sh
RUN wget -O /tmp/install_cmake.sh $CMAKE_DOWNLOAD_URL && \
    chmod +x /tmp/install_cmake.sh  && \
    /tmp/install_cmake.sh  --skip-license && \
    rm /tmp/install_cmake.sh

RUN apt update && apt install -y ninja-build && \
    rm -rf /var/lib/apt/lists/*

ENV PIP_EXTRA_INDEX_URL="https://devpi.library.illinois.edu/production/release"

RUN python -m pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install wheel

COPY --from=wheel_builder /wheels /wheels/

ADD requirements.txt ci/docker/shared/python/requirements-ci.txt /requirements/
RUN pip install --no-index --find-links=/wheels  \
        -r /requirements/requirements.txt --pre && \
    pip install --no-index --find-links=/wheels  \
        -r /requirements/requirements-ci.txt

ENV PIP_FIND_LINKS=/wheels

USER user
WORKDIR /home/user