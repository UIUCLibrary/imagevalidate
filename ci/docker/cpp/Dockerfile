FROM ubuntu:20.04
RUN apt update && apt install -y python3 python3-pip build-essential
RUN python3 -m pip install conan cmake

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

USER user
WORKDIR /home/user
ADD conanfile.py /tmp/conanfile.py
ENV CONAN_USER_HOME=/home/user/
RUN conan config home
RUN conan install /tmp --build  missing --no-import

#=========
ADD --chown=user conanfile.py CMakeLists.txt /home/user/src/
ADD --chown=user uiucprescon/ /home/user/src/uiucprescon/
ADD --chown=user tests/ /home/user/src/tests/
RUN conan install /home/user/src/ -if build
RUN cmake -B build -S src -DCMAKE_TOOLCHAIN_FILE:FILEPATH=/home/user/build/conan_paths.cmake -DCMAKE_VERBOSE_MAKEFILE=True -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=True
#RUN cmake --build build
RUN cmake --build build --target tester
