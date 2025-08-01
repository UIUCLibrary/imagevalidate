# escape=`
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8.1

ARG VS_INSTALL_PATH="C:\BuildTools"

# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V2_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.
ARG CONAN_CENTER_PROXY_V2_URL=https://center2.conan.io

ARG CONAN_USER_HOME=C:/Users/ContainerAdministrator
ARG CONAN_HOME=${CONAN_USER_HOME}/.conan2

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
ARG CONAN_HOME

ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL
ARG UV_INDEX_URL
ARG UV_EXTRA_INDEX_URL

COPY requirements-dev.txt c:/temp/requirements-dev.txt
COPY conanfile.py c:/temp/conanfile.py
COPY scripts/resources/windows/conan/profile.ini ${CONAN_HOME}/profiles/default
COPY ci/docker/shared/conan/remotes.json ${CONAN_HOME}/remotes.json
ARG CONAN_CENTER_PROXY_V2_URL
ENV UV_INDEX_STRATEGY=unsafe-best-match`
    UV_CONSTRAINT=c:/temp/requirements-dev.txt
RUN uvx --with cmake conan profile detect --exist-ok ; `
    if (${env:CONAN_CENTER_PROXY_V2_URL} -ne $(Get-Content -Raw -Path ${Env:CONAN_HOME}\remotes.json)) { `
          Copy-Item -Path "${Env:CONAN_HOME}\remotes.json" -Destination "c:\remotes.json" ; `
          uvx --with cmake conan remote update conan-center --url ${env:CONAN_CENTER_PROXY_V2_URL}; `
    }; `
    uvx --with cmake conan install c:/temp/ --build missing -pr:b=default ; `
    if ($LASTEXITCODE -ne 0) { `
          throw \"Command 'conan install' failed with exit code: $LASTEXITCODE\"`
    } ;`
    uvx --with cmake conan cache clean "*" -b --source --build --temp ; `
    uv cache clean --no-progress ; `
    if (${env:CONAN_CENTER_PROXY_V2_URL} -ne $(Get-Content -Raw -Path ${Env:CONAN_HOME}\remotes.json)) { `
      Move-Item -Path "c:\remotes.json" -Destination "${Env:CONAN_HOME}\remotes.json" -Force ;`
    }
# ==============================================================================

FROM CHOCOLATEY_BASE
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG CONAN_USER_HOME
ARG CONAN_HOME
COPY --from=CONAN_BUILDER ${CONAN_HOME}/ ${CONAN_HOME}/
ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE

RUN New-Item -type directory -path ${Env:PIP_DOWNLOAD_CACHE} -Force | Out-Null ; `
    New-Item -type directory -path ${Env:UV_CACHE_DIR} -Force| Out-Null

ENV CONAN_USER_HOME=${CONAN_USER_HOME}`
    CONAN_HOME=${CONAN_HOME}`
    UV_INDEX_STRATEGY=unsafe-best-match`
    UV_CACHE_DIR=${UV_CACHE_DIR}`
    PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}

