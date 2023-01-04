# escape=`

ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8
FROM ${FROM_IMAGE} as certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} as BASE_BUILDER

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]
ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
ADD ci/docker/shared/chocolatey/install_choco.ps1 choco/install_choco.ps1
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    ./choco/install_choco.ps1 -packageRepo $env:CHOCOLATEY_SOURCE ; `
    if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
    { `
        Write-Host "Adding $env:CHOCOLATEY_SOURCE to chocolatey sources" ; `
        choco source add -n=CHOCOLATEY_SOURCE --priority=1 -s=\"$env:CHOCOLATEY_SOURCE\"; `
        choco source remove -n=chocolatey ;`
    }; `
    Write-Host "Disabling Showing Download Progress" ; `
    choco feature disable -n=showDownloadProgress ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\*



ADD ci/docker/shared/chocolatey/packages.config choco/packages.config
RUN C:\ProgramData\chocolatey\bin\choco.exe sources ; `
    C:\ProgramData\chocolatey\bin\choco.exe install -y --stoponfirstfailure --no-progress --verbose choco/packages.config ;`
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    refreshenv ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    if (!(Test-Path 'C:\Program Files\Git\cmd\git.exe')) `
    { `
        throw 'git.exe not found' ; `
    }; `
    Write-Host "Finished install packages with Chocolatey"

ARG PYTHON_37_VERSION=3.7.9
ARG PYTHON_38_VERSION=3.8.10
ARG PYTHON_39_VERSION=3.9.13
ARG PYTHON_310_VERSION=3.10.8
ARG PYTHON_311_VERSION=3.11.0
RUN $PYTHON_VERSIONS = @(${Env:PYTHON_37_VERSION}, ${Env:PYTHON_38_VERSION}, ${Env:PYTHON_39_VERSION}, ${Env:PYTHON_310_VERSION}, ${Env:PYTHON_311_VERSION} ) ; `
    foreach( $PYTHON_VERSION in $PYTHON_VERSIONS ){ `
        Write-Host "Installing Python $PYTHON_VERSION with Chocolatey" ; `
        $process = start-process -NoNewWindow -PassThru -FilePath C:\ProgramData\chocolatey\bin\choco.exe -ArgumentList 'install -y --stoponfirstfailure --no-progress --verbose python3', "--version=$PYTHON_VERSION", "-my" -Wait ;`
        if ( $process.ExitCode -eq 0) `
        { `
            Write-Host "Installing Python $PYTHON_VERSION with Chocolatey - Done" ; `
        } else { `
            throw "Installing packages with Chocolatey - Failed with exit code ($process.ExitCode)" ;  `
        };`
        & py --list ;`
        $PYTHON_VERSION -match '^(?<major>[0-9]).(?<minor>([0-9]{1,2}))' ; `
        $VER_SHORT = $Matches.major + '.' + $Matches.minor ; `
        Write-Host "Testing Python $VER_SHORT installed" ; `
        & py -$VER_SHORT --version > $null;`
        if ($LastExitCode -eq 0) { `
            Write-Host "Testing Python $VER_SHORT installed - Success " ;`
        } else { `
            Write-Host "Testing Python $VER_SHORT installed - Failed " ;`
#            Get-ChildItem c:\Python311 ; `
            & py --list ;`
            Write-Error 'Error testing python';`
        };`
    } ; `
    Remove-Item C:\Users\ContainerAdministrator\AppData\Local\Temp\chocolatey -Recurse ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\* ; `
    py --list ;`
    py -3.7 --version ;  `
    py -3.8 --version ; `
    py -3.9 --version ; `
    py -3.10 --version ; `
    py -3.11 --version ; `
    Write-Host "Installing Python with Chocolatey - Done!"

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY37
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt c:/requirements/
COPY requirements c:/requirements/requirements
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.7
RUN py -m pip install --upgrade pip wheel && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir `
      -r c:/requirements/requirements-ci.txt  `
      -r c:/requirements/requirements-extras.txt  `
      -r c:/requirements/requirements.txt
RUN py -m pip wheel -w c:\wheels\ --no-cache-dir wheel
# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY38
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt c:/requirements/
COPY requirements c:/requirements/requirements
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.8
RUN py -m pip install --upgrade pip wheel && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir `
      -r c:/requirements/requirements-ci.txt  `
      -r c:/requirements/requirements-extras.txt  `
      -r c:/requirements/requirements.txt
RUN py -m pip wheel -w c:\wheels\ --no-cache-dir wheel

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY39
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt c:/requirements/
COPY requirements c:/requirements/requirements
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.9
RUN py -m pip install --upgrade pip wheel && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir `
      -r c:/requirements/requirements-ci.txt  `
      -r c:/requirements/requirements-extras.txt  `
      -r c:/requirements/requirements.txt
RUN py -m pip wheel -w c:\wheels\ --no-cache-dir wheel
# ==============================================================================

FROM BASE_BUILDER as WHEEL_BUilDER_PY310
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt c:/requirements/
COPY requirements c:/requirements/requirements
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.10
RUN py -m pip install --upgrade pip wheel && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir `
      -r c:/requirements/requirements-ci.txt  `
      -r c:/requirements/requirements-extras.txt  `
      -r c:/requirements/requirements.txt
RUN py -m pip wheel -w c:\wheels\ --no-cache-dir wheel
# ==============================================================================

FROM BASE_BUILDER as WHEEL_BUilDER_PY311
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extras.txt c:/requirements/
COPY requirements c:/requirements/requirements
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV PY_PYTHON=3.11
RUN py -m pip install --upgrade pip wheel && `
    py -m pip wheel -w c:\wheels\ --no-cache-dir `
      -r c:/requirements/requirements-ci.txt  `
      -r c:/requirements/requirements-extras.txt  `
      -r c:/requirements/requirements.txt
RUN py -m pip wheel -w c:\wheels\ --no-cache-dir wheel
# ==============================================================================

FROM BASE_BUILDER
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

COPY --from=WHEEL_BUilDER_PY37 c:/wheels/ c:/wheels/
COPY --from=WHEEL_BUilDER_PY38 c:/wheels/ c:/wheels/
COPY --from=WHEEL_BUilDER_PY39 c:/wheels/ c:/wheels/
COPY --from=WHEEL_BUilDER_PY310 c:/wheels/ c:/wheels/
COPY --from=WHEEL_BUilDER_PY311 c:/wheels/ c:/wheels/

ENV PIP_FIND_LINKS=c:\wheels
COPY requirements requirements
RUN python -m pip install pip --upgrade ; pip install wheel; pip install -r requirements/requirements_tox.txt "devpi-client<6.0"
WORKDIR C:/src
CMD tox --workdir ${Env:TEMP}\tox\ -vv  --recreate -p=auto
