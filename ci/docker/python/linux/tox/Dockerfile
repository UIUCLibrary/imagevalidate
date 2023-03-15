ARG CONAN_USER_HOME=/conan
ARG PIP_DOWNLOAD_CACHE=/.cache/pip
FROM ubuntu:20.04 as wheel_builder_base
COPY ci/docker/python/linux/tox/apt-packages.txt /tmp/apt-packages.txt
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install -y software-properties-common --no-install-recommends && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    < /tmp/apt-packages.txt xargs apt-get install -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

FROM wheel_builder_base as conan_builder
COPY requirements/requirements_conan.txt /tmp/requirements_conan.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements_conan.txt cmake
ARG CONAN_USER_HOME
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
COPY conanfile.py /tmp/conanfile.py
RUN conan config home
RUN conan install /tmp --build outdated --build=openjpeg --no-import && \
    conan remove "*" -b --src -f && \
    conan remove --locks
# ==============================================================================

FROM wheel_builder_base

ARG CONAN_USER_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY requirements/ /tmp/requirements
RUN pip3 install --no-cache-dir wheel==0.37.1 && \
    pip3 install --no-cache-dir -r /tmp/requirements/requirements_tox.txt -r /tmp/requirements/requirements_conan.txt -r /tmp/requirements/requirements_devpi.txt

COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
COPY conanfile.py /tmp/conanfile.py
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY --from=conan_builder ${CONAN_USER_HOME}/ ${CONAN_USER_HOME}/
RUN conan config home
RUN conan install /tmp --build missing --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks
RUN chmod -R 777 ${CONAN_USER_HOME}

ARG PIP_DOWNLOAD_CACHE
RUN mkdir -p ${PIP_DOWNLOAD_CACHE} && \
    chmod -R 777 ${PIP_DOWNLOAD_CACHE}

WORKDIR /src
CMD ["tox", "--workdir", "/tmp/tox", "--recreate"]
