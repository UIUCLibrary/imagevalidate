
ARG CONAN_USER_HOME=/conan

ARG CONAN_HOME=${CONAN_USER_HOME}/.conan2

ARG CONAN_CENTER_PROXY_V2_URL=https://center2.conan.io
# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V2_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.

ARG PIP_DOWNLOAD_CACHE=/.cache/pip
ARG UV_CACHE_DIR=/.cache/uv
ARG UV_EXTRA_INDEX_URL

FROM ghcr.io/astral-sh/uv:latest AS uv_builder

FROM ubuntu:24.04 AS wheel_builder_base
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    --mount=type=bind,source=ci/docker/linux/tox/apt-packages.txt,target=/tmp/apt-packages.txt \
    apt-get update && \
    apt-get install -yqq --no-install-recommends software-properties-common gpg-agent && \
    add-apt-repository ppa:deadsnakes/ppa && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -yqq install --no-install-recommends tzdata && \
    apt-get update && \
     < /tmp/apt-packages.txt xargs apt-get install -yqq --no-install-recommends

ARG CONAN_USER_HOME
RUN mkdir -p ${CONAN_USER_HOME}

FROM wheel_builder_base AS conan_builder
COPY --from=uv_builder /uv /uvx /bin/
ARG CONAN_USER_HOME
ARG CONAN_HOME
COPY ci/docker/shared/conan/remotes.json ${CONAN_HOME}/remotes.json
COPY conanfile.py /tmp/conanfile.py
ARG CONAN_CENTER_PROXY_V2_URL
ARG UV_EXTRA_INDEX_URL
ARG UV_INDEX_URL
ARG UV_CACHE_DIR
ENV UV_PROJECT=/tmp/uv
ENV UV_FROZEN=1
ENV UV_PROJECT_ENVIRONMENT=/tmp/uv/venv
RUN --mount=type=cache,target=${UV_CACHE_DIR} \
    --mount=type=tmpfs,target=${UV_PROJECT_ENVIRONMENT} \
    --mount=type=bind,source=pyproject.toml,target=${UV_PROJECT}/pyproject.toml \
    --mount=type=bind,source=uv.lock,target=${UV_PROJECT}/uv.lock \
    --mount=type=bind,source=conanfile.py,target=/tmp/conanfile.py \
    uv run --only-group=conan conan profile detect --exist-ok &&  \
    cat $(uv run --only-group=conan conan config home)/settings.yml && \
    uv run --only-group=conan conan config home && \
    if [ "$(jq -r '.remotes[0].url' ${CONAN_HOME}/remotes.json )" != "${CONAN_CENTER_PROXY_V2_URL}" ]; then \
        echo "Setting the conan center url for building cache: ${CONAN_CENTER_PROXY_V2_URL}" && \
        cp ${CONAN_HOME}/remotes.json /tmp/remotes.json && \
        uv run --only-group=conan conan remote update conan-center --url ${CONAN_CENTER_PROXY_V2_URL}; \
    fi && \
    uv run --only-group=conan conan install /tmp --build missing --build=openjpeg && \
    uv run --only-group=conan conan cache clean "*" -b --source --build --temp && \
    rm -rf venv && \
    if [ "$(jq -r '.remotes[0].url' ${CONAN_HOME}/remotes.json )" != "${CONAN_CENTER_PROXY_V2_URL}" ]; then \
        mv -f /tmp/remotes.json ${CONAN_HOME}/remotes.json; \
    fi
# ==============================================================================

FROM wheel_builder_base

COPY --from=uv_builder /uv /uvx /bin/
ARG CONAN_USER_HOME
ARG CONAN_HOME
COPY --from=conan_builder --chmod=777 ${CONAN_HOME} ${CONAN_HOME}
ENV CONAN_HOME=${CONAN_HOME}
ENV CONAN_USER_HOME=${CONAN_USER_HOME}

ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE
RUN mkdir -p ${PIP_DOWNLOAD_CACHE} && \
    chmod -R 777 ${PIP_DOWNLOAD_CACHE} && \
    mkdir -p ${UV_CACHE_DIR} && \
    chmod -R 777 ${UV_CACHE_DIR}

