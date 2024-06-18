ARG PIPX_HOME=/pipx
ARG CONAN_USER_HOME=/conan
ARG PIP_DOWNLOAD_CACHE=/.cache/pip
ARG UV_CACHE_DIR=/.cache/uv
ARG UV_EXTRA_INDEX_URL
FROM ubuntu:22.04 AS wheel_builder_base
COPY ci/docker/python/linux/tox/apt-packages.txt /tmp/apt-packages.txt
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install -y software-properties-common gpg-agent --no-install-recommends && \
    add-apt-repository ppa:deadsnakes/ppa && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata && \
    apt-get update && \
     < /tmp/apt-packages.txt xargs apt-get install -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

FROM wheel_builder_base AS conan_builder
COPY requirements/requirements_conan.txt /tmp/requirements_conan.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements_conan.txt cmake
ARG CONAN_USER_HOME
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
COPY ci/docker/python/linux/shared/ensure_compiler_support_by_conan.py /tmp/ensure_compiler_support_by_conan.py
RUN conan config init &&  \
    python3 /tmp/ensure_compiler_support_by_conan.py $(conan config home)/settings.yml  11.4 && \
    cat $(conan config home)/settings.yml
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

COPY requirements/ /tmp/python_requirements/requirements/
COPY requirements-dev.txt /tmp/python_requirements
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r /tmp/python_requirements/requirements/requirements_tox.txt -r /tmp/python_requirements/requirements/requirements_conan.txt

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
ARG UV_CACHE_DIR
RUN mkdir -p ${PIP_DOWNLOAD_CACHE} && \
    chmod -R 777 ${PIP_DOWNLOAD_CACHE} && \
    mkdir -p ${UV_CACHE_DIR} && \
    chmod -R 777 ${UV_CACHE_DIR}

ENV UV_INDEX_STRATEGY=unsafe-best-match

ARG PIPX_HOME
ENV PIPX_HOME=${PIPX_HOME}
ENV PIPX_BIN_DIR=${PIPX_HOME}/bin
RUN pip3 install --no-cache-dir pipx && \
    pipx ensurepath && \
    mkdir -p $PIPX_HOME  && chmod -R 777 $PIPX_HOME
RUN PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install 'devpi-client<7.0' &&  \
    PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install pip-audit



WORKDIR /src
CMD ["tox", "--workdir", "/tmp/tox", "--recreate"]
