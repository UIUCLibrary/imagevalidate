ARG PYTHON_VERSION=3.8

FROM python:${PYTHON_VERSION} as wheel_builder

RUN apt update && apt install -y ninja-build \
    && rm -rf /var/lib/apt/lists/*

ARG PYTHON_INDEX=https://devpi.library.illinois.edu/production/release
ENV PIP_EXTRA_INDEX_URL=${PYTHON_INDEX}
ENV PIP_NO_CACHE_DIR=1
ADD requirements.txt ci/docker/shared/python/requirements-ci.txt /requirements/
RUN python -m pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install wheel && \
    pip wheel --wheel-dir=/wheels  \
        -r /requirements/requirements.txt \
        -r /requirements/requirements-ci.txt \
         -i ${PYTHON_INDEX}

FROM wheel_builder as conan_builder
RUN pip install conan cmake
COPY --chown=user:user ci/docker/shared/conan/remotes.json  /home/user/.conan/remotes.json
COPY --chown=user:user ci/docker/shared/conan/profile.ini  /home/user/profiles/default
USER user
WORKDIR /home/user
COPY conanfile.py /tmp/conanfile.py
RUN conan config home
RUN conan install /tmp --build outdated --build=openjpeg --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks

FROM python:${PYTHON_VERSION}

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

RUN apt update && apt install -y ninja-build ccache && \
    rm -rf /var/lib/apt/lists/*

ENV PIP_EXTRA_INDEX_URL="https://devpi.library.illinois.edu/production/release"

RUN python -m pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install wheel

COPY --from=wheel_builder /wheels /wheels/

ADD requirements.txt ci/docker/shared/python/requirements-ci.txt /requirements/
RUN pip install --no-index --find-links=/wheels  \
        -r /requirements/requirements.txt --pre && \
    pip install --no-index --find-links=/wheels  \
        -r /requirements/requirements-ci.txt

ENV PIP_FIND_LINKS=/wheels
ENV PIP_NO_CACHE_DIR=1
COPY --from=conan_builder --chown=user:user /home/user/.conan/ /home/user/.conan/
COPY --chown=user:user ci/docker/shared/conan/remotes.json  /home/user/.conan/remotes.json
COPY --chown=user:user ci/docker/shared/conan/profile.ini  /home/user/profiles/default
USER user
WORKDIR /home/user
#COPY --chown=user:user ci/docker/shared/conan/remotes.json /home/user/.conan/remotes.json
ENV CONAN_USER_HOME=/home/user/
COPY conanfile.py /tmp/conanfile.py
RUN conan config home
RUN conan install /tmp --build outdated --build=openjpeg --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks