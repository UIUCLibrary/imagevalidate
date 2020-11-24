// @Library(["devpi", "PythonHelpers"]) _
def CONFIGURATIONS = loadConfigs()
wheel_stashes = []
def loadConfigs(){
    node(){
        echo "loading configurations"
        checkout scm
        return load("ci/jenkins/scripts/configs.groovy").getConfigurations()
    }
}


def run_dumpbin(glob){
    script{
        findFiles(glob: glob).each{
            bat(
                label: "Checking Python extension for dependents",
                script: "dumpbin /DEPENDENTS ${it.path}"
            )
        }
    }
}

def test_cpp_code(buildPath){
    stage("Build CPP"){
        tee("logs/cmake-build.log"){
            sh(label: "Testing CPP Code",
               script: """conan install . -if ${buildPath} -o "*:shared=True"
                          cmake -B ${buildPath} -Wdev -DCMAKE_TOOLCHAIN_FILE=build/conan_paths.cmake -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true -DBUILD_TESTING:BOOL=true -DCMAKE_CXX_FLAGS="-fprofile-arcs -ftest-coverage -Wall -Wextra"
                          cmake --build ${buildPath} -j \$(grep -c ^processor /proc/cpuinfo)
                          """
            )
        }
    }
    stage("CTest"){
        sh(label: "Running CTest",
           script: "cd ${buildPath} && ctest --output-on-failure --no-compress-output -T Test"
        )
    }
}

// def devpiRunTest(pkgPropertiesFile, devpiIndex, devpiSelector, devpiUsername, devpiPassword, toxEnv){
//     script{
//         def props = readProperties interpolate: true, file: pkgPropertiesFile
//         if (isUnix()){
//             sh(
//                 label: "Running test",
//                 script: """devpi use https://devpi.library.illinois.edu --clientdir certs/
//                            devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs/
//                            devpi use ${devpiIndex} --clientdir certs/
//                            devpi test --index ${devpiIndex} ${props.Name}==${props.Version} -s ${devpiSelector} --clientdir certs/ -e ${toxEnv} --tox-args=\"-vv\"
//                 """
//             )
//         } else {
//             bat(
//                 label: "Running tests on Devpi",
//                 script: """devpi use https://devpi.library.illinois.edu --clientdir certs\\
//                            devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs\\
//                            devpi use ${devpiIndex} --clientdir certs\\
//                            devpi test --index ${devpiIndex} ${props.Name}==${props.Version} -s ${devpiSelector} --clientdir certs\\ -e ${toxEnv} --tox-args=\"-vv\"
//                            """
//             )
//         }
//     }
// }

def devpiRunTest3(devpiClient, pkgName, pkgVersion, devpiIndex, devpiSelector, devpiUsername, devpiPassword, toxEnv){
    script{
        if(!fileExists(pkgPropertiesFile)){
            error "${pkgPropertiesFile} does not exist"
        }
        def props = readProperties interpolate: false, file: pkgPropertiesFile
        if (isUnix()){
            sh(
                label: "Running test",
                script: """${devpiClient} use https://devpi.library.illinois.edu --clientdir certs/
                           ${devpiClient} login ${devpiUsername} --password ${devpiPassword} --clientdir certs/
                           ${devpiClient} use ${devpiIndex} --clientdir certs/
                           ${devpiClient} test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${devpiSelector} --clientdir certs/ -e ${toxEnv} --tox-args=\"-vv\"
                """
            )
        } else {
            bat(
                label: "Running tests on Devpi",
                script: """devpi use https://devpi.library.illinois.edu --clientdir certs\\
                           devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs\\
                           devpi use ${devpiIndex} --clientdir certs\\
                           devpi test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${devpiSelector} --clientdir certs\\ -e ${toxEnv} --tox-args=\"-vv\"
                           """
            )
        }
    }
}
def testDevpiPackage2(devpiExec, devpiIndex, devpiUsername, devpiPassword,  pkgName, pkgVersion, pkgSelector, toxEnv){
    if(isUnix()){
        sh(
            label: "Running tests on Packages on DevPi",
            script: """${devpiExec} use https://devpi.library.illinois.edu --clientdir certs
                       ${devpiExec} login ${devpiUsername} --password ${devpiPassword} --clientdir certs
                       ${devpiExec} use ${devpiIndex} --clientdir certs
                       ${devpiExec} test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${pkgSelector} --clientdir certs -e ${toxEnv} -v
                       """
        )
    } else {
        bat(
            label: "Running tests on Packages on DevPi",
            script: """${devpiExec} use https://devpi.library.illinois.edu --clientdir certs\\
                       ${devpiExec} login ${devpiUsername} --password ${devpiPassword} --clientdir certs\\
                       ${devpiExec} use ${devpiIndex} --clientdir certs\\
                       ${devpiExec} test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${pkgSelector}  --clientdir certs\\ -e ${toxEnv} -v
                       """
        )
    }
}


