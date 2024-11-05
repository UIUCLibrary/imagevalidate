ARG PIPX_HOME=/pipx
ARG CONAN_USER_HOME=/conan
ARG PIP_DOWNLOAD_CACHE=/.cache/pip
ARG UV_CACHE_DIR=/.cache/uv
ARG UV_EXTRA_INDEX_URL
FROM ubuntu:22.04 AS wheel_builder_base
COPY ci/docker/python/linux/tox/apt-packages.txt /tmp/apt-packages.txt
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
COPY ci/docker/python/linux/shared/ensure_compiler_support_by_conan.py /tmp/ensure_compiler_support_by_conan.py
COPY conanfile.py /tmp/conanfile.py
RUN --mount=type=cache,target=${CONAN_USER_HOME}/.conan \
    python3 -m venv venv && \
    . ./venv/bin/activate  && \
    pip install --no-cache $(grep ^uv /tmp/requirements-dev.txt) && \
    uv pip install --no-cache $(grep ^conan /tmp/requirements-dev.txt) && \
    uv pip install --no-cache $(grep ^cmake /tmp/requirements-dev.txt) && \
    conan config init &&  \
    python3 /tmp/ensure_compiler_support_by_conan.py $(conan config home)/settings.yml  11.4 && \
    cat $(conan config home)/settings.yml && \
    conan config home && \
    conan install /tmp --build outdated --build=openjpeg --no-import && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    deactivate && rm -rf venv
# ==============================================================================

FROM wheel_builder_base

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY requirements/requirements_conan.txt /tmp/python_requirements/requirements/requirements_conan.txt
COPY requirements/requirements_tox.txt /tmp/python_requirements/requirements/requirements_tox.txt
COPY requirements-dev.txt /tmp/python_requirements
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r /tmp/python_requirements/requirements/requirements_tox.txt -r /tmp/python_requirements/requirements/requirements_conan.txt

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

ENV UV_INDEX_STRATEGY=unsafe-best-match

WORKDIR /src
CMD ["tox", "--workdir", "/tmp/tox", "--recreate"]
