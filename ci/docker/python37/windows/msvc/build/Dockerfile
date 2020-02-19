# escape=`
ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019
FROM ${FROM_IMAGE}

# Reset the shell.
SHELL ["cmd", "/S", "/C"]
RUN mkdir c:\\TEMP
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

ADD ci/docker/python37/windows/msvc/build/chocolatey/install_choco.ps1 choco/install_choco.ps1
ARG CHOCOLATEY_REPO=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; ./choco/install_choco.ps1 -packageRepo $env:CHOCOLATEY_REPO ; `
    choco source remove -n chocolatey ; choco source add -n=chocolatey_repo -s=\"$env:CHOCOLATEY_REPO\" ; `
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe

ADD ci/docker/python37/windows/msvc/build/chocolatey/packages.config choco/packages.config
RUN choco install -y choco/packages.config --no-progress --stoponfirstfailure;`
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse

ADD ci/docker/python37/windows/msvc/build/startup.bat c:\temp\startup.bat
RUN Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value "c:\temp\startup.bat"
RUN certutil -generateSSTFromWU roots.sst ; `
    certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe

RUN Invoke-WebRequest $Env:PYTHON_INSTALLER_URL -OutFile c:\python-installer.exe ; `
    Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; `
    Remove-Item c:\python-installer.exe -Force

ADD requirements.txt c:\temp\

ENV PIP_EXTRA_INDEX_URL="https://devpi.library.illinois.edu/production/release"

RUN python -m pip install --upgrade pip ; `
    pip install --upgrade setuptools ; `
    pip install wheel pipenv pytest-cov lxml sphinx mypy flake8 tox devpi-client -r c:\temp\requirements.txt
