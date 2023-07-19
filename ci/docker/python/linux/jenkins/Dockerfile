ARG PIP_FIND_LINKS=/wheels
ARG CONAN_USER_HOME=/conan
ARG SONAR_SCANNER_VERSION=4.8.0.2856
FROM ubuntu:22.04 as base_image
RUN DEBIAN_FRONTEND="noninteractive" apt-get update &&  \
    apt-get install -y software-properties-common gpg-agent --no-install-recommends && \
    apt-get -y install tzdata && \
    apt-get install -y --no-install-recommends \
        ninja-build \
        build-essential \
        ccache \
        git \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        ca-certificates \
        software-properties-common && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#==============================================================================
FROM base_image as DR_MEMORY_BUILDER
RUN apt-get update &&  \
    apt-get install -y --no-install-recommends wget

WORKDIR /drmemory
RUN wget --no-verbose https://github.com/DynamoRIO/drmemory/releases/download/release_2.3.0/DrMemory-Linux-2.3.0-1.tar.gz && \
    mkdir -p /opt/drmemory && tar xzf DrMemory-Linux-2.3.0-1.tar.gz -C /opt/drmemory --strip-components=1 && \
    ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version

FROM base_image as wheel_builder

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends  \
      ninja-build \
    && rm -rf /var/lib/apt/lists/*

ARG PYTHON_INDEX
ARG PIP_EXTRA_INDEX_URL
ENV PIP_NO_CACHE_DIR=1
COPY requirements-ci.txt /requirements/
COPY requirements/ /requirements/requirements/

ARG PIP_FIND_LINKS
RUN mkdir -p ${PIP_FIND_LINKS} &&  \
    python3 -m pip install pip --upgrade && \
    pip wheel --wheel-dir=${PIP_FIND_LINKS} --no-cache-dir -r /requirements/requirements-ci.txt
#==============================================================================

FROM base_image as SONAR_BUILDER
RUN apt-get update && \
    apt-get install -y --no-install-recommends  \
      unzip \
      curl && \
    rm -rf /var/lib/apt/lists/*
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


FROM wheel_builder as conan_builder
ARG CONAN_USER_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements/requirements_conan.txt /tmp/requirements_conan.txt
RUN pip install --no-cache-dir -r /tmp/requirements_conan.txt cmake
COPY ci/docker/shared/conan/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json
COPY ci/docker/python/linux/jenkins/conan/profile.ini  ${CONAN_USER_HOME}/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py
RUN conan config init

# shared files are needed to run the Build C++ Tests stage
RUN conan install /tmp --build outdated --no-import -pr:b=default && \
    conan install /tmp --build outdated --no-import -pr:b=default -o "*:shared=True" && \
    conan remove "*" -b --src -f && \
    conan remove --locks

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
    chmod -R 777 /.sonar/cache

RUN chmod -R 777 $SONAR_USER_HOME

ENV SONAR_SCANNER_OPTS="-server"

# -----------------------------------------------------------------------------
# Install Doctor memory
# -----------------------------------------------------------------------------
COPY --from=DR_MEMORY_BUILDER /opt/drmemory /opt/drmemory/
RUN ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version

ARG PIP_EXTRA_INDEX_URL
ARG PIP_FIND_LINKS
COPY --from=wheel_builder ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
COPY --from=wheel_builder requirements/ /requirements

RUN python3 -m pip install pip --upgrade && \
    pip install --no-index --no-cache-dir --find-links=${PIP_FIND_LINKS} \
    -r /requirements/requirements-ci.txt

ENV PIP_FIND_LINKS=${PIP_FIND_LINKS}
ENV PIP_NO_CACHE_DIR=1
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