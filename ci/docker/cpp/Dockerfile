FROM ubuntu:20.04
RUN apt update && apt install -y python3 python3-pip build-essential ninja-build
RUN python3 -m pip install conan cmake

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

USER user
WORKDIR /home/user
COPY --chown=user:user ci/docker/shared/conan/remotes.json /home/user/.conan/remotes.json
ENV CONAN_USER_HOME=/home/user/
#RUN ls /home/user/.conan
RUN conan profile new default --detect
RUN conan config home
#RUN ls /home/user/.conan
#ARG CONAN_CMAKE_GENERATOR=Ninja
COPY conanfile.py /tmp/conanfile.py
RUN conan install /tmp --build missing --no-import && \
    conan remove --locks && \
    conan remove "*" -b --src -f
#=========
ADD --chown=user conanfile.py CMakeLists.txt /home/user/src/
ADD --chown=user uiucprescon/ /home/user/src/uiucprescon/
ADD --chown=user tests/ /home/user/src/tests/
WORKDIR /home/user/
RUN conan install ./src -if build
#RUN which make && which ninja
#RUN cmake ..
#RUN cmake .  -DCMAKE_TOOLCHAIN_FILE:FILEPATH=/home/user/build/conan_paths.cmake  -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true
#RUN cmake ..  -DCMAKE_TOOLCHAIN_FILE:FILEPATH=/home/user/build/conan_paths.cmake  -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true
RUN cmake -S src -B build  -DCMAKE_TOOLCHAIN_FILE:FILEPATH=/home/user/build/conan_paths.cmake  -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true
##RUN cmake --build build
RUN cmake --build build --target tester
