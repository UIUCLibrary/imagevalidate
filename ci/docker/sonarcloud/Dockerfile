FROM sonarsource/sonar-scanner-cli:latest
RUN apk --no-cache add curl
RUN curl --create-dirs -sSLo $HOME/.sonar/build-wrapper-linux-x86.zip https://sonarcloud.io/static/cpp/build-wrapper-linux-x86.zip && \
    unzip -o $HOME/.sonar/build-wrapper-linux-x86.zip -d $HOME/.sonar/
USER scanner-cli
CMD /bin/sh