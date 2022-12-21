#ARG PYTHON_VERSION=3.8
FROM ubuntu:20.04 as base_image
ARG TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && \
    apt install -y \
        ninja-build \
        ccache \
        python3 \
        python3-pip \
        python3-venv \
        ca-certificates \
        software-properties-common && \
    rm -rf /var/lib/apt/lists/*
ARG SONAR_SCANNER_VERSION=4.6.2.2472

#==============================================================================
FROM base_image as DR_MEMORY_BUILDER
RUN apt-get update && apt install -y wget
WORKDIR /drmemory
RUN wget --no-verbose https://github.com/DynamoRIO/drmemory/releases/download/release_2.3.0/DrMemory-Linux-2.3.0-1.tar.gz && \
    mkdir -p /opt/drmemory && tar xzf DrMemory-Linux-2.3.0-1.tar.gz -C /opt/drmemory --strip-components=1 && \
    ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version

FROM base_image as wheel_builder

RUN apt update && apt install -y ninja-build \
    && rm -rf /var/lib/apt/lists/*

ARG PYTHON_INDEX
ARG PIP_EXTRA_INDEX_URL
ENV PIP_NO_CACHE_DIR=1
ADD requirements.txt ci/docker/shared/python/requirements-ci.txt /requirements/
COPY requirements/ /requirements/requirements/
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade setuptools && \
    python3 -m pip install wheel && \
    python3 -m pip wheel --wheel-dir=/wheels  \
        -r /requirements/requirements.txt \
        -r /requirements/requirements-ci.txt

#==============================================================================

FROM base_image as SONAR_BUILDER
RUN apt-get update && \
    apt-get install -y unzip curl && \
    rm -rf /var/lib/apt/lists/*
ARG SONAR_SCANNER_VERSION=4.6.2.2472
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
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN pip install conan cmake
ENV CONAN_USER_HOME=/conan
COPY ci/docker/shared/conan/remotes.json $CONAN_USER_HOME/.conan/remotes.json
COPY ci/docker/python/linux/build/conan/profile.ini  $CONAN_USER_HOME/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py
RUN conan config init

# shared files are needed to run the Build C++ Tests stage
RUN conan install /tmp --build outdated --no-import  && \
    conan install /tmp --build outdated --no-import -o "*:shared=True" && \
    conan remove "*" -b --src -f && \
    conan remove --locks

FROM base_image

RUN apt update && apt install -y ninja-build ccache clang-tidy cppcheck && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Install sonar-scanner and build-wrapper
# -----------------------------------------------------------------------------

COPY --from=SONAR_BUILDER /opt/sonar /opt/sonar/
COPY --from=SONAR_BUILDER /opt/build-wrapper-linux-x86 /opt/build-wrapper-linux-x86/
ARG SONAR_SCANNER_VERSION=4.6.2.2472
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



COPY --from=wheel_builder /wheels /wheels/

ADD requirements.txt ci/docker/shared/python/requirements-ci.txt /requirements/
COPY requirements/ /requirements/requirements/
#RUN python -m pip install --upgrade pip && \
#    pip install --upgrade setuptools && \
#    pip install wheel
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade wheel && \
    python3 -m pip install --no-index --find-links=/wheels  \
            -r /requirements/requirements.txt -r /requirements/requirements-ci.txt

ENV PIP_FIND_LINKS=/wheels
ENV PIP_NO_CACHE_DIR=1
ENV CONAN_USER_HOME=/conan
COPY --from=conan_builder /conan/.conan/ $CONAN_USER_HOME/.conan/
COPY ci/docker/shared/conan/remotes.json  $CONAN_USER_HOME/.conan/remotes.json
COPY ci/docker/python/linux/build/conan/profile.ini  $CONAN_USER_HOME/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py
RUN conan config home
RUN conan install /tmp --build outdated --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    chmod -R 777 /conan
