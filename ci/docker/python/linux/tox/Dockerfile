ARG CONAN_USER_HOME=/conan
ARG PIP_FIND_LINKS=/wheels
FROM ubuntu:20.04 as wheel_builder_base
COPY ci/docker/python/linux/tox/apt-packages.txt /tmp/
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    cat /tmp/apt-packages.txt | xargs apt-get -y install

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY37
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt requirements.txt /tmp/
COPY requirements /tmp/requirements
ENV PYTHON=python3.7
RUN $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w ${PIP_FIND_LINKS} --no-cache-dir  \
      -r /tmp/requirements.txt  \
      -r /tmp/requirements-ci.txt  \
      -r /tmp/requirements-extras.txt
RUN $PYTHON -m pip wheel  -w ${PIP_FIND_LINKS} --no-cache-dir wheel

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY38
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt requirements.txt /tmp/
COPY requirements /tmp/requirements
ENV PYTHON=python3.8
RUN $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w ${PIP_FIND_LINKS} --no-cache-dir  \
      -r /tmp/requirements.txt  \
      -r /tmp/requirements-ci.txt  \
      -r /tmp/requirements-extras.txt
RUN $PYTHON -m pip wheel  -w ${PIP_FIND_LINKS} --no-cache-dir wheel

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY39
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt requirements.txt /tmp/
COPY requirements /tmp/requirements
ENV PYTHON=python3.9
RUN $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w ${PIP_FIND_LINKS} --no-cache-dir  \
      -r /tmp/requirements.txt  \
      -r /tmp/requirements-ci.txt  \
      -r /tmp/requirements-extras.txt
RUN $PYTHON -m pip wheel  -w ${PIP_FIND_LINKS} --no-cache-dir wheel
# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY310
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt requirements.txt /tmp/
COPY requirements /tmp/requirements
ENV PYTHON=python3.10
RUN $PYTHON -m ensurepip --upgrade &&  \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w ${PIP_FIND_LINKS} --no-cache-dir  \
      -r /tmp/requirements.txt  \
      -r /tmp/requirements-ci.txt  \
      -r /tmp/requirements-extras.txt
RUN $PYTHON -m pip wheel  -w ${PIP_FIND_LINKS} --no-cache-dir wheel
# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY311
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt requirements.txt /tmp/
COPY requirements /tmp/requirements
ENV PYTHON=python3.11
RUN $PYTHON -m ensurepip --upgrade &&  \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w ${PIP_FIND_LINKS} --no-cache-dir  \
      -r /tmp/requirements.txt  \
      -r /tmp/requirements-ci.txt  \
      -r /tmp/requirements-extras.txt
RUN $PYTHON -m pip wheel  -w ${PIP_FIND_LINKS} --no-cache-dir wheel
# ==============================================================================

FROM wheel_builder_base as conan_builder
RUN pip3 install conan cmake
ARG CONAN_USER_HOME
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
COPY conanfile.py /tmp/conanfile.py
RUN conan config home
RUN conan install /tmp --build outdated --build=openjpeg --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks
# ==============================================================================

FROM wheel_builder_base

ARG CONAN_USER_HOME
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY --from=WHEEL_BUILDER_PY37 ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
COPY --from=WHEEL_BUILDER_PY38 ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
COPY --from=WHEEL_BUILDER_PY39 ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
COPY --from=WHEEL_BUILDER_PY310 ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
COPY --from=WHEEL_BUILDER_PY311 ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
ENV PIP_FIND_LINKS=${PIP_FIND_LINKS}
COPY requirements/ /tmp/requirements
RUN pip3 install wheel
RUN pip3 install -r /tmp/requirements/requirements_tox.txt conan "devpi-client<6.0"
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
ADD conanfile.py /tmp/conanfile.py
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY --from=conan_builder ${CONAN_USER_HOME}/ ${CONAN_USER_HOME}/
RUN conan config home
RUN conan install /tmp --build missing --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks
RUN chmod -R 777 ${CONAN_USER_HOME}
WORKDIR /src
CMD tox --workdir /tmp/tox --recreate
