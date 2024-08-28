ARG PIPX_HOME=/pipx
ARG PIP_FIND_LINKS=/wheels
ARG CONAN_USER_HOME=/conan
ARG SONAR_SCANNER_VERSION=5.0.1.3006
FROM ubuntu:22.04 AS base_image
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt \
    DEBIAN_FRONTEND="noninteractive" apt-get update &&  \
    apt-get install -yqq software-properties-common gpg-agent --no-install-recommends && \
    apt-get -yqq install tzdata && \
    apt-get install -yqq --no-install-recommends \
        ninja-build \
        build-essential \
        ccache \
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

FROM base_image AS wheel_builder

ARG PYTHON_INDEX
ARG PIP_EXTRA_INDEX_URL
ENV PIP_NO_CACHE_DIR=1
COPY requirements-dev.txt /requirements/

ARG PIP_FIND_LINKS
RUN mkdir -p ${PIP_FIND_LINKS} &&  \
    python3 -m pip install pip --upgrade && \
    pip wheel --wheel-dir=${PIP_FIND_LINKS} --no-cache-dir -r /requirements/requirements-dev.txt
#==============================================================================

FROM base_image AS SONAR_BUILDER
ARG SONAR_SCANNER_VERSION
ARG SONAR_SCANNER_HOME=/opt/sonar/${SONAR_SCANNER_VERSION}-linux
ENV SONAR_USER_HOME=/opt/sonar/.sonar

RUN curl --create-dirs -sSLo /tmp/sonar-scanner.zip \
        https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip && \
    ls -la /tmp/ && \
    unzip -o /tmp/sonar-scanner.zip -d /opt/sonar/ && \
    rm /tmp/sonar-scanner.zip && \
    mkdir -p $SONAR_USER_HOME/cache && \
    chmod -R 777 "${SONAR_USER_HOME}" &&\
    ln -s /opt/sonar/sonar-scanner-${SONAR_SCANNER_VERSION}-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    which sonar-scanner


RUN curl --create-dirs -sSLo /tmp/build-wrapper-linux-x86.zip https://sonarcloud.io/static/cpp/build-wrapper-linux-x86.zip && \
    unzip -o /tmp/build-wrapper-linux-x86.zip -d /opt/ &&\
    ln -s /opt/build-wrapper-linux-x86/build-wrapper-linux-x86-64 /usr/local/bin/build-wrapper-linux-x86-64 && \
    which build-wrapper-linux-x86-64


FROM wheel_builder AS conan_builder
ARG CONAN_USER_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/shared/conan/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json
COPY ci/docker/python/linux/jenkins/conan/profile.ini  ${CONAN_USER_HOME}/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py
COPY ci/docker/python/linux/shared/ensure_compiler_support_by_conan.py /tmp/ensure_compiler_support_by_conan.py
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN --mount=type=cache,target=${CONAN_USER_HOME}/.conan \
    python3 -m venv venv && \
    . ./venv/bin/activate  && \
    pip install --no-cache $(grep ^uv /tmp/requirements-dev.txt) && \
    uv pip install --no-cache $(grep ^conan /tmp/requirements-dev.txt) && \
    uv pip install --no-cache $(grep ^cmake /tmp/requirements-dev.txt) && \
    conan config init &&  \
    python3 /tmp/ensure_compiler_support_by_conan.py $(conan config home)/settings.yml  11.4 && \
    conan install /tmp --build outdated --no-import -pr:b=default && \
    conan install /tmp --build outdated --no-import -pr:b=default -o "*:shared=True" && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    deactivate && rm -rf venv


# shared files are needed to run the Build C++ Tests stage

FROM base_image

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends  \
      ninja-build \
      ccache \
      clang-tidy \
      cppcheck && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Install sonar-scanner and build-wrapper
# -----------------------------------------------------------------------------

COPY --from=SONAR_BUILDER /opt/sonar /opt/sonar/
COPY --from=SONAR_BUILDER /opt/build-wrapper-linux-x86 /opt/build-wrapper-linux-x86/
ARG SONAR_SCANNER_VERSION
ARG SONAR_SCANNER_HOME=/opt/sonar/${SONAR_SCANNER_VERSION}-linux
ENV SONAR_USER_HOME=/opt/sonar/.sonar

RUN ln -s /opt/sonar/sonar-scanner-${SONAR_SCANNER_VERSION}-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    which sonar-scanner

RUN ln -s /opt/build-wrapper-linux-x86/build-wrapper-linux-x86-64 /usr/local/bin/build-wrapper-linux-x86-64 && \
    which build-wrapper-linux-x86-64

RUN mkdir -p /.sonar/cache && \
    chmod -R 777 /.sonar/cache && \
    chmod -R 777 $SONAR_USER_HOME

ENV SONAR_SCANNER_OPTS="-server"

# -----------------------------------------------------------------------------
# Install Doctor memory
# -----------------------------------------------------------------------------
COPY --from=DR_MEMORY_BUILDER /opt/drmemory /opt/drmemory/
RUN ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version

ARG PIP_EXTRA_INDEX_URL
ARG PIP_FIND_LINKS
COPY requirements-dev.txt /requirements/requirements-dev.txt

RUN --mount=type=bind,from=wheel_builder,source=${PIP_FIND_LINKS},target=${PIP_FIND_LINKS}\
    python3 -m pip install pip --upgrade && \
    pip install --no-index --no-cache-dir --find-links=${PIP_FIND_LINKS} \
    -r /requirements/requirements-dev.txt

ENV PIP_FIND_LINKS=${PIP_FIND_LINKS}
ENV PIP_NO_CACHE_DIR=1

ARG PIPX_HOME
ENV PIPX_HOME=${PIPX_HOME}
ENV PIPX_BIN_DIR=${PIPX_HOME}/bin
RUN pip3 install --no-cache-dir pipx && \
    pipx ensurepath && \
    mkdir -p $PIPX_HOME  && chmod -R 777 $PIPX_HOME
RUN PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install 'devpi-client<7.0' &&  \
    PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install pip-audit


ARG CONAN_USER_HOME
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY --from=conan_builder ${CONAN_USER_HOME}/.conan/ ${CONAN_USER_HOME}/.conan/
COPY conanfile.py /tmp/conanfile.py
RUN conan config home
RUN conan install /tmp --build outdated --no-import -pr:b=default && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    chmod -R 777 ${CONAN_USER_HOME}
ENV TZ=UTC