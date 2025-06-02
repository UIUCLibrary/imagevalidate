ARG CONAN_USER_HOME=/conan

# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V1_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.
ARG CONAN_CENTER_PROXY_V1_URL

ARG manylinux_image=quay.io/pypa/manylinux2014_x86_64
ARG UV_CACHE_DIR=/.cache/uv
ARG PIP_DOWNLOAD_CACHE=/.cache/pip
FROM ${manylinux_image} AS base

# ==============================================================================
RUN --mount=type=cache,target=/var/cache/yum \
    yum install -y lndir

# This needed to use uvx with --constraint option
RUN --mount=type=cache,target=/path/to/pipx/cache \
    pipx install "uv>=0.6.5" --force

FROM base AS conan_builder
COPY requirements-dev.txt /tmp/requirements-dev.txt
ARG CONAN_USER_HOME
ARG TARGETARCH
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG UV_EXTRA_INDEX_URL
ARG UV_INDEX_URL

COPY ci/docker/shared/conan/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json
COPY contrib/docker/package_for_linux/conan/$TARGETARCH/profile.ini  $CONAN_USER_HOME/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py

ARG CONAN_CENTER_PROXY_V1_URL
ARG UV_CACHE_DIR=/root/.cache/uv
RUN --mount=type=cache,target=${UV_CACHE_DIR} \
    uvx --index-strategy unsafe-best-match --constraint /tmp/requirements-dev.txt --with cmake conan config home && \
    if [ -n "${CONAN_CENTER_PROXY_V1_URL}" ]; then \
        echo 'Using a proxy for conan center' && \
        cp ${CONAN_USER_HOME}/.conan/remotes.json /tmp/remotes.json && \
        uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remote remove conan-center && \
        uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remote add conan-center ${CONAN_CENTER_PROXY_V1_URL}; \
    fi && \
    uvx --index-strategy unsafe-best-match --constraint /tmp/requirements-dev.txt --with cmake conan install /tmp --build outdated --no-import  && \
    uvx --index-strategy unsafe-best-match --constraint /tmp/requirements-dev.txt --with cmake conan remove "*" -b --src -f && \
    uvx --index-strategy unsafe-best-match --constraint /tmp/requirements-dev.txt --with cmake conan remove --locks && \
    if [ -n "${CONAN_CENTER_PROXY_V1_URL}" ]; then \
        mv -f /tmp/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json; \
    fi
# ==============================================================================

FROM base

ARG CONAN_USER_HOME
COPY --from=conan_builder ${CONAN_USER_HOME}/ ${CONAN_USER_HOME}/
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE
RUN chmod -R 777 ${CONAN_USER_HOME} && \
    mkdir -p ${PIP_DOWNLOAD_CACHE} && \
    chmod -R 777 ${PIP_DOWNLOAD_CACHE} && \
    mkdir -p ${UV_CACHE_DIR} && \
    chmod -R 777 ${UV_CACHE_DIR}
