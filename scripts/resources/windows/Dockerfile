# escape=`
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8.1

ARG VS_INSTALL_PATH="C:\BuildTools"

# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V1_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.
ARG CONAN_CENTER_PROXY_V1_URL

ARG CONAN_USER_HOME=C:/Users/ContainerAdministrator

ARG UV_CACHE_DIR=c:/users/containeradministrator/appdata/local/uv
ARG PIP_DOWNLOAD_CACHE=c:/users/containeradministrator/appdata/local/pip

ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG chocolateyVersion

FROM ${FROM_IMAGE} AS certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} AS CHOCOLATEY_BASE

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

COPY scripts/resources/windows/msvc/visual_studio_config.json c:/setup/config.vsconfig
COPY scripts/resources/windows/msvc/install_msvc.ps1 c:/scripts/install_msvc.ps1
ARG VS_INSTALL_PATH
ARG VS_VERSION="2022"
ARG VS_DevCmdArguments="-arch=amd64"
ARG VS_DevPowershellArguments='-arch=amd64'
RUN c:/scripts/install_msvc.ps1 -InstallPath ${Env:VS_INSTALL_PATH} -VSConfigFile c:/setup/config.vsconfig -DevCmdArguments ${Env:VS_DevCmdArguments} -DevPowershellArguments ${Env:VS_DevPowershellArguments} -VSVersion ${Env:VS_VERSION}; `
    Write-Host "Note: Exporting This layer can take a while."

ARG CHOCOLATEY_SOURCE
ARG ChocolateyEnvironmentDebug=false
ARG chocolateyVersion
COPY scripts/resources/windows/chocolatey/install.ps1 c:/choco/install.ps1
COPY scripts/resources/windows/chocolatey/get_latest_chocolatey_url.ps1 c:/choco/get_latest_chocolatey_url.ps1
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


COPY scripts/resources/windows/chocolatey/packages.config choco/packages.config
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
COPY scripts/resources/windows/conan/profile.ini ${CONAN_USER_HOME}/.conan/profiles/default

ARG CONAN_CENTER_PROXY_V1_URL

RUN uvx --constraint=requirements-dev.txt --with cmake --index-strategy=unsafe-best-match conan config home ; `
    { `
          Copy-Item -Path "${Env:CONAN_USER_HOME}\.conan\remotes.json" -Destination "c:\remotes.json" ; `
          uvx --constraint=requirements-dev.txt conan remote remove conan-center ; `
          uvx --constraint=requirements-dev.txt conan remote add conan-center-proxy ${Env:CONAN_CENTER_PROXY_V1_URL} ; `
    }; `
    uvx --constraint=requirements-dev.txt --with cmake --index-strategy=unsafe-best-match conan install c:/temp/ --build missing --no-import -pr:b=default ; `
    uvx --constraint=requirements-dev.txt --with cmake --index-strategy=unsafe-best-match conan remove "*" -b --src -f ; `
    uvx --constraint=requirements-dev.txt --with cmake --index-strategy=unsafe-best-match conan remove --lock ; `
    uv cache clean --no-progress ; `
    if ( -not ([string]::IsNullOrEmpty($Env:CONAN_CENTER_PROXY_V1_URL ))) `
    {`
      Move-Item -Path "c:\remotes.json" -Destination "${Env:CONAN_USER_HOME}\.conan\remotes.json" -Force ;`
    }
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
