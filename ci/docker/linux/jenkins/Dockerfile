ARG CONAN_USER_HOME=/conan

ARG CONAN_HOME=${CONAN_USER_HOME}/.conan2

ARG CONAN_CENTER_PROXY_V2_URL=https://center2.conan.io
# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V2_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.

ARG PIP_DOWNLOAD_CACHE=/.cache/pip
# PIP Cache directory. Change this only if you need to override the default location.

ARG UV_CACHE_DIR=/.cache/uv
# UV Cache directory. Change this only if you need to override the default location.

FROM ghcr.io/astral-sh/uv:latest AS uv_builder

FROM ubuntu:24.04 AS base_image
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    DEBIAN_FRONTEND="noninteractive" apt-get update &&  \
    apt-get install -yqq software-properties-common gpg-agent --no-install-recommends && \
    apt-get -yqq install tzdata && \
    apt-get install -yqq --no-install-recommends \
        build-essential \
        clang-tidy \
        ccache \
        cppcheck \
        curl\
        git \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        ca-certificates \
        software-properties-common


#==============================================================================
FROM base_image AS dr_memory_builder
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update &&  \
    apt-get install -y --no-install-recommends wget

WORKDIR /drmemory
RUN wget --no-verbose https://github.com/DynamoRIO/drmemory/releases/download/release_2.3.0/DrMemory-Linux-2.3.0-1.tar.gz && \
    mkdir -p /opt/drmemory && tar xzf DrMemory-Linux-2.3.0-1.tar.gz -C /opt/drmemory --strip-components=1 && \
    ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version


FROM base_image AS sonar_builder
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update &&  \
    apt-get install -yqq --no-install-recommends unzip

RUN case $(uname -m) in \
    x86_64) URL=https://sonarcloud.io/static/cpp/build-wrapper-linux-x86.zip ;; \
    aarch64) URL=https://sonarcloud.io/static/cpp/build-wrapper-linux-aarch64.zip ;; \
    esac; \
    curl --create-dirs -sSLo /tmp/build-wrapper-linux.zip $URL && \
    unzip -o /tmp/build-wrapper-linux.zip -d /opt/build-wrapper-linux/ && \
    case $(uname -m) in \
        x86_64) ln -s /opt/build-wrapper-linux/build-wrapper-linux-x86/build-wrapper-linux-x86-64 /usr/local/bin/build-wrapper-linux ;; \
        aarch64) ln -s /opt/build-wrapper-linux/build-wrapper-linux-aarch64/build-wrapper-linux-aarch64 /usr/local/bin/build-wrapper-linux ;; \
    esac; \
    which build-wrapper-linux


FROM base_image AS conan_builder
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    DEBIAN_FRONTEND="noninteractive" apt-get update &&  \
    apt-get install -yqq --no-install-recommends jq

ARG CONAN_USER_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG UV_EXTRA_INDEX_URL
ARG UV_INDEX_URL

COPY --from=uv_builder /uv /uvx /bin/
ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE
ARG CONAN_CENTER_PROXY_V2_URL
ARG CONAN_HOME
ENV UV_PROJECT=/tmp/uv
ENV UV_FROZEN=1
ENV UV_PROJECT_ENVIRONMENT=/tmp/uv/venv
COPY ci/docker/linux/jenkins/conan/profile.ini  ${CONAN_HOME}/profiles/default
COPY ci/docker/shared/conan/remotes.json ${CONAN_HOME}/remotes.json
RUN --mount=type=cache,target=${PIP_DOWNLOAD_CACHE} \
    --mount=type=cache,target=${UV_CACHE_DIR} \
    --mount=type=bind,source=pyproject.toml,target=${UV_PROJECT}/pyproject.toml \
    --mount=type=bind,source=uv.lock,target=${UV_PROJECT}/uv.lock \
    --mount=type=bind,source=conanfile.py,target=/tmp/conanfile.py \
    --mount=type=bind,source=conan.lock,target=${UV_PROJECT}/conan.lock \
    --mount=type=tmpfs,target=${UV_PROJECT_ENVIRONMENT} \
    uv run --only-group=conan conan profile detect --exist-ok &&  \
    if [ "$(jq -r '.remotes[0].url' ${CONAN_HOME}/remotes.json )" != "${CONAN_CENTER_PROXY_V2_URL}" ]; then \
        echo "Setting the conan center url for building cache: ${CONAN_CENTER_PROXY_V2_URL}" && \
        cp ${CONAN_HOME}/remotes.json /tmp/remotes.json && \
        uv run --only-group=conan conan remote update conan-center --url ${CONAN_CENTER_PROXY_V2_URL}; \
    fi && \
    uv run --only-group=conan conan install /tmp --build missing -pr:b=default && \
    uv run --only-group=conan conan cache clean "*" -b --source --build --temp && \
    if [ "$(jq -r '.remotes[0].url' ${CONAN_HOME}/remotes.json )" != "${CONAN_CENTER_PROXY_V2_URL}" ]; then \
        mv -f /tmp/remotes.json ${CONAN_HOME}/remotes.json; \
    fi


# shared files are needed to run the Build C++ Tests stage

FROM base_image
COPY --from=uv_builder /uv /uvx /bin/
# -----------------------------------------------------------------------------
# Install sonar build-wrapper
# -----------------------------------------------------------------------------

COPY --from=sonar_builder /opt/build-wrapper-linux /opt/build-wrapper-linux/

RUN case $(uname -m) in \
        x86_64) ln -s /opt/build-wrapper-linux/build-wrapper-linux-x86/build-wrapper-linux-x86-64 /usr/local/bin/build-wrapper-linux  ;; \
        aarch64) ln ln -s /opt/build-wrapper-linux/build-wrapper-linux-aarch64/build-wrapper-linux-aarch64 /usr/local/bin/build-wrapper-linux  ;; \
    esac; \
    which build-wrapper-linux
ENV SONAR_SCANNER_OPTS="-server"

# -----------------------------------------------------------------------------
# Install Doctor memory
# -----------------------------------------------------------------------------
COPY --from=dr_memory_builder /opt/drmemory /opt/drmemory/
RUN ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version

ARG PIP_EXTRA_INDEX_URL

ENV PIP_NO_CACHE_DIR=1

ARG CONAN_USER_HOME
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
ARG CONAN_HOME
ENV CONAN_HOME=${CONAN_HOME}
COPY --from=conan_builder --chmod=777 ${CONAN_HOME} ${CONAN_HOME}
ENV TZ=UTC