ARG CONAN_USER_HOME=/conan
ARG PIP_FIND_LINKS=/wheels
FROM ubuntu:20.04 as wheel_builder_base
COPY ci/docker/python/linux/tox/apt-packages.txt /tmp/apt-packages.txt
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install -y software-properties-common --no-install-recommends && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    < /tmp/apt-packages.txt xargs apt-get install -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /.cache/pip && \
    chmod -R 777 /.cache
# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY37
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt requirements.txt /tmp/
COPY requirements /tmp/requirements
ENV PYTHON=python3.7
RUN $PYTHON -m venv venv && \
    source ./venv/bin/activate --upgrade-deps && \
    python -m pip install --no-cache-dir wheel==0.37.1 && \
    python -m pip wheel --no-cache-dir -w ${PIP_FIND_LINKS} \
      -r /tmp/requirements.txt  \
      -r /tmp/requirements-ci.txt  \
      -r /tmp/requirements-extras.txt

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY38
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt requirements.txt /tmp/
COPY requirements /tmp/requirements
ENV PYTHON=python3.8
RUN $PYTHON -m venv venv && \
    source ./venv/bin/activate --upgrade-deps && \
    python -m pip install --no-cache-dir wheel==0.37.1 && \
    python -m pip wheel --no-cache-dir -w ${PIP_FIND_LINKS} \
      -r /tmp/requirements.txt  \
      -r /tmp/requirements-ci.txt  \
      -r /tmp/requirements-extras.txt

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY39
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt requirements.txt /tmp/
COPY requirements /tmp/requirements
ENV PYTHON=python3.9
RUN $PYTHON -m venv venv && \
    source ./venv/bin/activate --upgrade-deps && \
    python -m pip install --no-cache-dir wheel==0.37.1 && \
    python -m pip wheel --no-cache-dir -w ${PIP_FIND_LINKS} \
      -r /tmp/requirements.txt  \
      -r /tmp/requirements-ci.txt  \
      -r /tmp/requirements-extras.txt
# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY310
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt requirements.txt /tmp/
COPY requirements /tmp/requirements
ENV PYTHON=python3.10
RUN $PYTHON -m venv venv && \
    source ./venv/bin/activate --upgrade-deps && \
    python -m pip install --no-cache-dir wheel==0.37.1 && \
    python -m pip wheel --no-cache-dir -w ${PIP_FIND_LINKS} \
      -r /tmp/requirements.txt  \
      -r /tmp/requirements-ci.txt  \
      -r /tmp/requirements-extras.txt
# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY311
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt requirements.txt /tmp/
COPY requirements /tmp/requirements
ENV PYTHON=python3.11
RUN $PYTHON -m venv venv && \
    source ./venv/bin/activate --upgrade-deps && \
    python -m pip install --no-cache-dir wheel==0.37.1 && \
    python -m pip wheel --no-cache-dir -w ${PIP_FIND_LINKS} \
      -r /tmp/requirements.txt  \
      -r /tmp/requirements-ci.txt  \
      -r /tmp/requirements-extras.txt
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
