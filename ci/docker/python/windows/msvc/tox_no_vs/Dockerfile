# escape=`
ARG PIPX_HOME=c:\pipx
ARG UV_CACHE_DIR=c:/users/containeradministrator/appdata/local/uv
ARG PIP_DOWNLOAD_CACHE=c:/users/containeradministrator/appdata/local/pip
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8
ARG UV_EXTRA_INDEX_URL

FROM ${FROM_IMAGE} AS certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} AS BASE_BUILDER

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]
ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
ARG chocolateyVersion
COPY ci/docker/shared/chocolatey/install.ps1 c:/choco/install.ps1
COPY ci/docker/shared/chocolatey/get_latest_chocolatey_url.ps1 c:/choco/get_latest_chocolatey_url.ps1
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
    Remove-Item -Force -Recurse ${Env:TEMP}\*


COPY ci/docker/python/windows/msvc/tox_no_vs/chocolatey/packages.xml c:/choco/packages.config
RUN C:\ProgramData\chocolatey\bin\choco.exe sources ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --verbose c:/choco/packages.config ;`
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    refreshenv ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    if (!(Test-Path 'C:\Program Files\Git\cmd\git.exe')) `
    { `
        throw 'git.exe not found' ; `
    }; `
    Write-Host "Finished install packages with Chocolatey"

ADD ci/docker/shared/chocolatey/python.xml choco/python.config
RUN C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --verbose choco/python.config ;`
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    refreshenv ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    py --list ;`
    py -3.8 --version ; `
    py -3.9 --version ; `
    py -3.10 --version ; `
    py -3.11 --version ; `
    py -3.12 --version ; `
    Write-Host "Installing Python with Chocolatey - Done"


FROM BASE_BUILDER
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY requirements-dev.txt c:/python_requirments/
COPY requirements/ c:/python_requirments/requirements
ARG UV_EXTRA_INDEX_URL
ENV UV_INDEX_STRATEGY=unsafe-best-match
RUN python -m pip install pip --upgrade ; pip install --no-cache-dir -r c:/python_requirments/requirements/requirements_tox.txt

ARG PIP_DOWNLOAD_CACHE
RUN New-Item -type directory -path ${Env:PIP_DOWNLOAD_CACHE} -Force

ENV PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}
ARG PIPX_HOME
ENV PIPX_HOME=${PIPX_HOME}
ENV PIPX_BIN_DIR=${PIPX_HOME}\bin


RUN py -3 -m pip install --no-cache-dir pipx ; `
    py -3 -m pipx ensurepath
RUN py -3 -m pipx install 'devpi-client<7.0'

CMD tox --workdir ${Env:TEMP}\tox\ -vv  --recreate -p=auto
