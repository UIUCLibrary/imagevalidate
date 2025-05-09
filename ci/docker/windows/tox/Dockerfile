# escape=`
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8.1

ARG VS_INSTALL_PATH="C:\BuildTools"

ARG CONAN_USER_HOME=C:/Users/ContainerAdministrator

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG PIP_DOWNLOAD_CACHE=c:/users/containeradministrator/appdata/local/pip
ARG UV_CACHE_DIR=c:/users/containeradministrator/appdata/local/uv

ARG PIPX_HOME=c:\pipx

ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG chocolateyVersion

FROM ${FROM_IMAGE} AS certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} AS BASE_BUILDER

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

COPY ci/docker/windows/tox/msvc/startup.bat c:/startup/startup.bat
COPY ci/docker/windows/tox/msvc/visual_studio_config.json c:/setup/config.vsconfig
COPY ci/docker/windows/tox/msvc/install_msvc.ps1 c:/scripts/install_msvc.ps1
ARG VS_INSTALL_PATH

RUN c:/scripts/install_msvc.ps1 ${Env:VS_INSTALL_PATH} c:/setup/config.vsconfig; `
    Get-ChildItem C:\Users\ContainerAdministrator\AppData\Local\Temp | Remove-Item -Recurse -Force -Verbose

FROM BASE_BUILDER AS CHOCOLATEY_BASE

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

ARG CHOCOLATEY_SOURCE
ARG ChocolateyEnvironmentDebug=false
ARG chocolateyVersion
COPY ci/docker/windows/tox/chocolatey/install.ps1 c:/choco/install.ps1
COPY ci/docker/windows/tox/chocolatey/get_latest_chocolatey_url.ps1 c:/choco/get_latest_chocolatey_url.ps1
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    $chocolateyDownloadUrl = c:/choco/get_latest_chocolatey_url.ps1 -packageRepo $env:CHOCOLATEY_SOURCE; `
    c:/choco/install.ps1 -ChocolateyDownloadUrl $chocolateyDownloadUrl;`
    if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
    { `
        Write-Host "Adding $env:CHOCOLATEY_SOURCE to chocolatey sources" ; `
        choco source add -n=CHOCOLATEY_SOURCE --priority=1 -s=\"${env:CHOCOLATEY_SOURCE}\"; `
    }; `
    Write-Host "Disabling Showing Download Progress" ; `
    choco feature disable -n=showDownloadProgress ; `
    choco cache remove --confirm


COPY ci/docker/windows/tox/chocolatey/packages.config choco/packages.config
RUN C:\ProgramData\chocolatey\bin\choco.exe sources ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --verbose choco/packages.config ;`
    refreshenv ; `
    choco cache remove --confirm;`
    if (!(Test-Path 'C:\Program Files\nasm\nasm.exe')) `
    { `
        throw 'nasm.exe not found' ; `
    }; `
    Write-Host "Finished install packages with Chocolatey"


RUN New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

FROM CHOCOLATEY_BASE AS CONAN_BUILDER
ARG CONAN_USER_HOME

ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL
ARG UV_INDEX_URL
ARG UV_EXTRA_INDEX_URL

COPY requirements-dev.txt requirements-dev.txt
COPY conanfile.py c:/temp/conanfile.py
COPY ci/docker/windows/tox/conan/profile.ini ${CONAN_USER_HOME}/.conan/profiles/default
SHELL ["cmd", "/S", "/C" ]
RUN uvx --with-requirements requirements-dev.txt --index-strategy=unsafe-best-match conan config home && `
    uvx --with-requirements requirements-dev.txt --index-strategy=unsafe-best-match conan install c:/temp/ --build missing --build openjpeg --no-import -pr:b=default && `
    uvx --with-requirements requirements-dev.txt --index-strategy=unsafe-best-match conan remove "*" -b --src -f && `
    uvx --with-requirements requirements-dev.txt --index-strategy=unsafe-best-match conan remove --lock && `
    uv cache clean --no-progress
# ==============================================================================

FROM CHOCOLATEY_BASE
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG CONAN_USER_HOME
COPY --from=CONAN_BUILDER ${CONAN_USER_HOME}/.conan/ ${CONAN_USER_HOME}/.conan/
ENV CONAN_USER_HOME=${CONAN_USER_HOME}

ENV UV_INDEX_STRATEGY=unsafe-best-match

ARG UV_CACHE_DIR
ENV UV_CACHE_DIR=${UV_CACHE_DIR}

ARG PIP_DOWNLOAD_CACHE
ENV PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}

RUN New-Item -type directory -path ${Env:PIP_DOWNLOAD_CACHE} -Force | Out-Null ; `
    New-Item -type directory -path ${Env:UV_CACHE_DIR} -Force| Out-Null


WORKDIR C:/src
CMD tox --workdir ${Env:TEMP}\tox\ -vv  --recreate -p=auto
