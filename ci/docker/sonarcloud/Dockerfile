FROM sonarsource/sonar-scanner-cli:latest
RUN apk --no-cache add curl
USER scanner-cli
RUN curl --create-dirs -sSLo $HOME/.sonar/build-wrapper-linux-x86.zip https://sonarcloud.io/static/cpp/build-wrapper-linux-x86.zip && \
    mkdir -p /home/scanner-cli/.sonar/ && \
    unzip -o $HOME/.sonar/build-wrapper-linux-x86.zip -d /home/scanner-cli/.sonar/
ENV PATH=/home/scanner-cli/.sonar/build-wrapper-linux-x86:$PATH
CMD /bin/sh