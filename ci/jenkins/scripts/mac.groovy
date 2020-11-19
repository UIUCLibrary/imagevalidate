def build_mac_package(args = [:]){
    echo "label = ${args['label']}"
    def pythonPath =  args['pythonPath'] ? args['pythonPath']: "python3"
    def outPath = "dist"
    echo "pythonPath = ${pythonPath}"
    echo "stash = ${args['stash']}"

    stage('Build wheel') {
        node(args['label']){
            checkout scm
            try{
                sh(
                    label: "Building wheel",
                    script: "${pythonPath} -m pip wheel . --no-deps -w ${outPath}"
                )
                stash includes: args['stash']['includes'], name: args['stash']['name']
            } finally{
                cleanWs(
                    deleteDirs: true,
                    patterns: [
                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                        [pattern: outPath, type: 'INCLUDE'],
                    ]
                )
            }

        }
    }
    stage('Testing Packages'){
        node(args['label']){
            try{
                unstash args['stash']['name']
                sh(
                    label:"Installing tox",
                    script: """${pythonPath} -m venv venv
                               venv/bin/python -m pip install pip --upgrade
                               venv/bin/python -m pip install wheel
                               venv/bin/python -m pip install tox
                               """
                )
                findFiles(glob: "dist/*.whl").each{
                    sh(
                        label: "Testing ${it}",
                        script: "venv/bin/tox --installpkg=${it.path} -e py -vvv --recreate"
                    )
                }
            } finally {
                cleanWs(
                    deleteDirs: true,
                    patterns: [
                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                        [pattern: '.tox/', type: 'INCLUDE'],
                        [pattern: '*.egg-info/', type: 'INCLUDE'],
                        [pattern: 'venv/', type: 'INCLUDE'],
                        [pattern: outPath, type: 'INCLUDE'],
                    ]
                )
            }
        }
    }
}


return this

