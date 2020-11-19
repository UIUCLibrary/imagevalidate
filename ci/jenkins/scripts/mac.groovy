def build_mac_package(args = [:]){
    echo "label = ${args['label']}"
    def pythonPath =  args['pythonPath'] ? args['pythonPath']: "python3"
    def outPath = "dist"
    echo "pythonPath = ${pythonPath}"
    echo "stash = ${args['stash']}"

    stage('Build wheel') {
        node(args['label']){
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
            echo "HERE"
            sh "ls -la"
        }
    }
}

def test_mac_package(toxPath, pkgRegex){
    findFiles(glob: pkgRegex).each{
        sh(
            label: "Testing ${it}",
            script: "${toxPath} --installpkg=${it.path} -e py -vvv --recreate"
        )
    }
}

return this

