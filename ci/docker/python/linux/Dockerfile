ARG PYTHON_VERSION=3.8

FROM python:${PYTHON_VERSION} as wheel_builder

ARG CMAKE_DOWNLOAD_URL=https://github.com/Kitware/CMake/releases/download/v3.17.3/cmake-3.17.3-Linux-x86_64.sh
RUN wget -O /tmp/install_cmake.sh $CMAKE_DOWNLOAD_URL
RUN chmod +x /tmp/install_cmake.sh  && /tmp/install_cmake.sh  --skip-license

RUN apt update && apt install -y ninja-build
ARG PYTHON_INDEX=https://devpi.library.illinois.edu/production/release
ENV PIP_EXTRA_INDEX_URL=${PYTHON_INDEX}
ADD requirements.txt /requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install wheel && \
    pip wheel --wheel-dir=/wheels pytest-cov lxml sphinx mypy flake8 tox devpi-client -i ${PYTHON_INDEX} -v && \
    pip wheel --wheel-dir=/wheels -r /requirements.txt --pre -i ${PYTHON_INDEX} -v



FROM python:${PYTHON_VERSION}

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

#RUN wget -O /tmp/install_cmake.sh $CMAKE_DOWNLOAD_URL
COPY --from=wheel_builder /tmp/install_cmake.sh /tmp/install_cmake.sh
RUN chmod +x /tmp/install_cmake.sh  && /tmp/install_cmake.sh  --skip-license

RUN apt update && apt install -y ninja-build

ENV PIP_EXTRA_INDEX_URL="https://devpi.library.illinois.edu/production/release"
COPY --from=wheel_builder /wheels /wheels/
ADD requirements.txt /requirements.txt
ENV PIP_FIND_LINKS=/wheels
RUN python -m pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install wheel && \
    pip install pytest-cov lxml sphinx mypy flake8 tox devpi-client && \
    pip install --no-index  -r /requirements.txt --pre

USER user
WORKDIR /home/user
