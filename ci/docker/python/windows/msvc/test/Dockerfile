# escape=`
ARG PYTHON_DOCKER_IMAGE_BASE=python:3.7
FROM ${PYTHON_DOCKER_IMAGE_BASE}

RUN certutil -generateSSTFromWU roots.sst ; `
    certutil -addstore -f root roots.sst ; `
    del roots.sst

ENV PIP_EXTRA_INDEX_URL="https://devpi.library.illinois.edu/production/release"

RUN python -m pip install tox
