library identifier: 'JenkinsPythonHelperLibrary@2024.2.0', retriever: modernSCM(
  [$class: 'GitSCMSource',
   remote: 'https://github.com/UIUCLibrary/JenkinsPythonHelperLibrary.git',
   ])


SUPPORTED_MAC_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12']
SUPPORTED_LINUX_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12']
SUPPORTED_WINDOWS_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12']

libraries = [:]

def getPypiConfig() {
    node(){
        configFileProvider([configFile(fileId: 'pypi_config', variable: 'CONFIG_FILE')]) {
            def config = readJSON( file: CONFIG_FILE)
            return config['deployment']['indexes']
        }
    }
}

def mac_wheels(){
    def wheelStages = [:]
    SUPPORTED_MAC_VERSIONS.each{ pythonVersion ->
        wheelStages["Python ${pythonVersion} - Mac"] = {
            stage("Python ${pythonVersion} - Mac"){
                stage("Single arch wheels for Python ${pythonVersion}"){
                    def archStages = [:]
                    if(params.INCLUDE_MACOS_X86_64 == true){
                        archStages["MacOS - Python ${pythonVersion} - x86_64: wheel"] = {
                            stage("Build Wheel (${pythonVersion} MacOS x86_64)"){
                                buildPythonPkg(
                                    agent: [
                                        label: "mac && python${pythonVersion} && x86_64",
                                    ],
                                    retries: 3,
                                    buildCmd: {
                                        withEnv([
                                            '_PYTHON_HOST_PLATFORM=macosx-10.9-x86_64',
                                            'MACOSX_DEPLOYMENT_TARGET=10.9',
                                            'UV_INDEX_STRATEGY=unsafe-best-match',
                                            'ARCHFLAGS=-arch x86_64'
                                        ]){
                                             sh(label: 'Building wheel',
                                                script: """python${pythonVersion} -m venv venv
                                                           . ./venv/bin/activate
                                                           python -m pip install --upgrade pip
                                                           pip install wheel==0.37
                                                           pip install build delocate uv
                                                           python -m build --wheel --installer=uv
                                                           """
                                               )
                                            findFiles(glob: 'dist/*.whl').each{
                                                sh(label: 'Fixing up wheel',
                                                       script: """. ./venv/bin/activate
                                                                  pip list
                                                                  delocate-listdeps --depending ${it.path}
                                                                  delocate-wheel -w fixed_wheels --require-archs x86_64 --verbose ${it.path}
                                                               """
                                                 )
                                            }
                                         }
                                    },
                                    post:[
                                        cleanup: {
                                            cleanWs(
                                                patterns: [
                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                        [pattern: 'venv/', type: 'INCLUDE'],
                                                    ],
                                                notFailBuild: true,
                                                deleteDirs: true
                                            )
                                        },
                                        success: {
                                            stash includes: 'dist/*.whl', name: "python${pythonVersion} mac x86_64 wheel"
                                            wheelStashes << "python${pythonVersion} mac x86_64 wheel"
                                            archiveArtifacts artifacts: 'dist/*.whl'
                                        }
                                    ]
                                )
                            }
                            if(params.TEST_PACKAGES == true){
                                stage("Test Wheel (${pythonVersion} MacOS x86_64)"){
                                    testPythonPkg(
                                        agent: [
                                            label: "mac && python${pythonVersion} && x86_64",
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash "python${pythonVersion} mac x86_64 wheel"
                                        },
                                        retries: 3,
                                        testCommand: {
                                            findFiles(glob: 'dist/*.whl').each{
                                                sh(label: 'Running Tox',
                                                   script: """python${pythonVersion} -m venv venv
                                                              . ./venv/bin/activate
                                                              python -m pip install --upgrade pip
                                                              pip install -r requirements/requirements_tox.txt
                                                              UV_INDEX_STRATEGY=unsafe-best-match tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                          """
                                                )
                                            }
                                        },
                                        post:[
                                            failure:{
                                                sh(script:'pip list', returnStatus: true)
                                            },
                                            cleanup: {
                                                cleanWs(
                                                    patterns: [
                                                            [pattern: 'dist/', type: 'INCLUDE'],
                                                            [pattern: 'venv/', type: 'INCLUDE'],
                                                            [pattern: '.tox/', type: 'INCLUDE'],
                                                        ],
                                                    notFailBuild: true,
                                                    deleteDirs: true
                                                )
                                            },
                                            success: {
                                                 archiveArtifacts artifacts: 'dist/*.whl'
                                            }
                                        ]
                                    )
                                    
                                }
                            }
                        }
                    }
                    if(params.INCLUDE_MACOS_ARM == true){
                        archStages["MacOS - Python ${pythonVersion} - M1: wheel"] = {
                            stage("Build Wheel (${pythonVersion} MacOS m1)"){
                                buildPythonPkg(
                                    agent: [
                                        label: "mac && python${pythonVersion} && m1",
                                    ],
                                    retries: 3,
                                    buildCmd: {
            //                     Taken from cibuildwheel source code
            //                     https://github.com/pypa/cibuildwheel/blob/main/cibuildwheel/macos.py
            //
            //                     # macOS 11 is the first OS with arm64 support, so the wheels
            //                     # have that as a minimum.
                                        withEnv([
                                            '_PYTHON_HOST_PLATFORM=macosx-11.0-arm64',
                                            'MACOSX_DEPLOYMENT_TARGET=11.0',
                                            'UV_INDEX_STRATEGY=unsafe-best-match',
                                            'ARCHFLAGS=-arch arm64'
                                            ]) {
                                             sh(label: 'Building wheel',
                                                script: """python${pythonVersion} -m venv venv
                                                           . ./venv/bin/activate
                                                           pip install --upgrade pip
                                                           pip install wheel==0.37
                                                           pip install build delocate uv
                                                           python -m build --wheel --installer=uv
                                                           """
                                               )
                                             findFiles(glob: 'dist/*.whl').each{
                                                sh(label: 'Fixing up wheel',
                                                   script: """./venv/bin/delocate-listdeps --depending ${it.path}
                                                              ./venv/bin/delocate-wheel -w fixed_wheels --require-archs arm64 --verbose ${it.path}
                                                           """
                                             )
                                         }
                                        }
                                    },
                                    post:[
                                        cleanup: {
                                            cleanWs(
                                                patterns: [
                                                        [pattern: 'venv/', type: 'INCLUDE'],
                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                    ],
                                                notFailBuild: true,
                                                deleteDirs: true
                                            )
                                        },
                                        success: {
                                            stash includes: 'dist/*.whl', name: "python${pythonVersion} m1 mac wheel"
                                            wheelStashes << "python${pythonVersion} m1 mac wheel"
                                            archiveArtifacts artifacts: 'dist/*.whl'
                                        }
                                    ]
                                )
                            }
                            stage("Test Wheel (${pythonVersion} MacOS m1)"){
                                testPythonPkg(
                                    agent: [
                                        label: "mac && python${pythonVersion} && m1",
                                    ],
                                    retries: 3,
                                    testSetup: {
                                        checkout scm
                                        unstash "python${pythonVersion} m1 mac wheel"
                                    },
                                    testCommand: {
                                        findFiles(glob: 'dist/*.whl').each{
                                            sh(label: 'Running Tox',
                                               script: """python${pythonVersion} -m venv venv
                                                          . ./venv/bin/activate
                                                          python -m pip install --upgrade pip
                                                          pip install -r requirements/requirements_tox.txt
                                                          UV_INDEX_STRATEGY=unsafe-best-match tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                      """
                                            )
                                        }
                                    },
                                    post:[
                                        failure:{
                                            sh(script:'pip list', returnStatus: true)
                                        },
                                        cleanup: {
                                            cleanWs(
                                                patterns: [
                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                        [pattern: 'venv/', type: 'INCLUDE'],
                                                        [pattern: '.tox/', type: 'INCLUDE'],
                                                    ],
                                                notFailBuild: true,
                                                deleteDirs: true
                                            )
                                        },
                                        success: {
                                             archiveArtifacts artifacts: 'dist/*.whl'
                                        }
                                    ]
                                )
                                
                            }
                        }
                    }
                    parallel(archStages)
                }
            }
            if(params.INCLUDE_MACOS_X86_64 && params.INCLUDE_MACOS_ARM && pythonVersion != '3.8'){
                stage("Universal2 Wheel: Python ${pythonVersion}"){
                    stage('Make Universal2 wheel'){
                        node("mac && python${pythonVersion}") {
                            unstash "python${pythonVersion} m1 mac wheel"
                            unstash "python${pythonVersion} mac x86_64 wheel"
                            def wheelNames = []
                            findFiles(excludes: '', glob: 'dist/*.whl').each{wheelFile ->
                                wheelNames.add(wheelFile.path)
                            }
                            try{
                                sh(label: 'Make Universal2 wheel',
                                   script: """python${pythonVersion} -m venv venv
                                              . ./venv/bin/activate
                                              pip install --upgrade pip
                                              pip install wheel delocate
                                              mkdir -p out
                                              delocate-merge  ${wheelNames.join(' ')} --verbose -w ./out/
                                              rm dist/*.whl
                                               """
                                   )
                               def fusedWheel = findFiles(excludes: '', glob: 'out/*.whl')[0]
                               def props = readTOML( file: 'pyproject.toml')['project']
                               def universalWheel = "uiucprescon.imagevalidate-${props.version}-cp${pythonVersion.replace('.','')}-cp${pythonVersion.replace('.','')}-macosx_11_0_universal2.whl"
                               sh "mv ${fusedWheel.path} ./dist/${universalWheel}"
                               stash includes: 'dist/*.whl', name: "python${pythonVersion} mac-universal2 wheel"
                               wheelStashes << "python${pythonVersion} mac-universal2 wheel"
                               archiveArtifacts artifacts: 'dist/*.whl'
                            } finally {
                                cleanWs(
                                    patterns: [
                                            [pattern: 'out/', type: 'INCLUDE'],
                                            [pattern: 'dist/', type: 'INCLUDE'],
                                            [pattern: 'venv/', type: 'INCLUDE'],
                                        ],
                                    notFailBuild: true,
                                    deleteDirs: true
                                )
                           }
                        }
                    }
                    if(params.TEST_PACKAGES == true){
                        stage("Test universal2 Wheel"){
                            parallel(
                                "Test Python ${pythonVersion} universal2 Wheel on x86_64 mac": {
                                    stage("Test Python ${pythonVersion} universal2 Wheel on x86_64 mac"){
                                        testPythonPkg(
                                            agent: [
                                                label: "mac && python${pythonVersion} && x86_64",
                                            ],
                                            testSetup: {
                                                checkout scm
                                                unstash "python${pythonVersion} mac-universal2 wheel"
                                            },
                                            retries: 3,
                                            testCommand: {
                                                findFiles(glob: 'dist/*.whl').each{
                                                    sh(label: 'Running Tox',
                                                       script: """python${pythonVersion} -m venv venv
                                                                  . ./venv/bin/activate
                                                                  python -m pip install --upgrade pip
                                                                  pip install -r requirements/requirements_tox.txt
                                                                  UV_INDEX_STRATEGY=unsafe-best-match CONAN_REVISIONS_ENABLED=1 tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                               """
                                                    )
                                                }
                                            },
                                            post:[
                                                cleanup: {
                                                    cleanWs(
                                                        patterns: [
                                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                                [pattern: 'venv/', type: 'INCLUDE'],
                                                                [pattern: '.tox/', type: 'INCLUDE'],
                                                            ],
                                                        notFailBuild: true,
                                                        deleteDirs: true
                                                    )
                                                },
                                                success: {
                                                     archiveArtifacts artifacts: 'dist/*.whl'
                                                }
                                            ]
                                        )
                                    }
                                },
                                "Test Python ${pythonVersion} universal2 Wheel on M1 Mac": {
                                    stage("Test Python ${pythonVersion} universal2 Wheel on M1 Mac"){
                                        testPythonPkg(
                                            agent: [
                                                label: "mac && python${pythonVersion} && m1",
                                            ],
                                            testSetup: {
                                                checkout scm
                                                unstash "python${pythonVersion} mac-universal2 wheel"
                                            },
                                            retries: 3,
                                            testCommand: {
                                                findFiles(glob: 'dist/*.whl').each{
                                                    sh(label: 'Running Tox',
                                                       script: """python${pythonVersion} -m venv venv
                                                                  . ./venv/bin/activate
                                                                  python -m pip install --upgrade pip
                                                                  pip install -r requirements/requirements_tox.txt
                                                                  UV_INDEX_STRATEGY=unsafe-best-match CONAN_REVISIONS_ENABLED=1 tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                               """
                                                    )
                                                }
                                            },
                                            post:[
                                                cleanup: {
                                                    cleanWs(
                                                        patterns: [
                                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                                [pattern: 'venv/', type: 'INCLUDE'],
                                                                [pattern: '.tox/', type: 'INCLUDE'],
                                                            ],
                                                        notFailBuild: true,
                                                        deleteDirs: true
                                                    )
                                                },
                                            ]
                                        )
                                    }
                                }
                            )
                        }
                    }
                }
            }
        }
    }
    parallel(wheelStages)
}

