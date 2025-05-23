ARG PIPX_HOME=/pipx
ARG CONAN_USER_HOME=/conan
FROM ubuntu:22.04 AS base_image
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt \
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
        software-properties-common \
        unzip && \
     rm -rf /var/lib/apt/lists/*

#==============================================================================
FROM base_image AS DR_MEMORY_BUILDER
RUN apt-get update &&  \
    apt-get install -y --no-install-recommends wget

WORKDIR /drmemory
RUN wget --no-verbose https://github.com/DynamoRIO/drmemory/releases/download/release_2.3.0/DrMemory-Linux-2.3.0-1.tar.gz && \
    mkdir -p /opt/drmemory && tar xzf DrMemory-Linux-2.3.0-1.tar.gz -C /opt/drmemory --strip-components=1 && \
    ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version


FROM base_image AS SONAR_BUILDER

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
ARG CONAN_USER_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG UV_EXTRA_INDEX_URL
ARG UV_INDEX_URL

COPY ci/docker/linux/jenkins/conan/profile.ini  ${CONAN_USER_HOME}/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py
COPY ci/docker/linux/shared/ensure_compiler_support_by_conan.py /tmp/ensure_compiler_support_by_conan.py
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN python3 -m venv venv && \
    venv/bin/pip install --no-cache --disable-pip-version-check uv && \
    . ./venv/bin/activate  && \
    uv pip install --no-cache --index-strategy unsafe-best-match -r /tmp/requirements-dev.txt && \
    conan config init &&  \
    python3 /tmp/ensure_compiler_support_by_conan.py $(conan config home)/settings.yml  11.4 && \
    conan install /tmp --build outdated --no-import -pr:b=default && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    deactivate && rm -rf venv


# shared files are needed to run the Build C++ Tests stage

FROM base_image

# -----------------------------------------------------------------------------
# Install sonar build-wrapper
# -----------------------------------------------------------------------------

COPY --from=SONAR_BUILDER /opt/build-wrapper-linux /opt/build-wrapper-linux/

RUN case $(uname -m) in \
        x86_64) ln -s /opt/build-wrapper-linux/build-wrapper-linux-x86/build-wrapper-linux-x86-64 /usr/local/bin/build-wrapper-linux  ;; \
        aarch64) ln ln -s /opt/build-wrapper-linux/build-wrapper-linux-aarch64/build-wrapper-linux-aarch64 /usr/local/bin/build-wrapper-linux  ;; \
    esac; \
    which build-wrapper-linux
ENV SONAR_SCANNER_OPTS="-server"

# -----------------------------------------------------------------------------
# Install Doctor memory
# -----------------------------------------------------------------------------
COPY --from=DR_MEMORY_BUILDER /opt/drmemory /opt/drmemory/
RUN ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version

ARG PIP_EXTRA_INDEX_URL

ENV PIP_NO_CACHE_DIR=1

ARG CONAN_USER_HOME
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY --from=conan_builder ${CONAN_USER_HOME}/.conan/ ${CONAN_USER_HOME}/.conan/
RUN chmod -R 777 ${CONAN_USER_HOME}
ENV TZ=UTC