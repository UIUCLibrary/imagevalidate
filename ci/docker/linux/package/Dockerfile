ARG CONAN_USER_HOME=/conan
ARG manylinux_image=quay.io/pypa/manylinux2014_x86_64
ARG UV_CACHE_DIR=/.cache/uv
ARG PIP_DOWNLOAD_CACHE=/.cache/pip
FROM ${manylinux_image} AS base

RUN yum install -y openjpeg2-devel ca-certificates

# ==============================================================================

FROM base AS conan_builder
COPY requirements-dev.txt /tmp/requirements-dev.txt
ARG CONAN_USER_HOME
ARG TARGETARCH
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG UV_EXTRA_INDEX_URL
ARG UV_INDEX_URL

COPY ci/docker/linux/package/conan/$TARGETARCH/profile.ini  $CONAN_USER_HOME/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py
ARG UV_CACHE_DIR=/root/.cache/uv
RUN --mount=type=cache,target=${UV_CACHE_DIR} \
    uvx --index-strategy unsafe-best-match --with-requirements /tmp/requirements-dev.txt conan config home && \
    uvx --index-strategy unsafe-best-match --with-requirements /tmp/requirements-dev.txt conan install /tmp --build outdated --no-import  && \
    uvx --index-strategy unsafe-best-match --with-requirements /tmp/requirements-dev.txt conan remove "*" -b --src -f && \
    uvx --index-strategy unsafe-best-match --with-requirements /tmp/requirements-dev.txt conan remove --locks
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