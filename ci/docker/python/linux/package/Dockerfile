ARG CONAN_USER_HOME=/conan
ARG manylinux_image=quay.io/pypa/manylinux2014_x86_64
ARG UV_CACHE_DIR=/.cache/uv
ARG PIP_DOWNLOAD_CACHE=/.cache/pip
FROM ${manylinux_image} AS base

RUN yum install -y openjpeg2-devel ca-certificates
ENV PATH=/opt/python/cp39-cp39/bin:/opt/python/cp38-cp38/bin:/opt/python/cp37-cp37m/bin:/opt/python/cp35-cp35m/bin:$PATH
ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE
RUN mkdir -p ${PIP_DOWNLOAD_CACHE} && \
    chmod -R 777 ${PIP_DOWNLOAD_CACHE} && \
    mkdir -p ${UV_CACHE_DIR} && \
    chmod -R 777 ${UV_CACHE_DIR}

ARG CONAN_USER_HOME
RUN mkdir -p ${CONAN_USER_HOME}/.conan && chmod -R 777 ${CONAN_USER_HOME}

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN python -m pip install pip --upgrade && python -m pip install wheel
# ==============================================================================

FROM base AS conan_builder
COPY requirements-dev.txt /tmp/requirements-dev.txt
ARG CONAN_USER_HOME
ARG TARGETARCH
COPY ci/docker/python/linux/package/conan/$TARGETARCH/profile.ini  $CONAN_USER_HOME/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py
RUN --mount=type=cache,target=${CONAN_USER_HOME}/.conan \
    python3 -m venv venv && \
    . ./venv/bin/activate  && \
    pip install --no-cache $(grep ^uv /tmp/requirements-dev.txt) && \
    uv pip install --no-cache $(grep ^conan /tmp/requirements-dev.txt) && \
    conan config home && \
    conan install /tmp --build outdated --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks &&  \
    deactivate && rm -rf venv
# ==============================================================================

FROM base

ARG TARGETARCH
ARG CONAN_USER_HOME
COPY --from=conan_builder ${CONAN_USER_HOME}/ ${CONAN_USER_HOME}/
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
RUN chmod -R 777 ${CONAN_USER_HOME}