def getDevPiStagingIndex(){

    if (env.TAG_NAME?.trim()){
        return 'tag_staging'
    } else{
        return "${env.BRANCH_NAME}_staging"
    }
}

def getDevpiConfig() {
    node(){
        configFileProvider([configFile(fileId: 'devpi_config', variable: 'CONFIG_FILE')]) {
            def configProperties = readProperties(file: CONFIG_FILE)
            configProperties.stagingIndex = getDevPiStagingIndex()
            return configProperties
        }
    }
}

DEVPI_CONFIG = getDevpiConfig()
echo "I got ${DEVPI_CONFIG}"
DEVPI_CONFIG_STAGING_INDEX =  getDevPiStagingIndex()
SUPPORTED_MAC_VERSIONS = ['3.8', '3.9', '3.10']
SUPPORTED_LINUX_VERSIONS = ['3.7', '3.8', '3.9', '3.10']
SUPPORTED_WINDOWS_VERSIONS = ['3.7', '3.8', '3.9', '3.10']

def PYPI_SERVERS = [
    'https://jenkins.library.illinois.edu/nexus/repository/uiuc_prescon_python_public/',
    'https://jenkins.library.illinois.edu/nexus/repository/uiuc_prescon_python_testing/'
    ]

wheelStashes = []

def getMacDevpiName(pythonVersion, format){
    if(format == 'wheel'){
        return "${pythonVersion.replace('.','')}-*macosx*.*whl"
    } else if(format == 'sdist'){
        return 'tar.gz'
    } else{
        error "unknown format ${format}"
    }
}

def get_sonarqube_unresolved_issues(report_task_file){
    script{

        def props = readProperties  file: '.scannerwork/report-task.txt'
        def response = httpRequest url : props['serverUrl'] + '/api/issues/search?componentKeys=' + props['projectKey'] + "&resolved=no"
        def outstandingIssues = readJSON text: response.content
        return outstandingIssues
    }
}

