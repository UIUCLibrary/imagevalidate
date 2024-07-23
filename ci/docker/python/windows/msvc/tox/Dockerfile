# escape=`
ARG PIPX_HOME=c:\pipx
ARG VS_INSTALL_PATH="C:\BuildTools"
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG UV_CACHE_DIR=c:/users/containeradministrator/appdata/local/uv
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019
FROM ${FROM_IMAGE} as certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} as BASE_BUILDER

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

COPY ci/docker/python/windows/msvc/tox/msvc/startup.bat c:/startup/startup.bat
COPY ci/docker/python/windows/msvc/tox/msvc/visual_studio_config.json c:/setup/config.vsconfig
COPY ci/docker/python/windows/msvc/tox/msvc/install_msvc.ps1 c:/scripts/install_msvc.ps1
ARG VS_INSTALL_PATH

RUN c:/scripts/install_msvc.ps1 ${Env:VS_INSTALL_PATH} c:/setup/config.vsconfig; `
    Get-ChildItem C:\Users\ContainerAdministrator\AppData\Local\Temp | Remove-Item -Recurse -Force -Verbose
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


ADD ci/docker/shared/chocolatey/packages.config choco/packages.config
ADD ci/docker/shared/verifyenv.ps1 verifyenv.ps1
RUN C:\ProgramData\chocolatey\bin\choco.exe sources ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --verbose choco/packages.config ;`
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    refreshenv ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    if (!(Test-Path 'C:\Program Files\Git\cmd\git.exe')) `
    { `
        throw 'git.exe not found' ; `
    }; `
    Write-Host "Finished install packages with Chocolatey" ;`
    Write-Host "Verifying installed packages" ;`
    $env:Path = [System.Environment]::GetEnvironmentVariable(\"Path\",\"Machine\") + \";\" + [System.Environment]::GetEnvironmentVariable(\"Path\",\"User\") ; `
    ./verifyenv.ps1

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
RUN New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

FROM BASE_BUILDER as CONAN_BUILDER
ARG CONAN_USER_HOME
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements requirements
RUN python -m pip install --upgrade pip ; `
    pip install wheel ; `
    pip install -r requirements/requirements_conan.txt cmake
COPY conanfile.py c:/temp/conanfile.py
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
COPY ci/docker/python/windows/msvc/shared/profile.ini ${CONAN_USER_HOME}/.conan/profiles/default
SHELL ["cmd", "/S", "/C" ]
RUN conan config home
RUN conan install c:/temp/ --build missing --build openjpeg --no-import -pr:b=default && `
    conan remove "*" -b --src -f && `
    conan remove --lock
# ==============================================================================

FROM BASE_BUILDER
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst
COPY requirements requirements
RUN python -m pip install pip --upgrade ; `
    pip install wheel ; `
    pip install --no-cache-dir -r requirements/requirements_conan.txt
ARG CONAN_USER_HOME
COPY --from=CONAN_BUILDER ${CONAN_USER_HOME}/.conan/ ${CONAN_USER_HOME}/.conan/
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY conanfile.py c:/temp/conanfile.py
RUN conan config home
RUN conan install c:/temp/ --build missing --no-import  -pr:b=default; `
    conan remove "*" -b --src -f ; `
    conan remove --locks  ; `
    py -3.8 -m pip install --no-cache-dir pip --upgrade ; `
    py -3.8 -m pip install --no-cache-dir build ; `
    py -3.9 -m pip install --no-cache-dir pip --upgrade ;  `
    py -3.9 -m pip install --no-cache-dir build; `
    py -3.10 -m pip install --no-cache-dir pip --upgrade ;  `
    py -3.10 -m pip install --no-cache-dir build; `
    py -3.11 -m pip install --no-cache-dir pip --upgrade ;  `
    py -3.11 -m pip install --no-cache-dir build; `
    py -3.12 -m pip install --no-cache-dir pip --upgrade ;  `
    py -3.12 -m pip install --no-cache-dir build

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY requirements-dev.txt c:/python_requirments/
COPY requirements/ c:/python_requirments/requirements
ARG UV_EXTRA_INDEX_URL
ENV UV_INDEX_STRATEGY=unsafe-best-match
RUN python -m pip install pip --upgrade ; pip install --no-cache-dir -r c:/python_requirments/requirements/requirements_tox.txt build

ARG PIP_DOWNLOAD_CACHE
RUN New-Item -type directory -path ${Env:PIP_DOWNLOAD_CACHE} -Force

ENV PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}
ARG PIPX_HOME
ENV PIPX_HOME=${PIPX_HOME}
ENV PIPX_BIN_DIR=${PIPX_HOME}\bin


RUN py -3 -m pip install --no-cache-dir pipx ; `
    py -3 -m pipx ensurepath
RUN py -3 -m pipx install 'devpi-client<7.0'


ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE

ENV UV_CACHE_DIR=${UV_CACHE_DIR}
ENV PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}

WORKDIR C:/src
CMD tox --workdir ${Env:TEMP}\tox\ -vv  --recreate -p=auto
