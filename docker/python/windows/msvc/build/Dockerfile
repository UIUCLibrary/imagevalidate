# escape=`
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8

FROM ${FROM_IMAGE} as certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE}

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

ADD ci/docker/shared/chocolatey/install_choco.ps1 choco/install_choco.ps1
ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    ./choco/install_choco.ps1 -packageRepo $env:CHOCOLATEY_SOURCE ; `
    if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
    { `
        Write-Host "Adding $env:CHOCOLATEY_SOURCE to chocolatey sources" ; `
        choco source add -n=CHOCOLATEY_SOURCE --priority=1 -s=\"$env:CHOCOLATEY_SOURCE\" ; `
        choco source remove -n chocolatey ; `
    }; `
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe

ADD ci/docker/shared/chocolatey/packages.config choco/packages.config
RUN choco sources ; `
    choco install -y choco/packages.config --no-progress --stoponfirstfailure; `
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ;`
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    if (!(Test-Path 'C:\Program Files\CMake\bin\cmake.exe')) `
    { `
        throw 'cmake.exe not found' ; `
    }; `
    if (!(Test-Path 'C:\Program Files\Git\cmd\git.exe')) `
    { `
        throw 'git.exe not found' ; `
    }; `
    if (! (Test-Path 'C:\BuildTools\Common7\Tools\VsDevCmd.bat')) `
    { `
        throw 'VsDevCmd.bat not found' ; `
    }; `
    Write-Host "Finished install packages with Chocolatey"


ADD ci/docker/shared/startup.bat c:\temp\startup.bat
RUN Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value "c:\temp\startup.bat"

COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe
RUN Invoke-WebRequest $Env:PYTHON_INSTALLER_URL -OutFile c:\python-installer.exe ; `
    Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; `
    Remove-Item c:\python-installer.exe -Force

ENV PIP_EXTRA_INDEX_URL="https://devpi.library.illinois.edu/production/release"
RUN python -m pip install --upgrade pip ; `
    pip install --upgrade setuptools ; `
    pip install wheel

ADD requirements.txt ci/docker/shared/python/requirements-ci.txt c:\temp\

RUN pip wheel --wheel-dir c:/wheels/ `
    -r c:\temp\requirements.txt `
    -r c:\temp\requirements-ci.txt

RUN pip install --no-index  --find-links=c:\wheels\ `
    -r c:\temp\requirements.txt `
    -r c:\temp\requirements-ci.txt

ENV PIP_FIND_LINKS=c:\wheels\