def sonarcloudSubmit(metadataFile, outputJson, sonarCredentials){
    def props = readProperties interpolate: true, file: metadataFile
    withSonarQubeEnv(installationName:'sonarcloud', credentialsId: sonarCredentials) {
        if (env.CHANGE_ID){
            sh(
                label: 'Running Sonar Scanner',
                script:"sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET} -Dsonar.cfamily.cache.enabled=false -Dsonar.cfamily.threads=\$(grep -c ^processor /proc/cpuinfo) -Dsonar.cfamily.build-wrapper-output=build/build_wrapper_output_directory"
                )
        } else {
            sh(
                label: 'Running Sonar Scanner',
                script: "sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME} -Dsonar.cfamily.cache.enabled=false -Dsonar.cfamily.threads=\$(grep -c ^processor /proc/cpuinfo) -Dsonar.cfamily.build-wrapper-output=build/build_wrapper_output_directory"
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


def build_packages(){
    script{
        def packages
        node(){
            checkout scm
            packages = load 'ci/jenkins/scripts/packaging.groovy'
        }
        def macBuildStages = [:]
            SUPPORTED_MAC_VERSIONS.each{ pythonVersion ->
                macBuildStages["MacOS x86_64 - Python ${pythonVersion}: wheel"] = {
                    packages.buildPkg(
                        agent: [
                            label: "mac && python${pythonVersion} && x86",
                        ],
                        buildCmd: {
                            withEnv([
                                '_PYTHON_HOST_PLATFORM=macosx-10.9-x86_64',
                                'ARCHFLAGS=-arch x86_64'
                            ]){
                                 sh(label: 'Building wheel',
                                    script: """python${pythonVersion} -m venv venv
                                               . ./venv/bin/activate
                                               python -m pip install --upgrade pip
                                               pip install wheel==0.37
                                               pip install build delocate
                                               python -m build --wheel
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
                            }
                        ]
                    )
                }
                macBuildStages["MacOS M1 - Python ${pythonVersion}: wheel"] = {
                    packages.buildPkg(
                        agent: [
                            label: "mac && python${pythonVersion} && m1",
                        ],
                        buildCmd: {
//                     Taken from cibuildwheel source code
//                     https://github.com/pypa/cibuildwheel/blob/main/cibuildwheel/macos.py
//
//                     # macOS 11 is the first OS with arm64 support, so the wheels
//                     # have that as a minimum.
                            withEnv([
                                '_PYTHON_HOST_PLATFORM=macosx-11.0-arm64',
                                'ARCHFLAGS=-arch arm64'
                                ]) {
                                 sh(label: 'Building wheel',
                                    script: """python${pythonVersion} -m venv venv
                                               . ./venv/bin/activate
                                               pip install --upgrade pip
                                               pip install wheel==0.37
                                               pip install build delocate
                                               python -m build --wheel
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
                                            [pattern: 'dist/', type: 'INCLUDE'],
                                        ],
                                    notFailBuild: true,
                                    deleteDirs: true
                                )
                            },
                            success: {
                                stash includes: 'dist/*.whl', name: "python${pythonVersion} m1 mac wheel"
                                wheelStashes << "python${pythonVersion} m1 mac wheel"
                            }
                        ]
                    )
                }
            }
            def windowsBuildStages = [:]
            SUPPORTED_WINDOWS_VERSIONS.each{ pythonVersion ->
                windowsBuildStages["Windows - Python ${pythonVersion}: wheel"] = {
                    packages.buildPkg(
                        agent: [
                            dockerfile: [
                                label: 'windows && docker && x86',
                                filename: 'ci/docker/python/windows/msvc/tox/Dockerfile',
                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        buildCmd: {
                            bat "py -${pythonVersion} -m pip wheel -v --no-deps -w ./dist ."
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
                            }
                        ]
                    )
                }
            }
            def buildStages =  [
               failFast: true,
                'Source Distribution': {
                    node('docker && linux') {
                        script{
                            try{
                                docker.image('python').inside {
                                    checkout scm
                                    sh(
                                        label: 'Building sdist',
                                        script: '''python -m venv venv --upgrade-deps
                                                   venv/bin/python -m pip install build
                                                   venv/bin/python -m build --sdist --outdir ./dist
                                        '''
                                        )
                                }
                                stash includes: 'dist/*.tar.gz,dist/*.zip', name: 'sdist'
                                wheelStashes << 'sdist'
                                archiveArtifacts artifacts: 'dist/*.tar.gz,dist/*.zip'
                            } finally {
                              cleanWs(
                                    patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE'],
                                        [pattern: 'venv/', type: 'INCLUDE'],
                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                    ],
                                    notFailBuild: true,
                                    deleteDirs: true
                                )
                            }
                        }
                    }
                }
            ]
            def linuxBuildStages = [:]
            SUPPORTED_LINUX_VERSIONS.each{ pythonVersion ->
                linuxBuildStages["Linux - Python ${pythonVersion} - x86: wheel"] = {
                    packages.buildPkg(
                        agent: [
                            dockerfile: [
                                label: 'linux && docker && x86',
                                filename: 'ci/docker/python/linux/package/Dockerfile',
                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg manylinux_image=quay.io/pypa/manylinux2014_x86_64'
                            ]
                        ],
                        buildCmd: {
                            sh(label: 'Building python wheel',
                               script:"""python${pythonVersion} -m build --wheel .
                                         auditwheel repair ./dist/*.whl -w ./dist
                                         """
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
                                stash includes: 'dist/*manylinux*.*whl', name: "python${pythonVersion} linux-x86 wheel"
                                wheelStashes << "python${pythonVersion} linux-x86 wheel"
                            }
                        ]
                    )
                }
                if(params.INCLUDE_ARM == true){
                    linuxBuildStages["Linux - Python ${pythonVersion} - ARM64: wheel"] = {
                        packages.buildPkg(
                            agent: [
                                dockerfile: [
                                    label: 'linux && docker && arm',
                                    filename: 'ci/docker/python/linux/package/Dockerfile',
                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg manylinux_image=quay.io/pypa/manylinux2014_aarch64'
                                ]
                            ],
                            buildCmd: {
                                sh(label: 'Building python wheel',
                                   script:"""python${pythonVersion} -m build --wheel .
                                             auditwheel repair ./dist/*.whl -w ./dist
                                             """
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
                                }
                            ]
                        )
                    }
                }
            }
            buildStages = buildStages + windowsBuildStages + linuxBuildStages
            if(params.BUILD_MAC_PACKAGES == true){
                buildStages = buildStages + macBuildStages
            }
            parallel(buildStages)
    }

}
def startup(){
    node('linux && docker') {
        try{
            checkout scm
            docker.image('python').inside {
                timeout(2){
                    stage('Getting Distribution Info'){
                        sh(
                           label: 'Running setup.py with dist_info',
                           script: '''python --version
                                      PIP_NO_CACHE_DIR=off python setup.py dist_info
                                   '''
                        )
                        stash includes: '*.dist-info/**', name: 'DIST-INFO'
                        archiveArtifacts artifacts: '*.dist-info/**'
                    }
                }
            }
        } finally{
            cleanWs(
                patterns: [
                        [pattern: '*.dist-info/**', type: 'INCLUDE'],
                        [pattern: '.eggs/', type: 'INCLUDE'],
                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                    ],
                notFailBuild: true,
                deleteDirs: true
            )
        }
    }
}
def get_mac_devpi_stages(packageName, packageVersion, devpiServer, devpiCredentials, stagingIndex, supportedPythonVersions){
    def devpi
     node('') {
        checkout scm
        devpi = load('ci/jenkins/scripts/devpi.groovy')
     }
    def macPackages = [:]
    supportedPythonVersions.each{pythonVersion ->
        macPackages["MacOS x86_64 - Python ${pythonVersion}: wheel"] = {
            withEnv([
                'PATH+EXTRA=./venv/bin'
            ]) {
                devpi.testDevpiPackage(
                    agent: [
                        label: "mac && python${pythonVersion} && x86 && devpi-access"
                    ],
                    devpi: [
                        index: stagingIndex,
                        server: devpiServer,
                        credentialsId: devpiCredentials,
                        devpiExec: 'venv/bin/devpi'
                    ],
                    package:[
                        name: packageName,
                        version: packageVersion,
                        selector: "(${pythonVersion.replace('.','')}).*(-*macosx_*).*(x86_64\\.whl)"
                    ],
                    test:[
                        setup: {
                            sh(
                                label: 'Installing Devpi client',
                                script: '''python3 -m venv venv
                                            venv/bin/python -m pip install pip --upgrade
                                            venv/bin/python -m pip install devpi_client tox
                                            '''
                            )
                        },
                        toxEnv: "py${pythonVersion}".replace('.',''),
                        teardown: {
                            sh( label: 'Remove Devpi client', script: 'rm -r venv')
                        }
                    ]
                )
            }
        }
        macPackages["MacOS m1 - Python ${pythonVersion}: wheel"] = {
            withEnv(['PATH+EXTRA=./venv/bin']) {
                devpi.testDevpiPackage(
                    agent: [
                        label: "mac && python${pythonVersion} && m1 && devpi-access"
                    ],
                    devpi: [
                        index: stagingIndex,
                        server: devpiServer,
                        credentialsId: devpiCredentials,
                        devpiExec: 'venv/bin/devpi'
                    ],
                    package:[
                        name: packageName,
                        version: packageVersion,
                        selector: "(${pythonVersion.replace('.','')}).*(-*macosx_*).*(arm64\\.whl)"
                    ],
                    test:[
                        setup: {
                            sh(
                                label:'Installing Devpi client',
                                script: '''python3 -m venv venv
                                            venv/bin/python -m pip install pip --upgrade
                                            venv/bin/python -m pip install devpi_client tox
                                            '''
                            )
                        },
                        toxEnv: "py${pythonVersion}".replace('.',''),
                        teardown: {
                            sh( label: 'Remove Devpi client', script: 'rm -r venv')
                        }
                    ]
                )
            }
        }
        macPackages["MacOS x86_64 - Python ${pythonVersion}: sdist"]= {
            withEnv([
                'PATH+EXTRA=./venv/bin'

            ]) {
                devpi.testDevpiPackage(
                    agent: [
                        label: "mac && python${pythonVersion} && x86 && devpi-access"
                    ],
                    devpi: [
                        index: stagingIndex,
                        server: devpiServer,
                        credentialsId: devpiCredentials,
                        devpiExec: 'venv/bin/devpi'
                    ],
                    package:[
                        name: packageName,
                        version: packageVersion,
                        selector: 'tar.gz'
                    ],
                    test:[
                        setup: {
                            sh(
                                label: 'Installing Devpi client',
                                script: '''python3 -m venv venv
                                            venv/bin/python -m pip install pip --upgrade
                                            venv/bin/python -m pip install devpi_client tox
                                            '''
                            )
                        },
                        toxEnv: "py${pythonVersion}".replace('.',''),
                        teardown: {
                            sh( label: 'Remove Devpi client', script: 'rm -r venv')
                        }
                    ]
                )
            }
        }
        macPackages["MacOS m1 - Python ${pythonVersion}: sdist"]= {
            withEnv(['PATH+EXTRA=./venv/bin']) {
                devpi.testDevpiPackage(
                    agent: [
                        label: "mac && python${pythonVersion} && m1 && devpi-access"
                    ],
                    devpi: [
                        index: stagingIndex,
                        server: devpiServer,
                        credentialsId: devpiCredentials,
                        devpiExec: 'venv/bin/devpi'
                    ],
                    package:[
                        name: packageName,
                        version: packageVersion,
                        selector: 'tar.gz'
                    ],
                    test:[
                        setup: {
                            sh(
                                label:'Installing Devpi client',
                                script: '''python3 -m venv venv
                                            venv/bin/python -m pip install pip --upgrade
                                            venv/bin/python -m pip install devpi_client tox
                                            '''
                            )
                        },
                        toxEnv: "py${pythonVersion}".replace('.',''),
                        teardown: {
                            sh( label: 'Remove Devpi client', script: 'rm -r venv')
                        }
                    ]
                )
            }
        }
    }
    return macPackages
}
def get_props(){
    stage('Reading Package Metadata'){
        node() {
            try{
                unstash 'DIST-INFO'
                def metadataFile = findFiles(excludes: '', glob: '*.dist-info/METADATA')[0]
                def package_metadata = readProperties interpolate: true, file: metadataFile.path
                echo """Metadata:

Name      ${package_metadata.Name}
Version   ${package_metadata.Version}
"""
                return package_metadata
            } finally {
                cleanWs(
                    patterns: [
                            [pattern: '*.dist-info/**', type: 'INCLUDE'],
                        ],
                    notFailBuild: true,
                    deleteDirs: true
                )
            }
        }
    }
}
startup()
props = get_props()

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
        booleanParam(name: 'BUILD_PACKAGES', defaultValue: false, description: 'Build Python packages')
        booleanParam(name: 'INCLUDE_ARM', defaultValue: false, description: 'Include ARM architecture')
        booleanParam(name: 'TEST_PACKAGES', defaultValue: true, description: 'Test Python packages by installing them and running tests on the installed package')
        booleanParam(name: 'BUILD_MAC_PACKAGES', defaultValue: false, description: 'Test Python packages on Mac')
        booleanParam(name: 'DEPLOY_PYPI', defaultValue: false, description: 'Deploy to pypi')
        booleanParam(name: 'DEPLOY_DEVPI', defaultValue: false, description: "Deploy to devpi on https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: 'DEPLOY_DEVPI_PRODUCTION', defaultValue: false, description: 'Deploy to production devpi on https://devpi.library.illinois.edu/production/release. Release Branch Only')
        booleanParam(name: 'DEPLOY_DOCS', defaultValue: false, description: 'Update online documentation. Release Branch Only')
    }
    stages {
        stage('Building'){
            agent {
                dockerfile {
                    filename 'ci/docker/python/linux/build/Dockerfile'
                    label 'linux && docker && x86'
                    additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL'
                }
            }
            stages{
                stage('Building Python Package'){
                    steps {
                        sh(
                            label: 'Building',
                            script: 'python3 setup.py build -b build --build-lib build/lib -t build/temp build_ext --inplace'
                        )
                    }
                }
                stage('Sphinx Documentation'){
                    steps {
                        sh(
                            label: 'Building docs',
                            script: 'python3 -m sphinx -b html docs/source build/docs/html -d build/docs/doctrees'
                        )
                    }
                    post{
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
                            zip archive: true, dir: 'build/docs/html', glob: '', zipFile: "dist/${props.Name}-${props.Version}.doc.zip"
                            stash includes: 'dist/*.doc.zip,build/docs/html/**', name: 'DOCS_ARCHIVE'
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
                                    filename 'ci/docker/python/linux/build/Dockerfile'
                                    label 'linux && docker && x86'
                                    additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL'
                                    args '--mount source=sonar-cache-uiucprescon-imagevalidate,target=/opt/sonar/.sonar/cache'
                                }
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
                                                       script: '''conan install . -if build/cpp -o "*:shared=True"
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
//                                                     recordIssues(
//                                                         tools: [
//                                                             gcc(pattern: 'logs/cmake-build.log'),
//                                                             [$class: 'Cmake', pattern: 'logs/cmake-build.log']
//                                                         ]
//                                                     )
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
//                                                             stash includes: 'reports/pytest.xml', name: 'PYTEST_REPORT'
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
//                                                             stash includes: 'logs/flake8.log', name: 'FLAKE8_REPORT'
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
//                                                     stash(includes: 'reports/coverage*.xml', name: 'PYTHON_COVERAGE_REPORT')
                                                    publishCoverage(
                                                        adapters: [
                                                                coberturaAdapter(mergeToOneReport: true, path: 'reports/coverage*.xml')
                                                            ],
                                                        sourceFileResolver: sourceFiles('STORE_ALL_BUILD'),
                                                   )
                                                }
                                            }
                                        }
                                        stage('Sonarcloud Analysis'){
                                            options{
                                                lock('uiucprescon.imagevalidate-sonarscanner')
                                            }
                                            when{
                                                equals expected: true, actual: params.USE_SONARQUBE
                                                beforeAgent true
                                                beforeOptions true
                                            }
                                            steps{
//                                                 unstash 'PYTHON_COVERAGE_REPORT'
//                                                 unstash 'PYTEST_REPORT'
//                                                 unstash 'FLAKE8_REPORT'
                                                unstash 'DIST-INFO'
                                                sh(
                                                label: 'Preparing c++ coverage data available for SonarQube',
                                                script: """mkdir -p build/coverage
                                                        find ./build -name '*.gcno' -exec gcov {} -p --source-prefix=${WORKSPACE}/ \\;
                                                        mv *.gcov build/coverage/
                                                        """
                                                )
                                                sonarcloudSubmit('uiucprescon.imagevalidate.dist-info/METADATA', 'reports/sonar-report.json', 'sonarcloud-uiucprescon.imagevalidate')
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
                stage('Run Tox'){
                    when{
                        equals expected: true, actual: params.TEST_RUN_TOX
                    }
                    steps {
                        script{
                            def tox
                            node(){
                                checkout scm
                                tox = load('ci/jenkins/scripts/tox.groovy')
                            }
                            def windowsJobs = [:]
                            def linuxJobs = [:]
                            stage('Scanning Tox Environments'){
                                parallel(
                                    'Linux':{
                                        linuxJobs = tox.getToxTestsParallel(
                                            envNamePrefix: 'Tox Linux',
                                            label: 'linux && docker && x86',
                                            dockerfile: 'ci/docker/python/linux/tox/Dockerfile',
                                            dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                            retry: 2
                                        )
                                    },
                                    'Windows':{
                                        windowsJobs = tox.getToxTestsParallel(
                                            envNamePrefix: 'Tox Windows',
                                            label: 'windows && docker && x86',
                                            dockerfile: 'ci/docker/python/windows/msvc/tox/Dockerfile',
                                            dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE',
                                            retry: 2
                                        )
                                    },
                                    failFast: true
                                )
                            }
                            parallel(windowsJobs + linuxJobs)
                        }
                    }
                }
            }

        }
        stage('Python Packaging'){
            when{
                anyOf{
                    equals expected: true, actual: params.BUILD_PACKAGES
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                }
                beforeAgent true
            }
            stages{
                stage('Building'){
                    steps{
                        build_packages()
                    }
                }
                stage('Testing'){
                    when{
                        equals expected: true, actual: params.TEST_PACKAGES
                    }
                    steps{
                        script{
                            def packages
                            node(){
                                checkout scm
                                packages = load 'ci/jenkins/scripts/packaging.groovy'
                            }
                            def macTestStages = [:]
                            SUPPORTED_MAC_VERSIONS.each{ pythonVersion ->
                                macTestStages["MacOS x86_64 - Python ${pythonVersion}: wheel"] = {
                                    packages.testPkg2(
                                        agent: [
                                            label: "mac && python${pythonVersion} && x86",
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash "python${pythonVersion} mac x86_64 wheel"
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.whl').each{
                                                sh(label: 'Running Tox',
                                                   script: """python${pythonVersion} -m venv venv
                                                   ./venv/bin/python -m pip install --upgrade pip
                                                   ./venv/bin/pip install tox
                                                   ./venv/bin/tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}"""
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
                                macTestStages["MacOS m1 - Python ${pythonVersion}: wheel"] = {
                                    packages.testPkg2(
                                        agent: [
                                            label: "mac && python${pythonVersion} && m1",
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash "python${pythonVersion} m1 mac wheel"
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.whl').each{
                                                sh(label: 'Running Tox',
                                                   script: """python${pythonVersion} -m venv venv
                                                   ./venv/bin/python -m pip install --upgrade pip
                                                   ./venv/bin/pip install tox
                                                   ./venv/bin/tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}"""
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
                                macTestStages["MacOS - Python ${pythonVersion}: sdist"] = {
                                    packages.testPkg2(
                                        agent: [
                                            label: "mac && python${pythonVersion} && x86",
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash 'sdist'
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.tar.gz').each{
                                                sh(label: 'Running Tox',
                                                   script: """python${pythonVersion} -m venv venv
                                                   ./venv/bin/python -m pip install --upgrade pip
                                                   ./venv/bin/pip install tox
                                                   ./venv/bin/tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}"""
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
                                macTestStages["MacOS m1 - Python ${pythonVersion}: sdist"] = {
                                    packages.testPkg2(
                                        agent: [
                                            label: "mac && python${pythonVersion} && m1",
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash 'sdist'
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.tar.gz').each{
                                                sh(label: 'Running Tox',
                                                   script: """python${pythonVersion} -m venv venv
                                                   ./venv/bin/python -m pip install --upgrade pip
                                                   ./venv/bin/pip install tox
                                                   ./venv/bin/tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}"""
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
                            def windowsTestStages = [:]
                            SUPPORTED_WINDOWS_VERSIONS.each{ pythonVersion ->
                                windowsTestStages["Windows - Python ${pythonVersion}: wheel"] = {
                                    packages.testPkg2(
                                        agent: [
                                            dockerfile: [
                                                label: 'windows && docker && x86',
                                                filename: 'ci/docker/python/windows/msvc/tox_no_vs/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                            ]
                                        ],
                                        dockerImageName: "${currentBuild.fullProjectName}_test_no_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
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
                                windowsTestStages["Windows - Python ${pythonVersion}: sdist"] = {
                                    packages.testPkg2(
                                        agent: [
                                            dockerfile: [
                                                label: 'windows && docker && x86',
                                                filename: 'ci/docker/python/windows/msvc/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                            ]
                                        ],
                                        dockerImageName: "${currentBuild.fullProjectName}_test_with_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                        testSetup: {
                                            checkout scm
                                            unstash 'sdist'
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.tar.gz').each{
                                                bat(label: 'Running Tox', script: "tox --workdir %TEMP%\\tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}")
                                            }
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
                                        ]
                                    )
                                }
                            }
                            def linuxTestStages = [:]
                            SUPPORTED_LINUX_VERSIONS.each{ pythonVersion ->
                                linuxTestStages["Linux - Python ${pythonVersion} - x86: wheel"] = {
                                    packages.testPkg2(
                                        agent: [
                                            dockerfile: [
                                                label: 'linux && docker && x86',
                                                filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                                            ]
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash "python${pythonVersion} linux-x86 wheel"
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
                                linuxTestStages["Linux - Python ${pythonVersion} - x86: sdist"] = {
                                    packages.testPkg2(
                                        agent: [
                                            dockerfile: [
                                                label: 'linux && docker && x86',
                                                filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                                            ]
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash 'sdist'
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.tar.gz').each{
                                                sh(
                                                    label: 'Running Tox',
                                                    script: "tox --installpkg ${it.path} --workdir /tmp/tox -e py${pythonVersion.replace('.', '')}"
                                                    )
                                            }
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
                                        ]
                                    )
                                }
                                if(params.INCLUDE_ARM == true){
                                    linuxTestStages["Linux - Python ${pythonVersion} - ARM64: wheel"] = {
                                        packages.testPkg2(
                                            agent: [
                                                dockerfile: [
                                                    label: 'linux && docker && arm',
                                                    filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
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
                                    linuxTestStages["Linux - Python ${pythonVersion} - ARM64: sdist"] = {
                                        packages.testPkg2(
                                            agent: [
                                                dockerfile: [
                                                    label: 'linux && docker && arm',
                                                    filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                                                ]
                                            ],
                                            testSetup: {
                                                checkout scm
                                                unstash 'sdist'
                                            },
                                            testCommand: {
                                                findFiles(glob: 'dist/*.tar.gz').each{
                                                    sh(
                                                        label: 'Running Tox',
                                                        script: "tox --installpkg ${it.path} --workdir /tmp/tox -e py${pythonVersion.replace('.', '')}"
                                                        )
                                                }
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
                                            ]
                                        )
                                    }
                                }

                            }

                            def testingStages = windowsTestStages + linuxTestStages
                            if(params.BUILD_MAC_PACKAGES == true){
                                testingStages = testingStages + macTestStages
                            }
                            parallel(testingStages)
                        }
                    }
                }
            }
        }
        stage('Deploy to Devpi'){
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: 'master', actual: env.BRANCH_NAME
                        equals expected: 'dev', actual: env.BRANCH_NAME
                        tag '*'
                    }
                }
                beforeAgent true
            }
            agent none
            options{
                lock('uiucprescon.imagevalidate-devpi')
            }
            stages{
                stage('Deploy to Devpi Staging') {
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/tox/Dockerfile'
                            label 'linux && docker && devpi-access'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                          }
                    }
                    options{
                        retry(3)
                    }
                    steps {
                        timeout(5){
                            unstash 'DOCS_ARCHIVE'
                            script{
                                wheelStashes.each{
                                    unstash it
                                }
                                def devpi = load('ci/jenkins/scripts/devpi.groovy')
                                devpi.upload(
                                    server: DEVPI_CONFIG.server,
                                    credentialsId: DEVPI_CONFIG.credentialsId,
                                    index: DEVPI_CONFIG_STAGING_INDEX,
                                )
                            }
                        }
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
                stage('Test DevPi packages') {
                    steps{
                        script{
                            def devpi
                            node(''){
                                checkout scm
                                devpi = load('ci/jenkins/scripts/devpi.groovy')
                            }
                            def macPackages = get_mac_devpi_stages(props.Name, props.Version, DEVPI_CONFIG.server, DEVPI_CONFIG.credentialsId, DEVPI_CONFIG_STAGING_INDEX, SUPPORTED_MAC_VERSIONS)
                            def windowsPackages = [:]
                            SUPPORTED_WINDOWS_VERSIONS.each{pythonVersion ->
                                windowsPackages["Windows - Python ${pythonVersion}: sdist"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/python/windows/msvc/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE',
                                                label: 'windows && docker && x86 && devpi-access'
                                            ]
                                        ],
                                        dockerImageName:  "${currentBuild.fullProjectName}_devpi_with_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                        devpi: [
                                            index: DEVPI_CONFIG_STAGING_INDEX,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                        ],
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'tar.gz'
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ],
                                        retry: 2
                                    )
                                }
                                windowsPackages["Test Python ${pythonVersion}: wheel Windows"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/python/windows/msvc/tox_no_vs/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE',
                                                label: 'windows && docker && x86 && devpi-access'
                                            ]
                                        ],
                                        devpi: [
                                            index: DEVPI_CONFIG_STAGING_INDEX,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                        ],
                                        dockerImageName:  "${currentBuild.fullProjectName}_devpi_without_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: "(${pythonVersion.replace('.','')}).*(win_amd64\\.whl)"
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ],
                                        retry: 2
                                    )
                                }
                            }
                            def linuxPackages = [:]
                            SUPPORTED_LINUX_VERSIONS.each{pythonVersion ->
                                linuxPackages["Linux - Python ${pythonVersion}: sdist"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                label: 'linux && docker && x86 && devpi-access'
                                            ]
                                        ],
                                        devpi: [
                                            index: DEVPI_CONFIG_STAGING_INDEX,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                        ],
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'tar.gz'
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ],
                                        retry: 2
                                    )
                                }
                                linuxPackages["Linux - Python ${pythonVersion}: wheel"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                label: 'linux && docker && x86 && devpi-access'
                                            ]
                                        ],
                                        devpi: [
                                            index: DEVPI_CONFIG_STAGING_INDEX,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                        ],
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: "(${pythonVersion.replace('.','')}).+(manylinux).+x86"
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ],
                                        retry: 2
                                    )
                                }
                            }
                            def devpiPackagesTesting = windowsPackages + linuxPackages
                            if (params.BUILD_MAC_PACKAGES){
                                 devpiPackagesTesting = devpiPackagesTesting + macPackages
                            }
                            parallel(devpiPackagesTesting)
                        }
                    }
                }
                stage('Deploy to DevPi Production') {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            anyOf {
                                branch 'master'
                                tag '*'
                            }
                        }
                        beforeAgent true
                        beforeInput true
                    }
                    options{
                      timeout(time: 1, unit: 'DAYS')
                    }
                    input {
                      message 'Release to DevPi Production?'
                    }
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/tox/Dockerfile'
                            label 'linux && docker && devpi-access'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                        }
                    }
                    steps {
                        script{
                            def devpi = load('ci/jenkins/scripts/devpi.groovy')
                            echo 'Pushing to production/release index'
                            devpi.pushPackageToIndex(
                                pkgName: props.Name,
                                pkgVersion: props.Version,
                                server: DEVPI_CONFIG.server,
                                indexSource: "DS_Jenkins/${DEVPI_CONFIG_STAGING_INDEX}",
                                indexDestination: 'production/release',
                                credentialsId: DEVPI_CONFIG.credentialsId
                            )
                        }
                    }
                }
            }
            post{
                success{
                    node('linux && docker && devpi-access') {
                        script{
                            if (!env.TAG_NAME?.trim()){
                                checkout scm
                                devpi = load 'ci/jenkins/scripts/devpi.groovy'
                                docker.build('imagevalidate:devpi','-f ./ci/docker/python/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL .').inside{
                                    devpi.pushPackageToIndex(
                                        pkgName: props.Name,
                                        pkgVersion: props.Version,
                                        server: DEVPI_CONFIG.server,
                                        indexSource: "DS_Jenkins/${DEVPI_CONFIG_STAGING_INDEX}",
                                        indexDestination: "DS_Jenkins/${env.BRANCH_NAME}",
                                        credentialsId: DEVPI_CONFIG.credentialsId
                                    )
                                }
                            }
                        }
                    }
                }
                cleanup{
                    node('linux && docker && devpi-access') {
                        script{
                            checkout scm
                            devpi = load 'ci/jenkins/scripts/devpi.groovy'
                            docker.build('imagevalidate:devpi','-f ./ci/docker/python/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL .').inside{
                                devpi.removePackage(
                                    pkgName: props.Name,
                                    pkgVersion: props.Version,
                                    index: "DS_Jenkins/${DEVPI_CONFIG_STAGING_INDEX}",
                                    server: DEVPI_CONFIG.server,
                                    credentialsId: DEVPI_CONFIG.credentialsId,

                                )
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
                            filename 'ci/docker/python/linux/build/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL'
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
                                choices: PYPI_SERVERS,
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
                            def pypi = fileLoader.fromGit(
                                    'pypi',
                                    'https://github.com/UIUCLibrary/jenkins_helper_scripts.git',
                                    '2',
                                    null,
                                    ''
                                )
                            pypi.pypiUpload(
                                credentialsId: 'jenkins-nexus',
                                repositoryUrl: SERVER_URL,
                                glob: 'dist/*'
                                )
                        }
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
                            filename 'ci/docker/python/linux/build/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL'
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
