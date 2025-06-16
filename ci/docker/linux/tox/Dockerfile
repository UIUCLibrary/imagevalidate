
ARG CONAN_USER_HOME=/conan

ARG CONAN_HOME=${CONAN_USER_HOME}/.conan2

ARG CONAN_CENTER_PROXY_V2_URL=https://center2.conan.io
# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V2_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.

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
ARG CONAN_HOME
COPY ci/docker/linux/shared/ensure_compiler_support_by_conan.py /tmp/ensure_compiler_support_by_conan.py
COPY ci/docker/shared/conan/remotes.json ${CONAN_HOME}/remotes.json

COPY conanfile.py /tmp/conanfile.py
ARG CONAN_CENTER_PROXY_V2_URL
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG UV_EXTRA_INDEX_URL
ARG UV_INDEX_URL
ENV UV_CONSTRAINT=/tmp/requirements-dev.txt
ARG PIP_DOWNLOAD_CACHE
ARG UV_CACHE_DIR
RUN --mount=type=cache,target=${PIP_DOWNLOAD_CACHE} \
    --mount=type=cache,target=${UV_CACHE_DIR} \
    python3 -m venv venv && \
    ./venv/bin/pip install --no-cache --disable-pip-version-check uv && \
    ./venv/bin/uvx --with cmake conan profile detect --exist-ok &&  \
    ./venv/bin/uv run /tmp/ensure_compiler_support_by_conan.py ${CONAN_HOME}/settings.yml  11.4 && \
    cat $(./venv/bin/uvx --with cmake conan config home)/settings.yml && \
    ./venv/bin/uvx --with cmake conan config home && \
    if [ "$(jq -r '.remotes[0].url' ${CONAN_HOME}/remotes.json )" != "${CONAN_CENTER_PROXY_V2_URL}" ]; then \
        echo "Setting the conan center url for building cache: ${CONAN_CENTER_PROXY_V2_URL}" && \
        cp ${CONAN_HOME}/remotes.json /tmp/remotes.json && \
        ./venv/bin/uvx --with cmake conan remote update conan-center --url ${CONAN_CENTER_PROXY_V2_URL}; \
    fi && \
    ./venv/bin/uvx --with cmake conan install /tmp --build missing --build=openjpeg && \
    ./venv/bin/uvx --with cmake conan cache clean "*" -b --source --build --temp && \
    rm -rf venv && \
    if [ "$(jq -r '.remotes[0].url' ${CONAN_HOME}/remotes.json )" != "${CONAN_CENTER_PROXY_V2_URL}" ]; then \
        mv -f /tmp/remotes.json ${CONAN_HOME}/remotes.json; \
    fi
# ==============================================================================

FROM wheel_builder_base


ARG CONAN_USER_HOME
ARG CONAN_HOME
COPY --from=conan_builder ${CONAN_HOME} ${CONAN_HOME}
ENV CONAN_HOME=${CONAN_HOME}
ENV CONAN_USER_HOME=${CONAN_USER_HOME}

ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE
RUN chmod -R 777 ${CONAN_HOME} && \
    mkdir -p ${PIP_DOWNLOAD_CACHE} && \
    chmod -R 777 ${PIP_DOWNLOAD_CACHE} && \
    mkdir -p ${UV_CACHE_DIR} && \
    chmod -R 777 ${UV_CACHE_DIR}

