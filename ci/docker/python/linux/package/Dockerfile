ARG manylinux_image=quay.io/pypa/manylinux2014_x86_64
FROM ${manylinux_image} as base

RUN yum install -y openjpeg2-devel ca-certificates
ENV PATH=/opt/python/cp39-cp39/bin:/opt/python/cp38-cp38/bin:/opt/python/cp37-cp37m/bin:/opt/python/cp35-cp35m/bin:$PATH
RUN mkdir -p /.cache/pip && \
    chmod -R 777 /.cache
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

RUN python -m pip install pip --upgrade && python -m pip install wheel
RUN python --version && python -m pip install conan cmake build
# ==============================================================================
FROM base as PYTHON37_WHEEL_BUILDER
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt /tmp/

RUN PYTHON=python3.7 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir \
        -r /tmp/requirements-ci.txt \
        -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extras.txt
# ==============================================================================
FROM base as PYTHON38_WHEEL_BUILDER
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt /tmp/

RUN PYTHON=python3.8 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir \
        -r /tmp/requirements-ci.txt \
        -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extras.txt
# ==============================================================================

FROM base as PYTHON39_WHEEL_BUILDER
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt /tmp/

# ==============================================================================

RUN PYTHON=python3.9 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir \
        -r /tmp/requirements-ci.txt \
        -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extras.txt

# ==============================================================================
FROM base as conan_builder
RUN pip3 install conan cmake
ENV CONAN_USER_HOME=/conan
COPY ci/docker/shared/conan/remotes.json  $CONAN_USER_HOME/.conan/remotes.json
COPY ci/docker/python/linux/package/conan/profile.ini  $CONAN_USER_HOME/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py
RUN conan config home
RUN conan install /tmp --build outdated --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks
# ==============================================================================

FROM base
ENV PIP_FIND_LINKS=/wheels

COPY --from=PYTHON37_WHEEL_BUILDER /wheels/* $PIP_FIND_LINKS/
RUN python3.7 -m pip install pip --upgrade pip

COPY --from=PYTHON38_WHEEL_BUILDER /wheels/* $PIP_FIND_LINKS/
RUN python3.8 -m pip install pip --upgrade pip

COPY --from=PYTHON39_WHEEL_BUILDER /wheels/* $PIP_FIND_LINKS/
RUN python3.9 -m pip install pip --upgrade pip
ENV CONAN_USER_HOME=/conan
COPY ci/docker/shared/conan/remotes.json  $CONAN_USER_HOME/.conan/remotes.json
COPY ci/docker/python/linux/package/conan/profile.ini  $CONAN_USER_HOME/.conan/profiles/default
ADD conanfile.py /tmp/conanfile.py
COPY --from=conan_builder /conan/ /conan/
RUN conan config home
RUN conan install /tmp --build missing --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks
RUN chmod -R 777 /conan