ARG CONAN_USER_HOME=/conan
ARG manylinux_image=quay.io/pypa/manylinux2014_x86_64
FROM ${manylinux_image} as base

RUN yum install -y openjpeg2-devel ca-certificates
ENV PATH=/opt/python/cp39-cp39/bin:/opt/python/cp38-cp38/bin:/opt/python/cp37-cp37m/bin:/opt/python/cp35-cp35m/bin:$PATH
RUN mkdir -p /.cache/pip && \
    chmod -R 777 /.cache
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

RUN python -m pip install pip --upgrade && python -m pip install wheel
COPY requirements/requirements_conan.txt /tmp/requirements_conan.txt
RUN python --version && python -m pip install -r /tmp/requirements_conan.txt cmake build
# ==============================================================================

FROM base as conan_builder
COPY requirements/requirements_conan.txt /tmp/requirements_conan.txt
RUN pip3 install -r /tmp/requirements_conan.txt cmake
ARG CONAN_USER_HOME
COPY ci/docker/shared/conan/remotes.json  $CONAN_USER_HOME/.conan/remotes.json
ARG TARGETARCH
COPY ci/docker/python/linux/package/conan/$TARGETARCH/profile.ini  $CONAN_USER_HOME/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py
RUN conan config home
RUN conan install /tmp --build outdated --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks
# ==============================================================================

FROM base

RUN python3.8 -m pip install pip --upgrade pip

RUN python3.9 -m pip install pip --upgrade pip

RUN python3.10 -m pip install pip --upgrade pip

ARG TARGETARCH
ARG CONAN_USER_HOME
COPY ci/docker/shared/conan/remotes.json  $CONAN_USER_HOME/.conan/remotes.json
COPY ci/docker/python/linux/package/conan/$TARGETARCH/profile.ini  $CONAN_USER_HOME/.conan/profiles/default
ADD conanfile.py /tmp/conanfile.py
COPY --from=conan_builder ${CONAN_USER_HOME}/ ${CONAN_USER_HOME}/
RUN conan config home
RUN conan install /tmp --build missing --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks
RUN chmod -R 777 ${CONAN_USER_HOME}
