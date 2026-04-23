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

FROM ${FROM_IMAGE} AS certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} AS installed_applications_base

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

COPY scripts/resources/windows/msvc/visual_studio_config.json c:/setup/config.vsconfig
COPY scripts/resources/windows/msvc/install_msvc.ps1 c:/scripts/install_msvc.ps1
ARG VS_INSTALL_PATH
ARG VS_VERSION="2022"
ARG VS_DevCmdArguments="-arch=amd64"
ARG VS_DevPowershellArguments='-arch=amd64'
RUN c:/scripts/install_msvc.ps1 -InstallPath ${Env:VS_INSTALL_PATH} -VSConfigFile c:/setup/config.vsconfig -DevCmdArguments ${Env:VS_DevCmdArguments} -DevPowershellArguments ${Env:VS_DevPowershellArguments} -VSVersion ${Env:VS_VERSION}; `
    Write-Host "Note: Exporting This layer can take a while."

COPY scripts/resources/windows/scoop c:/scoopinstall
RUN irm get.scoop.sh -outfile 'install.ps1' ; `
    .\install.ps1 -RunAsAdmin ; `
    Remove-Item -Path ".\install.ps1" ; `
    scoop install git ; `
    scoop bucket add versions ; `
    scoop import c:/scoopinstall/scoopfile.json ; `
    scoop cache show ; `
    Write-Host "Cleaning up cache" ;`
    scoop cache clean ; `
    Write-Host "Cleaning up cache - Done" ;`
    Write-Host "Verifying installed packages" ;`
    c:/scoopinstall/verifyenv.ps1 ;`
    Write-Host "Verifying installed packages - Done"

RUN New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

FROM installed_applications_base AS conan_builder
ARG CONAN_HOME

ARG UV_INDEX_URL
ARG UV_EXTRA_INDEX_URL
ENV UV_PROJECT=c:/temp/uv
ENV UV_PROJECT_ENVIRONMENT=c:\temp\uv\.venv
COPY pyproject.toml uv.lock conan.lock conanfile.py ${UV_PROJECT}/
COPY scripts/resources/windows/conan/profile.ini ${CONAN_HOME}/profiles/default
COPY ci/docker/shared/conan/remotes.json ${CONAN_HOME}/remotes.json

ARG CONAN_CENTER_PROXY_V2_URL
ENV UV_FROZEN=1
RUN uv run --only-group conan --with ninja conan profile detect --exist-ok ; `
    if (${env:CONAN_CENTER_PROXY_V2_URL} -ne $(Get-Content -Raw -Path ${Env:CONAN_HOME}\remotes.json)) { `
          Copy-Item -Path "${Env:CONAN_HOME}\remotes.json" -Destination "c:\remotes.json" ; `
          uv run --only-group conan --with ninja conan remote update conan-center --url ${env:CONAN_CENTER_PROXY_V2_URL}; `
    }; `
    uv run --only-group conan --with ninja conan install ${env:UV_PROJECT}/conanfile.py --build missing -pr:b=default --conf=tools.cmake.cmaketoolchain:generator=Ninja -c tools.build:skip_test=True -c tools.graph:skip_test=True ; `
    if ($LASTEXITCODE -ne 0) { `
          throw \"Command 'conan install' failed with exit code: $LASTEXITCODE\"`
    } ;`
    uv run --only-group conan --with ninja conan cache clean "*" -b --source --build --temp ; `
    Remove-Item -Path \"${Env:UV_PROJECT_ENVIRONMENT}\" -Recurse -Force ; `
    uv cache clean --no-progress ; `
    if (${env:CONAN_CENTER_PROXY_V2_URL} -ne $(Get-Content -Raw -Path ${Env:CONAN_HOME}\remotes.json)) { `
      Move-Item -Path "c:\remotes.json" -Destination "${Env:CONAN_HOME}\remotes.json" -Force ;`
    }
# ==============================================================================

FROM installed_applications_base
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG CONAN_USER_HOME
ARG CONAN_HOME
COPY --from=conan_builder ${CONAN_HOME}/ ${CONAN_HOME}/
ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE

RUN New-Item -type directory -path ${Env:PIP_DOWNLOAD_CACHE} -Force | Out-Null ; `
    New-Item -type directory -path ${Env:UV_CACHE_DIR} -Force| Out-Null

ENV CONAN_USER_HOME=${CONAN_USER_HOME}`
    CONAN_HOME=${CONAN_HOME}`
    UV_CACHE_DIR=${UV_CACHE_DIR}`
    PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}