def devpiRunTest2(devpiClient, pkgPropertiesFile, devpiIndex, devpiSelector, devpiUsername, devpiPassword, toxEnv){
    script{
        if(!fileExists(pkgPropertiesFile)){
            error "${pkgPropertiesFile} does not exist"
        }
        def props = readProperties interpolate: false, file: pkgPropertiesFile
        if (isUnix()){
            sh(
                label: "Running test",
                script: """${devpiClient} use https://devpi.library.illinois.edu --clientdir certs/
                           ${devpiClient} login ${devpiUsername} --password ${devpiPassword} --clientdir certs/
                           ${devpiClient} use ${devpiIndex} --clientdir certs/
                           ${devpiClient} test --index ${devpiIndex} ${props.Name}==${props.Version} -s ${devpiSelector} --clientdir certs/ -e ${toxEnv} --tox-args=\"-vv\"
                """
            )
        } else {
            bat(
                label: "Running tests on Devpi",
                script: """devpi use https://devpi.library.illinois.edu --clientdir certs\\
                           devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs\\
                           devpi use ${devpiIndex} --clientdir certs\\
                           devpi test --index ${devpiIndex} ${props.Name}==${props.Version} -s ${devpiSelector} --clientdir certs\\ -e ${toxEnv} --tox-args=\"-vv\"
                           """
            )
        }
    }
}


def remove_from_devpi(devpiExecutable, pkgName, pkgVersion, devpiIndex, devpiUsername, devpiPassword){
    script {
                try {
                    bat "${devpiExecutable} login ${devpiUsername} --password ${devpiPassword}"
                    bat "${devpiExecutable} use ${devpiIndex}"
                    bat "${devpiExecutable} remove -y ${pkgName}==${pkgVersion}"
                } catch (Exception ex) {
                    echo "Failed to remove ${pkgName}==${pkgVersion} from ${devpiIndex}"
            }

    }
}

def get_package_version(stashName, metadataFile){
    ws {
        unstash "${stashName}"
        script{
            def props = readProperties interpolate: true, file: "${metadataFile}"
            deleteDir()
            return props.Version
        }
    }
}