def windows_wheels(){
    def wheelStages = [:]
    SUPPORTED_WINDOWS_VERSIONS.each{ pythonVersion ->
        if(params.INCLUDE_WINDOWS_X86_64 == true){
            wheelStages["Python ${pythonVersion} - Windows"] = {
                stage("Python ${pythonVersion} - Windows"){
                    stage("Build Wheel (${pythonVersion} Windows)"){
                        retry(2){
                            buildPythonPkg(
                                agent: [
                                    dockerfile: [
                                        label: 'windows && docker && x86_64',
                                        filename: 'ci/docker/python/windows/msvc/tox/Dockerfile',
                                        additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg chocolateyVersion --build-arg PIP_DOWNLOAD_CACHE=c:/users/ContainerUser/appdata/local/pip --build-arg UV_CACHE_DIR=c:/users/ContainerUser/appdata/local/uv',
                                        args: '-v pipcache_imagevalidate:c:/users/ContainerUser/appdata/local/pip',
                                    ]
                                ],
                                buildCmd: {
                                    bat "py -${pythonVersion} -m build --wheel --installer=uv"
                                },
                                post:[
                                    cleanup: {
                                        cleanWs(
                                            patterns: [
                                                    [pattern: 'dist/', type: 'INCLUDE'],
                                                ],
                                            notFailBuild: true,
                                            deleteDirs: true
                                        )
                                    },
                                    success: {
                                        stash includes: 'dist/*.whl', name: "python${pythonVersion} windows wheel"
                                        wheelStashes << "python${pythonVersion} windows wheel"
                                        archiveArtifacts artifacts: 'dist/*.whl'
                                    }
                                ]
                            )
                        }
                    }
                    stage("Test Wheel (${pythonVersion} Windows)"){
                        retry(2){
                            testPythonPkg(
                                agent: [
                                    dockerfile: [
                                        label: 'windows && docker && x86_64',
                                        filename: 'ci/docker/python/windows/msvc/tox_no_vs/Dockerfile',
                                        additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg chocolateyVersion --build-arg PIP_DOWNLOAD_CACHE=c:/users/ContainerUser/appdata/local/pip --build-arg UV_CACHE_DIR=c:/users/ContainerUser/appdata/local/uv',
                                        args: '-v pipcache_imagevalidate:c:/users/ContainerUser/appdata/local/pip -v uvcache_imagevalidate:c:/users/ContainerUser/appdata/local/uv',
                                        dockerImageName: "${currentBuild.fullProjectName}_test_no_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                    ]
                                ],
                                testSetup: {
                                     checkout scm
                                     unstash "python${pythonVersion} windows wheel"
                                },
                                testCommand: {
                                     findFiles(glob: 'dist/*.whl').each{
                                         bat(label: 'Running Tox', script: "tox --installpkg ${it.path} --workdir %TEMP%\\tox  -e py${pythonVersion.replace('.', '')}")
                                     }

                                },
                                post:[
                                    failure:{
                                        bat(script:'pip list')
                                    },
                                    cleanup: {
                                        cleanWs(
                                            patterns: [
                                                    [pattern: 'dist/', type: 'INCLUDE'],
                                                    [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                ],
                                            notFailBuild: true,
                                            deleteDirs: true
                                        )
                                    },
                                    success: {
                                        archiveArtifacts artifacts: 'dist/*.whl'
                                    }
                                ]
                            )
                        }
                    }
                }
            }
        }
    }
    parallel(wheelStages)
}

def linux_wheels(){
    def wheelStages = [:]
     SUPPORTED_LINUX_VERSIONS.each{ pythonVersion ->
        wheelStages["Python ${pythonVersion} - Linux"] = {
            stage("Python ${pythonVersion} - Linux"){
                def archBuilds = [:]
                if(params.INCLUDE_LINUX_X86_64 == true){
                    archBuilds["Python ${pythonVersion} Linux x86_64 Wheel"] = {
                        stage("Python ${pythonVersion} Linux x86_64 Wheel"){
                            stage("Build Wheel (${pythonVersion} Linux x86_64)"){
                                buildPythonPkg(
                                    agent: [
                                        dockerfile: [
                                            label: 'linux && docker && x86_64',
                                            filename: 'ci/docker/python/linux/package/Dockerfile',
                                            additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg manylinux_image=quay.io/pypa/manylinux2014_x86_64 --build-arg UV_CACHE_DIR=/.cache/uv',
                                            args: '-v pipcache_imagevalidate:/.cache/pip -v uvcache_wheel_builder_imagevalidate:/.cache/uv',
                                        ]
                                    ],
                                    retries: 3,
                                    buildCmd: {                                         
                                        sh(label: 'Building python wheel',
                                           script: "sh ./contrib/build_linux_wheels.sh . --base-python=python${pythonVersion}"
                                           )
                                    },
                                    post:[
                                        cleanup: {
                                            cleanWs(
                                                patterns: [
                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                    ],
                                                notFailBuild: true,
                                                deleteDirs: true
                                            )
                                        },
                                        success: {
                                            stash includes: 'dist/*manylinux*.*whl', name: "python${pythonVersion} linux-x86-64 wheel"
                                            wheelStashes << "python${pythonVersion} linux-x86-64 wheel"
                                            archiveArtifacts artifacts: 'dist/*.whl'
                                        }
                                    ]
                                )
                            }
                            if(params.TEST_PACKAGES == true){
                                stage("Test Wheel (${pythonVersion} Linux x86_64)"){
                                    retry(2){
                                        testPythonPkg(
                                            agent: [
                                                dockerfile: [
                                                    label: 'linux && docker && x86_64',
                                                    filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_DOWNLOAD_CACHE=/.cache/pip --build-arg UV_CACHE_DIR=/.cache/uv',
                                                    args: '-v pipcache_imagevalidate:/.cache/pip -v uvcache_imagevalidate:/.cache/uv',
                                                ]
                                            ],
                                            testSetup: {
                                                checkout scm
                                                unstash "python${pythonVersion} linux-x86-64 wheel"
                                            },
                                            testCommand: {
                                                findFiles(glob: 'dist/*.whl').each{
                                                    timeout(5){
                                                        sh(
                                                            label: 'Running Tox',
                                                            script: "tox --installpkg ${it.path} --workdir /tmp/tox -e py${pythonVersion.replace('.', '')}"
                                                            )
                                                    }
                                                }
                                            },
                                            post:[
                                                failure:{
                                                    sh(script:'pip list')
                                                },
                                                cleanup: {
                                                    cleanWs(
                                                        patterns: [
                                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                                [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                            ],
                                                        notFailBuild: true,
                                                        deleteDirs: true
                                                    )
                                                },
                                                success: {
                                                    archiveArtifacts artifacts: 'dist/*.whl'
                                                },
                                            ]
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
                if(params.INCLUDE_LINUX_ARM == true){
                    archBuilds["Python ${pythonVersion} Linux ARM64 wheel"] = {
                        stage("Python ${pythonVersion} Linux ARM64 Wheel"){
                            stage("Build Wheel (${pythonVersion} Linux ARM64)"){
                                buildPythonPkg(
                                    agent: [
                                        dockerfile: [
                                            label: 'linux && docker && arm',
                                            filename: 'ci/docker/python/linux/package/Dockerfile',
                                            additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg manylinux_image=quay.io/pypa/manylinux2014_aarch64'
                                        ]
                                    ],
                                    buildCmd: {
                                        sh(label: 'Building python wheel',
                                           script: "sh ./contrib/build_linux_wheels.sh . --base-python=python${pythonVersion}"
                                           )
                                    },
                                    post:[
                                        cleanup: {
                                            cleanWs(
                                                patterns: [
                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                    ],
                                                notFailBuild: true,
                                                deleteDirs: true
                                            )
                                        },
                                        success: {
                                            stash includes: 'dist/*manylinux*.*whl', name: "python${pythonVersion} linux-arm64 wheel"
                                            wheelStashes << "python${pythonVersion} linux-arm64 wheel"
                                            archiveArtifacts artifacts: 'dist/*.whl'
                                        }
                                    ]
                                )
                            }
                            if(params.TEST_PACKAGES == true){
                                stage("Test Wheel (${pythonVersion} Linux ARM64)"){
                                    retry(2){
                                        testPythonPkg(
                                            agent: [
                                                dockerfile: [
                                                    label: 'linux && docker && arm',
                                                    filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_DOWNLOAD_CACHE=/.cache/pip --build-arg UV_CACHE_DIR=/.cache/uv',
                                                    args: '-v pipcache_imagevalidate:/.cache/pip -v uvcache_imagevalidate:/.cache/uv',
                                                ]
                                            ],
                                            testSetup: {
                                                checkout scm
                                                unstash "python${pythonVersion} linux-arm64 wheel"
                                            },
                                            testCommand: {
                                                findFiles(glob: 'dist/*.whl').each{
                                                    timeout(5){
                                                        sh(
                                                            label: 'Running Tox',
                                                            script: "tox --installpkg ${it.path} --workdir /tmp/tox -e py${pythonVersion.replace('.', '')}"
                                                            )
                                                    }
                                                }
                                            },
                                            post:[
                                                failure:{
                                                    sh(script:'pip list')
                                                },
                                                cleanup: {
                                                    cleanWs(
                                                        patterns: [
                                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                                [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                            ],
                                                        notFailBuild: true,
                                                        deleteDirs: true
                                                    )
                                                },
                                                success: {
                                                    archiveArtifacts artifacts: 'dist/*.whl'
                                                },
                                            ]
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
                parallel(archBuilds)
            }
        }
    }
    parallel(wheelStages)
}

wheelStashes = []

def get_sonarqube_unresolved_issues(report_task_file){
    script{

        def props = readProperties  file: '.scannerwork/report-task.txt'
        def branch = props['branch']
        def url = props['serverUrl'] + '/api/issues/search?componentKeys=' + props['projectKey'] + "&branch=" + branch +"&resolved=no"
        def response = httpRequest(url : url)
        def outstandingIssues = readJSON text: response.content
        return outstandingIssues
    }
}

def sonarcloudSubmit(outputJson, sonarCredentials){
    withSonarQubeEnv(installationName:'sonarcloud', credentialsId: sonarCredentials) {
        def props = readTOML( file: 'pyproject.toml')['project']
        if (env.CHANGE_ID){
            sh(
                label: 'Running Sonar Scanner',
                script:"sonar-scanner -Dsonar.projectVersion=${props.version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET} -Dsonar.cfamily.cache.enabled=false -Dsonar.cfamily.threads=\$(grep -c ^processor /proc/cpuinfo) -Dsonar.cfamily.build-wrapper-output=build/build_wrapper_output_directory"
                )
        } else {
            sh(
                label: 'Running Sonar Scanner',
                script: "sonar-scanner -Dsonar.projectVersion=${props.version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME} -Dsonar.cfamily.cache.enabled=false -Dsonar.cfamily.threads=\$(grep -c ^processor /proc/cpuinfo) -Dsonar.cfamily.build-wrapper-output=build/build_wrapper_output_directory"
                )
        }
    }
     timeout(time: 1, unit: 'HOURS') {
         def sonarqube_result = waitForQualityGate(abortPipeline: false)
         if (sonarqube_result.status != 'OK') {
             unstable "SonarQube quality gate: ${sonarqube_result.status}"
         }
         def outstandingIssues = get_sonarqube_unresolved_issues('.scannerwork/report-task.txt')
         writeJSON file: outputJson, json: outstandingIssues
     }
}


def startup(){
    parallel(
        'Loading Reference Build Information': {
            stage('Loading Reference Build Information'){
                node(){
                    checkout scm
                    discoverGitReferenceBuild()
                }
            }
        },
    )
}

stage('Pipeline Pre-tasks'){
    startup()
}
pipeline {
    agent none
    options {
        timeout(time: 1, unit: 'DAYS')
    }
    parameters {
        booleanParam(name: 'RUN_CHECKS', defaultValue: true, description: 'Run checks on code')
        booleanParam(name: 'RUN_MEMCHECK', defaultValue: false, description: 'Run Memcheck. NOTE: This can be very slow.')
        booleanParam(name: 'TEST_RUN_TOX', defaultValue: false, description: 'Run Tox Tests')
        booleanParam(name: 'USE_SONARQUBE', defaultValue: true, description: 'Send data test data to SonarQube')
        credentials(name: 'SONARCLOUD_TOKEN', credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl', defaultValue: 'sonarcloud_token', required: false)
        booleanParam(name: 'BUILD_PACKAGES', defaultValue: false, description: 'Build Python packages')
        booleanParam(name: 'TEST_PACKAGES', defaultValue: true, description: 'Test Python packages by installing them and running tests on the installed package')
        booleanParam(name: 'INCLUDE_LINUX_ARM', defaultValue: false, description: 'Include ARM architecture for Linux')
        booleanParam(name: 'INCLUDE_LINUX_X86_64', defaultValue: true, description: 'Include x86_64 architecture for Linux')
        booleanParam(name: 'INCLUDE_MACOS_ARM', defaultValue: false, description: 'Include ARM(m1) architecture for Mac')
        booleanParam(name: 'INCLUDE_MACOS_X86_64', defaultValue: false, description: 'Include x86_64 architecture for Mac')
        booleanParam(name: 'INCLUDE_WINDOWS_X86_64', defaultValue: false, description: 'Include x86_64 architecture for Windows')
        booleanParam(name: 'DEPLOY_PYPI', defaultValue: false, description: 'Deploy to pypi')
        booleanParam(name: 'DEPLOY_DOCS', defaultValue: false, description: 'Update online documentation. Release Branch Only')
    }
    stages {
        stage('Building and Testing'){
            when{
                anyOf{
                    equals expected: true, actual: params.RUN_CHECKS
                    equals expected: true, actual: params.TEST_RUN_TOX
                    equals expected: true, actual: params.DEPLOY_DOCS
                }
            }
            stages{
                stage('Building'){
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker && x86_64'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                        }
                    }
                    when{
                        anyOf{
                            equals expected: true, actual: params.RUN_CHECKS
                            equals expected: true, actual: params.DEPLOY_DOCS
                        }
                        beforeAgent true
                    }
                    options {
                        retry(2)
                    }
                    stages{
                        stage('Sphinx Documentation'){
                            steps {
                                sh(
                                    label: 'Building',
                                    script: 'python3 setup.py build -b build --build-lib build/lib -t build/temp build_ext --inplace'
                                )
                                sh(
                                    label: 'Building docs',
                                    script: 'python3 -m sphinx -b html docs/source build/docs/html -d build/docs/doctrees -v -w logs/build_sphinx.log -W --keep-going'
                                )
                            }
                            post{
                                always {
                                    recordIssues(tools: [sphinxBuild(name: 'Sphinx Documentation Build', pattern: 'logs/build_sphinx.log')])
                                    archiveArtifacts artifacts: 'logs/build_sphinx.log'
                                    script{
                                        def props = readTOML( file: 'pyproject.toml')['project']
                                        zip archive: true, dir: 'build/docs/html', glob: '', zipFile: "dist/${props.name}-${props.version}.doc.zip"
                                    }
                                    stash includes: 'dist/*.doc.zip,build/docs/html/**', name: 'DOCS_ARCHIVE'
                                }
                                success{
                                    publishHTML(
                                        [
                                            allowMissing: false,
                                            alwaysLinkToLastBuild: false,
                                            keepAll: false, reportDir: 'build/docs/html',
                                            reportFiles: 'index.html',
                                            reportName: 'Documentation',
                                            reportTitles: ''
                                        ]
                                    )
                                }
                           }
                       }
                   }
                   post{
                       cleanup{
                           cleanWs(
                               deleteDirs: true,
                               patterns: [
                                   [pattern: 'logs/', type: 'INCLUDE'],
                                   [pattern: 'build/', type: 'INCLUDE'],
                                   [pattern: 'dist/', type: 'INCLUDE'],
                                   [pattern: '.eggs/', type: 'INCLUDE']
                               ]
                           )
                       }
                   }
                }
                stage('Checks'){
                    when{
                        equals expected: true, actual: params.RUN_CHECKS
                    }
                    stages{
                        stage('Testing'){
                            stages{
                                stage('Testing Python') {
                                    agent {
                                        dockerfile {
                                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                                            label 'linux && docker && x86_64'
                                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                                            args '--mount source=sonar-cache-uiucprescon-imagevalidate,target=/opt/sonar/.sonar/cache'
                                        }
                                    }
                                    options {
                                      retry(conditions: [agent()], count: 3)
                                    }
                                    stages{
                                        stage('Set up Tests'){
                                            parallel{
                                                stage('Build extension for Python'){
                                                    steps{
                                                        sh(
                                                            label: 'Building',
                                                            script: 'CFLAGS="--coverage" python3 setup.py build -b build/python --build-lib build/python/lib -t build/python/temp build_ext --inplace'
                                                        )
                                                    }
                                                }
                                                stage('Build C++ Tests'){
                                                    steps{
                                                        tee('logs/cmake-build.log'){
                                                            sh(label: 'Compiling CPP Code',
                                                               script: '''conan install . -if build/cpp -o "*:shared=True" --build=missing
                                                                          cmake -B build/cpp \
                                                                            -Wdev \
                                                                            -DCMAKE_BUILD_TYPE=Debug \
                                                                            -DCMAKE_TOOLCHAIN_FILE=build/cpp/conan_paths.cmake \
                                                                            -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=ON \
                                                                            -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true \
                                                                            -DBUILD_TESTING:BOOL=true \
                                                                            -DCMAKE_CXX_FLAGS="-fno-inline -fno-omit-frame-pointer -fprofile-arcs -ftest-coverage -Wall -Wextra" \
                                                                            -DMEMORYCHECK_COMMAND=$(which drmemory) \
                                                                            -DMEMORYCHECK_COMMAND_OPTIONS="-check_uninit_blacklist libopenjp2.so.7"
                                                                          build-wrapper-linux-x86-64 --out-dir build/build_wrapper_output_directory cmake --build build/cpp -j $(grep -c ^processor /proc/cpuinfo) --config Debug
                                                                          '''
                                                            )
                                                        }
                                                    }
                                                    post{
                                                        always{
                                                            archiveArtifacts artifacts: 'logs/*'
                                                            recordIssues(
                                                                 tools: [
                                                                     gcc(pattern: 'logs/cmake-build.log'),
                                                                     [$class: 'Cmake', pattern: 'logs/cmake-build.log']
                                                                 ]
                                                            )
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        stage('Run Tests'){
                                            stages{
                                                stage('Run Testing'){
                                                    parallel {
                                                        stage('C++ Unit Tests'){
                                                            steps{
                                                                sh(label: 'Running CTest',
                                                                   script: 'cd build/cpp && ctest --output-on-failure --no-compress-output -T Test'
                                                                )
                                                            }
                                                            post{
                                                                always{
                                                                    xunit(
                                                                       testTimeMargin: '3000',
                                                                       thresholdMode: 1,
                                                                       thresholds: [
                                                                           failed(),
                                                                           skipped()
                                                                       ],
                                                                       tools: [
                                                                           CTest(
                                                                               deleteOutputFiles: true,
                                                                               failIfNotNew: true,
                                                                               pattern: 'build/cpp/Testing/**/*.xml',
                                                                               skipNoTestFiles: true,
                                                                               stopProcessingIfError: true
                                                                           )
                                                                       ]
                                                                   )
                                                                   sh 'mkdir -p reports && gcovr --filter uiucprescon/imagevalidate --print-summary  --xml -o reports/coverage_cpp.xml'
                                                                   stash(includes: 'reports/coverage_cpp.xml', name: 'CPP_COVERAGE_REPORT')
                                                                }
                                                            }
                                                        }
                                                        stage('Clang Tidy Analysis') {
                                                            steps{
                                                                tee('logs/clang-tidy.log') {
                                                                    sh(label: 'Run Clang Tidy', script: 'run-clang-tidy -clang-tidy-binary $(which clang-tidy) -p $WORKSPACE/build/cpp/ ./uiucprescon/imagevalidate' )
                                                                }
                                                            }
                                                            post{
                                                                always {
                                                                    recordIssues(tools: [clangTidy(pattern: 'logs/clang-tidy.log')])
                                                                }
                                                            }
                                                        }
                                                        stage('CPP Check'){
                                                            steps{
                                                                writeFile(
                                                                    file: 'cppcheck_exclusions.txt',
                                                                    text: "*:${WORKSPACE}/build/cpp/_deps/*"
                                                                )
                                                                catchError(buildResult: 'SUCCESS', message: 'cppcheck found issues', stageResult: 'UNSTABLE') {
                                                                    sh(label: 'Running cppcheck',
                                                                       script: 'cppcheck --error-exitcode=1 --project=build/cpp/compile_commands.json --enable=all -i build/cpp/_deps  --inline-suppr --xml --xml-version=2 --output-file=logs/cppcheck_debug.xml --suppress=missingIncludeSystem --suppressions-list=cppcheck_exclusions.txt --check-config'
                                                                       )
                                                                }
                                                            }
                                                            post{
                                                                always {
                                                                    recordIssues(
                                                                        filters: [
                                                                             excludeType('unmatchedSuppression')
                                                                        ],
                                                                        tools: [
                                                                            cppCheck(pattern: 'logs/cppcheck_debug.xml')
                                                                        ]
                                                                    )
                                                                }
                                                            }
                                                        }
                                                        stage('MemCheck'){
                                                            when{
                                                                equals expected: true, actual: params.RUN_MEMCHECK
                                                            }
                                                            steps{
                                                                timeout(15){
                                                                    sh(
                                                                      label: 'Running memcheck',
                                                                      script: '(cd build/cpp && ctest -T memcheck -j $(grep -c ^processor /proc/cpuinfo) )'
                                                                    )
                                                                }
                                                            }
                                                            post{
                                                                always{
                                                                    recordIssues(
                                                                        tools: [
                                                                            drMemory(pattern: 'build/cpp/Testing/Temporary/DrMemory/**/results.txt')
                                                                            ]
                                                                    )
                                                                    archiveArtifacts allowEmptyArchive: true, artifacts: 'build/cpp/Testing/Temporary/DrMemory/**/results.txt'
                                                                }
                                                            }
                                                        }
                                                        stage('Run PyTest Unit Tests'){
                                                            steps{
                                                                catchError(buildResult: 'UNSTABLE', message: 'Did not pass all pytest tests', stageResult: 'UNSTABLE') {
                                                                    sh(
                                                                        label: 'Running Pytest',
                                                                        script:'''mkdir -p reports/coverage
                                                                                  coverage run --parallel-mode --source=uiucprescon -m pytest --junitxml=reports/pytest.xml --integration
                                                                                  '''
                                                                   )
                                                               }
                                                            }
                                                            post {
                                                                always {
                                                                    junit 'reports/pytest.xml'
                                                                }
                                                            }
                                                        }
                                                        stage('Run Doctest Tests'){
                                                           steps {
                                                               catchError(buildResult: 'SUCCESS', message: 'Doctest found issues', stageResult: 'UNSTABLE') {
                                                                   sh( label: 'Running Doctest',
                                                                       script: '''coverage run --parallel-mode --source=uiucprescon -m sphinx -b doctest docs/source build/docs -d build/docs/doctrees -v
                                                                                  mkdir -p reports
                                                                                  mv build/docs/output.txt reports/doctest.txt
                                                                                  '''
                                                                       )
                                                               }
                                                           }
                                                        }
                                                        stage('Task Scanner'){
                                                            steps{
                                                                recordIssues(tools: [taskScanner(highTags: 'FIXME', includePattern: 'uiucprescon/**/*.py', normalTags: 'TODO')])
                                                            }
                                                        }
                                                        stage('Run MyPy Static Analysis') {
                                                            steps{
                                                                catchError(buildResult: 'SUCCESS', message: 'MyPy found issues', stageResult: 'UNSTABLE') {
                                                                    sh(
                                                                        label: 'Running Mypy',
                                                                        script: '''mkdir -p logs
                                                                                   mypy -p uiucprescon --html-report reports/mypy/html > logs/mypy.log
                                                                                   '''
                                                                   )
                                                                }
                                                            }
                                                            post {
                                                                always {
                                                                    recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                                                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                                                }
                                                            }
                                                        }
                                                        stage('Run Flake8 Static Analysis') {
                                                            steps{
                                                                catchError(buildResult: 'SUCCESS', message: 'Flake8 found issues', stageResult: 'UNSTABLE') {
                                                                    sh '''mkdir -p logs
                                                                          flake8 uiucprescon --format=pylint --tee --output-file=logs/flake8.log
                                                                          '''
                                                                }
                                                            }
                                                            post {
                                                                always {
                                                                    recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                                                                }
                                                            }
                                                        }
                                                    }
                                                    post{
                                                        always{
                                                            sh(label: 'combining coverage data',
                                                               script: '''coverage combine
                                                                          coverage xml -o ./reports/coverage-python.xml
                                                                          gcovr --filter uiucprescon/imagevalidate --print-summary --xml -o reports/coverage-c-extension.xml
                                                                          '''
                                                            )
                                                            recordCoverage(tools: [[parser: 'COBERTURA', pattern: 'reports/coverage*.xml']])
                                                        }
                                                    }
                                                }
                                                stage('Sonarcloud Analysis'){
                                                    options{
                                                        lock('uiucprescon.imagevalidate-sonarscanner')
                                                    }
                                                    when{
                                                        allOf{
                                                            equals expected: true, actual: params.USE_SONARQUBE
                                                            expression{
                                                                try{
                                                                    withCredentials([string(credentialsId: params.SONARCLOUD_TOKEN, variable: 'dddd')]) {
                                                                        echo 'Found credentials for sonarqube'
                                                                    }
                                                                } catch(e){
                                                                    return false
                                                                }
                                                                return true
                                                            }
                                                        }
                                                    }
                                                    steps{
                                                        sh(
                                                            label: 'Preparing c++ coverage data available for SonarQube',
                                                            script: """mkdir -p build/coverage
                                                                    find ./build -name '*.gcno' -exec gcov {} -p --source-prefix=${WORKSPACE}/ \\;
                                                                    mv *.gcov build/coverage/
                                                                    """
                                                        )
                                                        sonarcloudSubmit('reports/sonar-report.json', params.SONARCLOUD_TOKEN)
                                                    }
                                                    post {
                                                        always{
                                                            script{
                                                                if(fileExists('reports/sonar-report.json')){
                                                                    stash includes: 'reports/sonar-report.json', name: 'SONAR_REPORT'
                                                                    archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/sonar-report.json'
                                                                    recordIssues(tools: [sonarQube(pattern: 'reports/sonar-report.json')])
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                            post{
                                                cleanup{
                                                    cleanWs(
                                                        patterns: [
                                                            [pattern: 'logs/', type: 'INCLUDE'],
                                                            [pattern: 'reports', type: 'INCLUDE'],
                                                        ]
                                                    )
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                stage('Run Tox'){
                    when{
                        equals expected: true, actual: params.TEST_RUN_TOX
                    }
                    parallel{
                        stage('Linux'){
                            when{
                                expression {return nodesByLabel('linux && docker && x86').size() > 0}
                            }
                            steps{
                                script{
                                    parallel(
                                        getToxTestsParallel(
                                            envNamePrefix: 'Tox Linux',
                                            label: 'linux && docker && x86_64',
                                            dockerfile: 'ci/docker/python/linux/tox/Dockerfile',
                                            dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_DOWNLOAD_CACHE=/.cache/pip --build-arg UV_CACHE_DIR=/.cache/uv',
                                            dockerRunArgs: '-v pipcache_imagevalidate:/.cache/pip -v uvcache_imagevalidate:/.cache/uv',
                                            retry: 2
                                        )
                                    )
                                }
                            }
                        }
                        stage('Windows'){
                            when{
                                expression {return nodesByLabel('windows && docker && x86').size() > 0}
                            }
                            steps{
                                script{
                                    parallel(
                                        getToxTestsParallel(
                                            envNamePrefix: 'Tox Windows',
                                            label: 'windows && docker && x86_64',
                                            dockerfile: 'ci/docker/python/windows/msvc/tox/Dockerfile',
                                            dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg chocolateyVersion --build-arg PIP_DOWNLOAD_CACHE=c:/users/ContainerUser/appdata/local/pip --build-arg UV_CACHE_DIR=c:/users/ContainerUser/appdata/local/uv',
                                            dockerRunArgs: '-v pipcache_imagevalidate:c:/users/ContainerUser/appdata/local/pip -v uvcache_imagevalidate:c:/users/ContainerUser/appdata/local/uv',
                                            toxWorkingDir: '%TEMP%/tox',
                                            verbosity: 3,
                                            retry: 2
                                        )
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
        stage('Python Packaging'){
            when{
                equals expected: true, actual: params.BUILD_PACKAGES
                beforeAgent true
            }
            failFast true
            parallel{
                stage('Platform Wheels: Mac'){
                    when {
                        anyOf {
                            equals expected: true, actual: params.INCLUDE_MACOS_X86_64
                            equals expected: true, actual: params.INCLUDE_MACOS_ARM
                        }
                    }
                    steps{
                        mac_wheels()
                    }
                }
                stage('Platform Wheels: Windows'){
                    when {
                        equals expected: true, actual: params.INCLUDE_WINDOWS_X86_64
                    }
                    steps{
                        windows_wheels()
                    }
                }
                stage('Platform Wheels: Linux'){
                    when {
                        anyOf {
                            equals expected: true, actual: params.INCLUDE_LINUX_X86_64
                            equals expected: true, actual: params.INCLUDE_LINUX_ARM
                        }
                    }
                    steps{
                        linux_wheels()
                    }
                }
                stage('Source Distribution'){
                    stages{
                        stage('Build sdist'){
                            agent {
                                docker {
                                    image 'python:3.11'
                                    label 'docker && linux'
                                }
                            }
                            environment{
                                PIP_NO_CACHE_DIR="off"
                            }
                            options {
                                retry(3)
                            }
                            steps{
                                sh(
                                    label: 'Building sdist',
                                    script: '''python -m venv venv --upgrade-deps
                                               venv/bin/python -m pip install build
                                               venv/bin/python -m build --sdist --outdir ./dist
                                    '''
                                    )
                            }
                            post{
                                success {
                                    stash includes: 'dist/*.tar.gz,dist/*.zip', name: 'python sdist'
                                    archiveArtifacts artifacts: 'dist/*.tar.gz,dist/*.zip'
                                    script{
                                        wheelStashes << 'python sdist'
                                    }
                                }
                                cleanup {
                                    cleanWs(
                                        patterns: [
                                            [pattern: 'dist/', type: 'INCLUDE'],
                                        ],
                                        notFailBuild: true,
                                        deleteDirs: true
                                    )
                                }
                                failure {
                                    sh 'python3 -m pip list'
                                }
                            }
                        }
                        stage('Test sdist'){
                            when{
                                equals expected: true, actual: params.TEST_PACKAGES
                            }
                            steps{
                                script{
                                    def testSdistStages = [
                                        failFast: true
                                    ]
                                    SUPPORTED_MAC_VERSIONS.each{ pythonVersion ->
                                        def arches = []
                                        if(params.INCLUDE_MACOS_X86_64 == true){
                                            arches << "x86_64"
                                        }
                                        if(params.INCLUDE_MACOS_ARM == true){
                                            arches << "m1"
                                        }
                                        arches.each{arch ->
                                            testSdistStages["Test sdist (MacOS ${arch} - Python ${pythonVersion})"] = {
                                                stage("Test sdist (MacOS ${arch} - Python ${pythonVersion})"){
                                                    testPythonPkg(
                                                        agent: [
                                                            label: "mac && python${pythonVersion} && ${arch}",
                                                        ],
                                                        retries: 3,
                                                        testSetup: {
                                                            checkout scm
                                                            unstash 'python sdist'
                                                        },
                                                        testCommand: {
                                                            findFiles(glob: 'dist/*.tar.gz').each{
                                                                sh(label: 'Running Tox',
                                                                   script: """python${pythonVersion} -m venv venv
                                                                              . ./venv/bin/activate
                                                                              python -m pip install --upgrade pip
                                                                              pip install -r requirements/requirements_tox.txt
                                                                              UV_INDEX_STRATEGY=unsafe-best-match CONAN_REVISIONS_ENABLED=1  tox run --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                                           """
                                                                )
                                                            }
                                                        },
                                                        post:[
                                                            cleanup: {
                                                                cleanWs(
                                                                    patterns: [
                                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                                        [pattern: 'venv/', type: 'INCLUDE'],
                                                                        [pattern: '.tox/', type: 'INCLUDE'],
                                                                    ],
                                                                    notFailBuild: true,
                                                                    deleteDirs: true
                                                                )
                                                            },
                                                        ]
                                                    )
                                                }
                                            }
                                        }
                                    }
                                    SUPPORTED_WINDOWS_VERSIONS.each{ pythonVersion ->
                                        if(params.INCLUDE_WINDOWS_X86_64 == true){
                                            testSdistStages["Test sdist (Windows x86_64 - Python ${pythonVersion})"] = {
                                                stage("Test sdist (Windows x86_64 - Python ${pythonVersion})"){
                                                    retry(2){
                                                        testPythonPkg(
                                                            agent: [
                                                                dockerfile: [
                                                                    label: 'windows && docker && x86',
                                                                    filename: 'ci/docker/python/windows/msvc/tox/Dockerfile',
                                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg chocolateyVersion --build-arg PIP_DOWNLOAD_CACHE=c:/users/ContainerUser/appdata/local/pip --build-arg UV_CACHE_DIR=c:/users/ContainerUser/appdata/local/uv',
//                                                                    args: '-v pipcache_imagevalidate:c:/users/ContainerUser/appdata/local/pip -v uvcache_imagevalidate:c:/users/ContainerUser/appdata/local/uv',
                                                                    dockerImageName: "${currentBuild.fullProjectName}_test_with_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                                                ]
                                                            ],
                                                            testSetup: {
                                                                checkout scm
                                                                unstash 'python sdist'
                                                            },
                                                            testCommand: {
                                                                findFiles(glob: 'dist/*.tar.gz').each{
                                                                    bat(label: 'Running Tox', script: "tox run --workdir %TEMP%\\.tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}")
                                                                }
                                                            },
                                                            post:[
                                                                failure:{
                                                                    bat(script:'pip list')
                                                                },
                                                                cleanup: {
                                                                    cleanWs(
                                                                        patterns: [
                                                                                [pattern: '.tox/', type: 'INCLUDE'],
                                                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                                                [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                                            ],
                                                                        notFailBuild: true,
                                                                        deleteDirs: true
                                                                    )
                                                                },
                                                            ]
                                                        )
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    SUPPORTED_LINUX_VERSIONS.each{pythonVersion ->
                                        def arches = []
                                        if(params.INCLUDE_LINUX_X86_64 == true){
                                            arches << "x86_64"
                                        }
                                        if(params.INCLUDE_LINUX_ARM == true){
                                            arches << "arm64"
                                        }
                                        arches.each{arch ->
                                            testSdistStages["Test sdist (Linux ${arch} - Python ${pythonVersion})"] = {
                                                stage("Test sdist (Linux ${arch} - Python ${pythonVersion})"){
                                                    testPythonPkg(
                                                        agent: [
                                                            dockerfile: [
                                                                label: "linux && docker && ${arch}",
                                                                filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_DOWNLOAD_CACHE=/.cache/pip --build-arg UV_CACHE_DIR=/.cache/uv'
                                                            ]
                                                        ],
                                                        retries: 3,
                                                        testSetup: {
                                                            checkout scm
                                                            unstash 'python sdist'
                                                        },
                                                        testCommand: {
                                                            findFiles(glob: 'dist/*.tar.gz').each{
                                                                sh(
                                                                    label: 'Running Tox',
                                                                    script: "tox run --installpkg ${it.path} --workdir ./.tox -e py${pythonVersion.replace('.', '')}"
                                                                    )
                                                            }
                                                        },
                                                        post:[
                                                            cleanup: {
                                                                cleanWs(
                                                                    patterns: [
                                                                            [pattern: '.tox', type: 'INCLUDE'],
                                                                            [pattern: 'dist/', type: 'INCLUDE'],
                                                                            [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                                        ],
                                                                    notFailBuild: true,
                                                                    deleteDirs: true
                                                                )
                                                            },
                                                        ]
                                                    )
                                                }
                                            }
                                        }
                                    }
                                    parallel(testSdistStages)
                                }
                            }
                        }
                    }
                }
            }
        }
        stage('Release') {
            parallel {
                stage('Deploy to pypi') {
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker && x86_64'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                        }
                    }
                    when{
                        allOf{
                            equals expected: true, actual: params.DEPLOY_PYPI
                            equals expected: true, actual: params.BUILD_PACKAGES
                        }
                        beforeAgent true
                        beforeInput true
                    }
                    options{
                        retry(3)
                    }
                    input {
                        message 'Upload to pypi server?'
                        parameters {
                            choice(
                                choices: getPypiConfig(),
                                description: 'Url to the pypi index to upload python packages.',
                                name: 'SERVER_URL'
                            )
                        }
                    }
                    steps{
                        script{
                            wheelStashes.each{
                                unstash it
                            }
                        }
                        pypiUpload(
                            credentialsId: 'jenkins-nexus',
                            repositoryUrl: SERVER_URL,
                            glob: 'dist/*'
                        )
                    }
                    post{
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE']
                                    ]
                            )
                        }
                    }
                }
                stage('Deploy Online Documentation') {
                    when{
                        equals expected: true, actual: params.DEPLOY_DOCS
                        beforeAgent true
                        beforeInput true
                    }

                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                        }
                    }
                    options{
                        timeout(time: 1, unit: 'DAYS')
                    }
                    input {
                        message 'Update project documentation?'
                    }
                    steps{
                        unstash 'DOCS_ARCHIVE'
                        withCredentials([usernamePassword(credentialsId: 'dccdocs-server', passwordVariable: 'docsPassword', usernameVariable: 'docsUsername')]) {
                            sh 'python utils/upload_docs.py --username=$docsUsername --password=$docsPassword --subroute=imagevalidate build/docs/html apache-ns.library.illinois.edu'
                        }
                    }
                    post{
                        cleanup{
                            cleanWs(
                                    deleteDirs: true,
                                    patterns: [
                                        [pattern: 'build/', type: 'INCLUDE'],
                                        [pattern: 'dist/', type: 'INCLUDE'],
                                        ]
                                )
                        }
                    }
                }
            }
        }
    }
}
