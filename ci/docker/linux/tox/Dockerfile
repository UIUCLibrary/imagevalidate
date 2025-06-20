
ARG CONAN_USER_HOME=/conan

# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V1_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.
ARG CONAN_CENTER_PROXY_V1_URL

ARG PIP_DOWNLOAD_CACHE=/.cache/pip
ARG UV_CACHE_DIR=/.cache/uv
ARG UV_EXTRA_INDEX_URL
FROM ubuntu:22.04 AS wheel_builder_base
COPY ci/docker/linux/tox/apt-packages.txt /tmp/apt-packages.txt
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -yqq --no-install-recommends software-properties-common gpg-agent && \
    add-apt-repository ppa:deadsnakes/ppa && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -yqq install --no-install-recommends tzdata && \
    apt-get update && \
     < /tmp/apt-packages.txt xargs apt-get install -yqq --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

ARG CONAN_USER_HOME
RUN mkdir -p ${CONAN_USER_HOME}

FROM wheel_builder_base AS conan_builder
COPY requirements-dev.txt /tmp/requirements-dev.txt
ARG CONAN_USER_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG UV_EXTRA_INDEX_URL
ARG UV_INDEX_URL
COPY ci/docker/linux/shared/ensure_compiler_support_by_conan.py /tmp/ensure_compiler_support_by_conan.py
COPY ci/docker/shared/conan/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json

COPY conanfile.py /tmp/conanfile.py
ARG CONAN_CENTER_PROXY_V1_URL
RUN python3 -m venv venv && \
    venv/bin/pip install --no-cache --disable-pip-version-check uv && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan config init &&  \
    ./venv/bin/uv run /tmp/ensure_compiler_support_by_conan.py $(./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan config home)/settings.yml  11.4 && \
    cat $(./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan config home)/settings.yml && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan config home && \
    if [ -n "${CONAN_CENTER_PROXY_V1_URL}" ]; then \
        echo 'Using a proxy for conan center' && \
        cp ${CONAN_USER_HOME}/.conan/remotes.json /tmp/remotes.json && \
        ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remote remove conan-center && \
        ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remote add conan-center ${CONAN_CENTER_PROXY_V1_URL}; \
    fi && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan install /tmp --build outdated --build=openjpeg --no-import && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remove "*" -b --src -f && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remove --locks && \
    rm -rf venv && \
    if [ -n "${CONAN_CENTER_PROXY_V1_URL}" ]; then \
        mv -f /tmp/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json; \
    fi
# ==============================================================================

FROM wheel_builder_base

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

ARG CONAN_USER_HOME
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY --from=conan_builder ${CONAN_USER_HOME}/ ${CONAN_USER_HOME}/
RUN chmod -R 777 ${CONAN_USER_HOME}

ARG PIP_DOWNLOAD_CACHE
ARG UV_CACHE_DIR
RUN mkdir -p ${PIP_DOWNLOAD_CACHE} && \
    chmod -R 777 ${PIP_DOWNLOAD_CACHE} && \
    mkdir -p ${UV_CACHE_DIR} && \
    chmod -R 777 ${UV_CACHE_DIR}


WORKDIR /src
CMD ["tox", "--workdir", "/tmp/tox", "--recreate"]