def devpiPushToIndex(pkgName, pkgVersion, sourceIndex, destinationIndex, devpiUsername, devpiPassword){
    if (!env.TAG_NAME?.trim()){
        docker.build("imagevalidate:devpi",'-f ./ci/docker/deploy/devpi/deploy/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
            withEnv(["DEVPI_USR=${devpiUsername}", "DEVPI_PSW=${devpiPassword}"]) {
                sh(
                    label: "Moving DevPi package from staging index to index",
                    script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                               devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                               devpi use ${sourceIndex} --clientdir ./devpi
                               devpi push ${pkgName}==${pkgVersion} ${destinationIndex} --clientdir ./devpi
                               """
                )
            }
        }
   }
}

def get_package_name(stashName, metadataFile){
    ws {
        unstash "${stashName}"
        script{
            def props = readProperties interpolate: true, file: "${metadataFile}"
            deleteDir()
            return props.Name
        }
    }
}
//

def get_sonarqube_unresolved_issues(report_task_file){
    script{

        def props = readProperties  file: '.scannerwork/report-task.txt'
        def response = httpRequest url : props['serverUrl'] + "/api/issues/search?componentKeys=" + props['projectKey'] + "&resolved=no"
        def outstandingIssues = readJSON text: response.content
        return outstandingIssues
    }
}

def sonarcloudSubmit(metadataFile, outputJson, sonarCredentials){
    def props = readProperties interpolate: true, file: metadataFile
    withSonarQubeEnv(installationName:"sonarcloud", credentialsId: sonarCredentials) {
        if (env.CHANGE_ID){
            sh(
                label: "Running Sonar Scanner",
                script:"sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET}"
                )
        } else {
            sh(
                label: "Running Sonar Scanner",
                script: "sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME}"
                )
        }
    }
     timeout(time: 1, unit: 'HOURS') {
         def sonarqube_result = waitForQualityGate(abortPipeline: false)
         if (sonarqube_result.status != 'OK') {
             unstable "SonarQube quality gate: ${sonarqube_result.status}"
         }
         def outstandingIssues = get_sonarqube_unresolved_issues(".scannerwork/report-task.txt")
         writeJSON file: outputJson, json: outstandingIssues
     }
}
def build_wheel(){
    if(isUnix()){
        sh(label: "Building Python Wheel",
           script: 'python -m pep517.build --binary .'
        )
    } else{
        bat(label: "Building Python Wheel",
            script: 'python -m pep517.build --binary .'
        )
    }
}

def fixup_wheel(wheelRegex, platform){
    script{
        if(platform == "linux"){
            sh "auditwheel repair ${wheelRegex} -w ./dist"
        }
    }
}

def getDevPiStagingIndex(){

    if (env.TAG_NAME?.trim()){
        return "tag_staging"
    } else{
        return "${env.BRANCH_NAME}_staging"
    }
}

def test_pkg(glob, timeout_time){

    findFiles( glob: glob).each{
        timeout(timeout_time){
            if(isUnix()){
                sh(label: "Testing ${it}",
                   script: """python --version
                              tox --installpkg=${it.path} -e py -vv
                              """
                )
            } else {
                bat(label: "Testing ${it}",
                    script: """python --version
                               tox --installpkg=${it.path} -e py -vv
                               """
                )
            }
        }
    }
}

def get_devpi_doc_archive_name(pkgName, pkgVersion){
    return "${pkgName}-${pkgVersion}.doc.zip"
}

def DEFAULT_DOCKER_FILENAME = "ci/docker/python/linux/build/Dockerfile"
def DEFAULT_DOCKER_LABEL = "linux && docker"
def DEFAULT_DOCKER_BUILD_ARGS = '--build-arg PYTHON_VERSION=3.7 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'

def startup(){
    node(){
        checkout scm
        tox = load("ci/jenkins/scripts/tox.groovy")
        mac = load("ci/jenkins/scripts/mac.groovy")
        devpiLib = load("ci/jenkins/scripts/devpi.groovy")
    }

//     mac.build_mac_package(
//         label: 'mac && 10.14 && python3.8',
//         pythonPath: 'python3.8',
//         stash: [
//             includes: 'dist/*.whl',
//             name: "MacOS 10.14 py38 wheel"
//         ]
//     )
    node('linux && docker') {
        try{
            checkout scm
            docker.image('python:3.8').inside {
                timeout(2){
                    stage("Getting Distribution Info"){
                        sh(
                           label: "Running setup.py with dist_info",
                           script: """python --version
                                      python setup.py dist_info
                                   """
                        )
                        stash includes: "uiucprescon.imagevalidate.dist-info/**", name: 'DIST-INFO'
                        archiveArtifacts artifacts: "uiucprescon.imagevalidate.dist-info/**"
                    }
                }
            }
        } finally{
            cleanWs(
               deleteDirs: true,
               patterns: [
                  [pattern: 'uiucprescon.imagevalidate.dist-info/', type: 'INCLUDE'],
              ]

           )
        }
    }
}

def get_props(){
    stage("Reading Package Metadata"){
        node() {
            try{
                unstash "DIST-INFO"
                def package_metadata = readProperties interpolate: true, file: "uiucprescon.imagevalidate.dist-info/METADATA"
                echo """Metadata:

Name      ${package_metadata.Name}
Version   ${package_metadata.Version}
"""
                return package_metadata
            } finally {
                deleteDir()
            }
        }
    }
}
startup()
def props = get_props()

pipeline {
    agent none
    options {
        timeout(time: 1, unit: 'DAYS')
    }
    parameters {
//         TODO: set defaultValue to true
        booleanParam(name: "RUN_CHECKS", defaultValue: false, description: "Run checks on code")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: false, description: "Run Tox Tests")
        booleanParam(name: "USE_SONARQUBE", defaultValue: true, description: "Send data test data to SonarQube")

//         TODO: set defaultValue to false
        booleanParam(name: "BUILD_PACKAGES", defaultValue: true, description: "Build Python packages")

//         TODO: set defaultValue to true
        booleanParam(name: "TEST_PACKAGES", defaultValue: false, description: "Test Python packages by installing them and running tests on the installed package")
        booleanParam(name: "BUILD_MAC_PACKAGES", defaultValue: false, description: "Test Python packages on Mac")
//         TODO: set defaultValue to false
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to devpi on https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to production devpi on https://devpi.library.illinois.edu/production/release. Release Branch Only")
        booleanParam(name: "DEPLOY_DOCS", defaultValue: false, description: "Update online documentation. Release Branch Only")
    }
    stages {
        stage("Building"){
            agent {
                dockerfile {
                    filename DEFAULT_DOCKER_FILENAME
                    label DEFAULT_DOCKER_LABEL
                    additionalBuildArgs DEFAULT_DOCKER_BUILD_ARGS
                }
            }
            stages{
                stage("Building Python Package"){
                    steps {
                        sh(
                            label: "Building",
                            script: 'CFLAGS="--coverage" python setup.py build -b build --build-lib build/lib -t build/temp build_ext --inplace'
                        )
                    }
                    post{
                        success{
                            stash includes: "build/**,uiucprescon/imagevalidate/*.dll,uiucprescon/imagevalidate/*.pyd,uiucprescon/imagevalidate/*.so", name: 'LINUX_BUILD_FILES'
                        }
                    }
                }
                stage("Sphinx Documentation"){
                    steps {
                        sh(
                            label: "Building docs",
                            script: 'python -m sphinx -b html docs/source build/docs/html -d build/docs/doctrees'
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
                            zip archive: true, dir: "build/docs/html", glob: '', zipFile: "dist/${get_devpi_doc_archive_name(props.Name, props.Version)}"
                            stash includes: "dist/*.doc.zip,build/docs/html/**", name: 'DOCS_ARCHIVE'
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
                           [pattern: ".eggs/", type: 'INCLUDE']
                       ]
                   )
               }
           }
        }
        stage("Checks"){
            when{
                equals expected: true, actual: params.RUN_CHECKS
            }
            stages{
                stage("Testing"){
                    stages{

                        stage('Testing Python') {
                            agent {
                                dockerfile {
                                    filename DEFAULT_DOCKER_FILENAME
                                    label DEFAULT_DOCKER_LABEL
                                    additionalBuildArgs DEFAULT_DOCKER_BUILD_ARGS
                                }
                            }
                            stages{
                                stage("Run Python Testing"){
                                    parallel {
                                        stage("Run PyTest Unit Tests"){
                                            steps{
                                                unstash "LINUX_BUILD_FILES"
                                                catchError(buildResult: "UNSTABLE", message: 'Did not pass all pytest tests', stageResult: "UNSTABLE") {
                                                    sh(
                                                        label: "Running Pytest",
                                                        script:'''mkdir -p reports/coverage
                                                                  coverage run --parallel-mode --source=uiucprescon -m pytest --junitxml=reports/pytest.xml --integration
                                                                  '''
                                                   )
                                               }
                                            }
                                            post {
                                                always {
                                                    junit "reports/pytest.xml"
                                                    stash includes: "reports/pytest.xml", name: "PYTEST_REPORT"
                                                }
                                            }
                                        }
                                        stage("Run Doctest Tests"){
                                           steps {
                                               catchError(buildResult: "SUCCESS", message: 'Doctest found issues', stageResult: "UNSTABLE") {
                                                   sh( label: "Running Doctest",
                                                       script: '''coverage run --parallel-mode --source=uiucprescon -m sphinx -b doctest docs/source build/docs -d build/docs/doctrees -v
                                                                  mkdir -p reports
                                                                  mv build/docs/output.txt reports/doctest.txt
                                                                  '''
                                                       )
                                               }
                                           }
                                        }
                                        stage("Run MyPy Static Analysis") {
                                            steps{
                                                catchError(buildResult: "SUCCESS", message: 'MyPy found issues', stageResult: "UNSTABLE") {
                                                    sh(
                                                        label: "Running Mypy",
                                                        script: '''mkdir -p logs
                                                                   mypy -p uiucprescon --html-report reports/mypy/html > logs/mypy.log
                                                                   '''
                                                   )
                                                }
                                            }
                                            post {
                                                always {
                                                    recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/mypy/html/", reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                                }
                                            }
                                        }
                                        stage("Run Flake8 Static Analysis") {
                                            steps{
                                                catchError(buildResult: "SUCCESS", message: 'Flake8 found issues', stageResult: "UNSTABLE") {
                                                    sh '''mkdir -p logs
                                                          flake8 uiucprescon --format=pylint --tee --output-file=logs/flake8.log
                                                          '''
                                                }
                                            }
                                            post {
                                                always {
                                                    recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                                                    stash includes: "logs/flake8.log", name: "FLAKE8_REPORT"
                                                }
                                            }
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
                                    stash(includes: 'reports/coverage*.xml', name: 'PYTHON_COVERAGE_REPORT')
                                }
                                cleanup{
                                    cleanWs(
                                        patterns: [
                                            [pattern: 'logs/', type: 'INCLUDE'],
                                            [pattern: 'reports/xml"', type: 'INCLUDE'],
                                        ]
                                    )
                                }
                            }
                        }
                        stage("Run Tox"){
                            when{
                                equals expected: true, actual: params.TEST_RUN_TOX
                            }
                            steps {
                                script{
                                    def windowsJobs
                                    def linuxJobs
                                    stage("Scanning Tox Environments"){
                                        parallel(
                                            "Linux":{
                                                linuxJobs = tox.getToxTestsParallel("Tox Linux", "linux && docker", "ci/docker/python/linux/tox/Dockerfile", '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)')
                                            },
                                            "Windows":{
                                                windowsJobs = tox.getToxTestsParallel("Tox Windows", "windows && docker", "ci/docker/python/windows/msvc/tox/Dockerfile", "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE")
                                            },
                                            failFast: true
                                        )
                                    }
                                    parallel(windowsJobs + linuxJobs)
                                }
                            }
                        }
                        stage('Testing CPP code') {
                            agent {
                                dockerfile {
                                    filename "ci/docker/cpp/Dockerfile"
                                    additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                    label "linux && docker"
                                }
                            }
                            steps{
                                test_cpp_code('build')
                            }
                            post{
                                always{
                                    recordIssues(tools: [gcc(pattern: 'logs/cmake-build.log'), [$class: 'Cmake', pattern: 'logs/cmake-build.log']])
                                    sh "mkdir -p reports && gcovr --filter uiucprescon/imagevalidate --print-summary  --xml -o reports/coverage_cpp.xml"
                                    stash(includes: "reports/coverage_cpp.xml", name: "CPP_COVERAGE_REPORT")
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
                                               pattern: "build/Testing/**/*.xml",
                                               skipNoTestFiles: true,
                                               stopProcessingIfError: true
                                           )
                                       ]
                                   )
                                }
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        patterns: [
                                            [pattern: 'build/', type: 'INCLUDE'],
                                        ]
                                    )
                                }
                            }
                        }
                    }
                    post{
                        always{
                            node(""){
                                unstash "PYTHON_COVERAGE_REPORT"
                                unstash "CPP_COVERAGE_REPORT"
                                publishCoverage(
                                    adapters: [
                                            coberturaAdapter(mergeToOneReport: true, path: 'reports/coverage*.xml')
                                        ],
                                    sourceFileResolver: sourceFiles('STORE_ALL_BUILD'),
                               )

                            }
                        }
                    }
                }
                stage("Sonarcloud Analysis"){
                    agent {
                        dockerfile {
                            filename 'ci/docker/sonarcloud/Dockerfile'
                            label 'linux && docker'
                        }
                    }
                    options{
                        lock("uiucprescon.imagevalidate-sonarscanner")
                    }
                    when{
                        equals expected: true, actual: params.USE_SONARQUBE
                        beforeAgent true
                        beforeOptions true
                    }
                    steps{
                        unstash "PYTHON_COVERAGE_REPORT"
                        unstash "PYTEST_REPORT"
                        unstash "FLAKE8_REPORT"
                        unstash "DIST-INFO"
                        sonarcloudSubmit("uiucprescon.imagevalidate.dist-info/METADATA", "reports/sonar-report.json", 'sonarcloud-uiucprescon.imagevalidate')
                    }
                    post {
                        always{
                            script{
                                if(fileExists('reports/sonar-report.json')){
                                    stash includes: "reports/sonar-report.json", name: 'SONAR_REPORT'
                                    archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/sonar-report.json'
                                    recordIssues(tools: [sonarQube(pattern: 'reports/sonar-report.json')])
                                }
                            }
                        }
                    }
                }
            }
        }
        stage("Packaging"){
            when{
                anyOf{
                    equals expected: true, actual: params.BUILD_PACKAGES
                    equals expected: true, actual: params.BUILD_MAC_PACKAGES
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                }
            }
            stages{
                stage('Creating Source Package') {
                    agent {
                        dockerfile {
                            filename DEFAULT_DOCKER_FILENAME
                            label DEFAULT_DOCKER_LABEL
                            additionalBuildArgs DEFAULT_DOCKER_BUILD_ARGS
                        }
                    }
                    steps {
                        sh "python -m pep517.build --source ."
                    }
                    post{
                        always{
                            stash includes: 'dist/*.zip,dist/*.tar.gz', name: "sdist"
                        }
                        success{
                            archiveArtifacts artifacts: "dist/*.zip,dist/*.tar.gz", fingerprint: true
                        }
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: 'dist/', type: 'INCLUDE'],
                                    [pattern: 'build/', type: 'INCLUDE'],
                                ]
                            )
                        }
                    }
                }
                stage("Mac Versions"){
                    when{
                        equals expected: true, actual: params.BUILD_MAC_PACKAGES
                        beforeAgent true
                    }
                    matrix{
                        agent none
                        axes{
                            axis {
                                name "PYTHON_VERSION"
                                values(
                                    "3.8",
                                    '3.9'
                                )
                            }
                        }
                        stages{
                            stage("Build"){
                                steps{
                                    script{
                                        def stashName = "MacOS 10.14 py${PYTHON_VERSION} wheel"
                                        mac.build_mac_package(
                                            label: "mac && 10.14 && python${PYTHON_VERSION}",
                                            pythonPath: "python${PYTHON_VERSION}",
                                            stash: [
                                                includes: 'dist/*.whl',
                                                name: stashName
                                            ]
                                        )
                                        wheel_stashes << stashName
                                    }
                                }
                            }
                            stage("Test Packages"){
                                when{
                                     equals expected: true, actual: params.TEST_PACKAGES
                                }
                                stages{
                                    stage("Test wheel"){
                                        steps{
                                            script{
                                                mac.test_mac_package(
                                                    label: "mac && 10.14 && python${PYTHON_VERSION}",
                                                    pythonPath: "python${PYTHON_VERSION}",
                                                    stash: "MacOS 10.14 py${PYTHON_VERSION} wheel",
                                                    glob: "dist/*.whl"
                                                )
                                            }
                                        }
                                    }
                                    stage("Test sdist"){
                                        steps{
                                            script{
                                                mac.test_mac_package(
                                                    label: "mac && 10.14 && python${PYTHON_VERSION}",
                                                    pythonPath: "python${PYTHON_VERSION}",
                                                    stash: "sdist",
                                                    glob: "dist/*.tar.gz,dist/*.zip"
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                stage('Testing Packages') {
                    when{
                        anyOf{
                            equals expected: true, actual: params.BUILD_PACKAGES
                            equals expected: true, actual: params.DEPLOY_DEVPI
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                        }
                    }
                    matrix{
                        agent none
                        axes{
                            axis {
                                name 'PLATFORM'
                                values(
                                    "linux",
                                    "windows"
                                )
                            }
                            axis {
                                name "PYTHON_VERSION"
                                values(
                                    "3.7",
                                    "3.8",
                                    '3.9'
                                )
                            }
                        }
                        stages{
                            stage("Creating bdist wheel"){
                                agent {
                                    dockerfile {
                                        filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.package.dockerfile}"
                                        label "${PLATFORM} && docker"
                                        additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.build.additionalBuildArgs}"
                                     }
                                }
                                steps{
                                    timeout(15){
                                        build_wheel()
                                        fixup_wheel("./dist/*.whl", PLATFORM)

                                    }
                                }
                                post{
                                    always{
                                        script{
                                            def stashName = "whl ${PLATFORM} ${PYTHON_VERSION}"
                                            if(PLATFORM == "linux"){
                                                stash includes: 'dist/*manylinux*.whl', name: stashName
                                            } else{
                                                stash includes: 'dist/*.whl', name: stashName
                                            }
                                            wheel_stashes << stashName
                                        }
                                    }
                                    success{
                                        archiveArtifacts artifacts: "dist/*.whl", fingerprint: true
                                    }
                                    cleanup{
                                        cleanWs(
                                            deleteDirs: true,
                                            patterns: [[pattern: 'dist/', type: 'INCLUDE']]
                                        )
                                    }
                                }
                            }
                            stage("Testing Python packages"){
                                when{
                                    anyOf{
                                        equals expected: true, actual: params.TEST_PACKAGES
                                    }
                                }
                                stages{
                                    stage("Testing wheel package"){
                                        agent {
                                            dockerfile {
                                                filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['whl'].dockerfile}"
                                                label "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['whl'].label}"
                                                additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['whl'].additionalBuildArgs}"
                                             }
                                        }
                                        steps{
                                            unstash "whl ${PLATFORM} ${PYTHON_VERSION}"
                                            catchError(stageResult: 'FAILURE') {
                                                test_pkg("dist/**/${CONFIGURATIONS[PYTHON_VERSION].pkgRegex['whl']}", 15)
                                            }
                                        }
                                        post{
                                            cleanup{
                                                cleanWs(
                                                    deleteDirs: true,
                                                    notFailBuild: true,
                                                    patterns: [
                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                        [pattern: '.tox/', type: 'INCLUDE'],
                                                    ]
                                                )
                                            }
                                        }
                                    }
                                    stage("Testing sdist package"){
                                        agent {
                                            dockerfile {
                                                filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['sdist'].dockerfile}"
                                                label "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['sdist'].label}"
                                                additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['sdist'].additionalBuildArgs}"
                                             }
                                        }
                                        steps{
                                            unstash "sdist"
                                            catchError(stageResult: 'FAILURE') {
                                                test_pkg("dist/**/${CONFIGURATIONS[PYTHON_VERSION].pkgRegex['sdist']}", 15)
                                            }
                                        }
                                        post{
                                            cleanup{
                                                cleanWs(
                                                    deleteDirs: true,
                                                    notFailBuild: true,
                                                    patterns: [
                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                        [pattern: '.tox/', type: 'INCLUDE'],
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
        }
        stage("Deploy to Devpi"){
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                        tag "*"
                    }
                }
            }
            agent none
            environment{
//                 DEVPI = credentials("DS_devpi")
                devpiStagingIndex = getDevPiStagingIndex()
            }
            options{
                lock("uiucprescon.imagevalidate-devpi")
            }
            stages{
                stage("Deploy to Devpi Staging") {
                    agent {
                        dockerfile {
                            filename 'ci/docker/deploy/devpi/deploy/Dockerfile'
                            label 'linux&&docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                          }
                    }
                    steps{
                        unstash "DOCS_ARCHIVE"
                        unstash "sdist"
                        script{
                            wheel_stashes.each{
                                unstash it
                            }
                            devpiLib.upload(
                                server: "https://devpi.library.illinois.edu",
                                credentialsId: "DS_devpi",
                                index: devpiStagingIndex,
                                clientDir: "./devpi"
                            )
                        }
                    }
                }
//                 stage("Deploy to Devpi Staging") {
//                     agent {
//                         dockerfile {
//                             filename 'ci/docker/deploy/devpi/deploy/Dockerfile'
//                             label 'linux&&docker'
//                             additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
//                           }
//                     }
//                     steps {
//                         script{
//                             wheel_stashes.each{
//                                 unstash it
//                             }
//                         }
//                         unstash "sdist"
//                         unstash "DOCS_ARCHIVE"
//                         sh(
//                             label: "Uploading to DevPi Staging",
//                             script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
//                                        devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
//                                        devpi use /${env.DEVPI_USR}/${env.devpiStagingIndex} --clientdir ./devpi
//                                        devpi upload --from-dir dist --clientdir ./devpi"""
//                         )
//                     }
//                 }
                stage("Test DevPi Package") {
                    stages{
                        stage("Test DevPi packages mac") {
                            when{
                                equals expected: true, actual: params.BUILD_MAC_PACKAGES
                            }
                            parallel{
                                stage("Wheel"){
                                    agent {
                                        label 'mac && 10.14 && python3.8'
                                    }
                                    steps{
                                        timeout(10){
                                            sh(
                                                label: "Installing devpi client",
                                                script: '''python3 -m venv venv
                                                           venv/bin/python -m pip install --upgrade pip
                                                           venv/bin/pip install devpi-client
                                                           venv/bin/devpi --version
                                                '''
                                            )
//                                             unstash "DIST-INFO"
                                            sh(
                                                        label: "Installing devpi client",
                                                        script: '''python3.8 -m venv venv
                                                                   venv/bin/python -m pip install --upgrade pip
                                                                   venv/bin/pip install devpi-client
                                                                   venv/bin/devpi --version
                                                        '''
                                                    )
                                                testDevpiPackage2(
                                                    "venv/bin/devpi",
                                                    env.devpiStagingIndex,
                                                    DEVPI_USR,
                                                    DEVPI_PSW,
                                                    props.Name,
                                                    props.Version,
                                                    "38-macosx_10_14_x86_64*.*whl",
                                                    "py38"
                                                )
//                                             devpiRunTest3(
//                                                 "venv/bin/devpi",
//                                                 props.Name,
//                                                 props.Version,
//                                                 env.devpiStagingIndex,
//                                                 "38-macosx_10_14_x86_64*.*whl",
//                                                 DEVPI_USR,
//                                                 DEVPI_PSW,
//                                                 "py38"
//                                             )
                                        }
                                    }
                                    post{
                                        cleanup{
                                            cleanWs(
                                                notFailBuild: true,
                                                deleteDirs: true,
                                                patterns: [
                                                    [pattern: 'venv/', type: 'INCLUDE'],
                                                ]
                                            )
                                        }
                                    }
                                }
                                stage("sdist"){
                                    agent {
                                        label 'mac && 10.14 && python3.8'
                                    }
                                    steps{
                                        timeout(10){
                                            sh(
                                                label: "Installing devpi client",
                                                script: '''python3 -m venv venv
                                                           venv/bin/python -m pip install --upgrade pip
                                                           venv/bin/pip install devpi-client
                                                           venv/bin/devpi --version
                                                '''
                                            )
                                            testDevpiPackage2(
                                                    "venv/bin/devpi",
                                                    env.devpiStagingIndex,
                                                    DEVPI_USR,
                                                    DEVPI_PSW,
                                                    props.Name,
                                                    props.Version,
                                                    "tar.gz",
                                                    "py38"
                                                )
//                                             unstash "DIST-INFO"
                                        }
                                    }
                                    post{
                                        cleanup{
                                            cleanWs(
                                                notFailBuild: true,
                                                deleteDirs: true,
                                                patterns: [
                                                    [pattern: 'venv/', type: 'INCLUDE'],
                                                ]
                                            )
                                        }
                                    }
                                }
                            }
                        }
                        stage("Test DevPi Packages for Windows and Linux"){
                            matrix {
                                axes {
                                    axis {
                                        name 'PLATFORM'
                                        values(
                                            "linux",
                                            "windows"
                                        )
                                    }
                                    axis {
                                        name 'PYTHON_VERSION'
                                        values(
                                            '3.7',
                                            '3.8',
                                            '3.9'
                                        )
                                    }
                                }
                                agent none
                                stages{
                                    stage("Testing DevPi wheel Package"){
                                        agent {
                                          dockerfile {
                                            additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['whl'].dockerfile.additionalBuildArgs}"
                                            filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['whl'].dockerfile.filename}"
                                            label "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['whl'].dockerfile.label}"
                                          }
                                        }
                                        steps{
                                            timeout(10){
                                                unstash "DIST-INFO"
                                                devpiRunTest2("devpi",
                                                    "uiucprescon.imagevalidate.dist-info/METADATA",
                                                    env.devpiStagingIndex,
                                                    CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].devpiSelector['whl'],
                                                    DEVPI_USR,
                                                    DEVPI_PSW,
                                                    CONFIGURATIONS[PYTHON_VERSION].tox_env
                                                )
                                            }
                                        }
                                    }
                                    stage("Testing DevPi sdist Package"){
                                        agent {
                                          dockerfile {
                                            additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['sdist'].dockerfile.additionalBuildArgs}"
                                            filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['sdist'].dockerfile.filename}"
                                            label "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['sdist'].dockerfile.label}"
                                          }
                                        }
                                        steps{
                                            timeout(10){
                                                unstash "DIST-INFO"
                                                devpiRunTest2("devpi",
                                                    "uiucprescon.imagevalidate.dist-info/METADATA",
                                                    env.devpiStagingIndex,
                                                    "tar.gz",
                                                    DEVPI_USR,
                                                    DEVPI_PSW,
                                                    CONFIGURATIONS[PYTHON_VERSION].tox_env
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                stage("Deploy to DevPi Production") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            anyOf {
                                branch "master"
                                tag "*"
                            }
                        }
                        beforeInput true
                    }
                    options{
                          timeout(time: 1, unit: 'DAYS')
                    }
                    input {
                      message 'Release to DevPi Production? '
                    }
                    agent {
                        dockerfile {
                            filename 'ci/docker/deploy/devpi/deploy/Dockerfile'
                            label 'linux&&docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                        }
                    }
                    steps {
                        sh(
                            label: "Pushing to production/release index",
                            script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                       devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                       devpi push --index DS_Jenkins/${env.devpiStagingIndex} ${props.Name}==${props.Version} production/release --clientdir ./devpi
                                       """
                        )
                    }
                }
            }
            post{
                success{
                    node('linux && docker') {
                        devpiPushToIndex(props.Name, props.Version, "/DS_Jenkins/${env.devpiStagingIndex}", "DS_Jenkins/${env.BRANCH_NAME}", env.DEVPI_USR, env.DEVPI_PSW)
                    }
                }
                cleanup{
                    node('linux && docker') {
                        script{
                            docker.build("imagevalidate:devpi",'-f ./ci/docker/deploy/devpi/deploy/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
                                sh(
                                    label: "Removing Package from DevPi staging index",
                                    script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                               devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                               devpi use /DS_Jenkins/${env.devpiStagingIndex} --clientdir ./devpi
                                                       devpi remove -y ${props.Name}==${props.Version} --clientdir ./devpi
                                                       """
                                )
                            }
                        }
                    }
                }
            }
        }
        stage("Release") {
            parallel {
                stage("Deploy Online Documentation") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DOCS
                            branch "master"
                        }
                        beforeAgent true
                        beforeInput true
                    }
                    input {
                        message 'Update project documentation'
                        parameters {
                            string(name: 'DEPLOY_DOCS_URL_SUBFOLDER', defaultValue: "imagevalidate", description: 'The directory that the docs should be saved under')
                        }
                    }
                    steps {
                        dir("build/docs/html/"){
                            sshPublisher(
                                publishers: [
                                    sshPublisherDesc(
                                        configName: 'apache-ns - lib-dccuser-updater',
                                        sshLabel: [label: 'Linux'],
                                        transfers: [
                                            sshTransfer(
                                                excludes: '',
                                                execCommand: '',
                                                execTimeout: 120000,
                                                flatten: false,
                                                makeEmptyDirs: false,
                                                noDefaultExcludes: false,
                                                patternSeparator: '[, ]+',
                                                remoteDirectory: "${params.DEPLOY_DOCS_URL_SUBFOLDER}",
                                                remoteDirectorySDF: false,
                                                removePrefix: '',
                                                sourceFiles: '**'
                                            )
                                        ],
                                        usePromotionTimestamp: false,
                                        useWorkspaceInPromotion: false,
                                        verbose: true
                                    )
                                ]
                            )
                        }
                    }
                }
            }
        }
    }
}
