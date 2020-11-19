def build_mac_package(args = [:]){
    echo "label = ${args['label']}"
    def pythonPath =  args['pythonPath'] ? args['pythonPath']: "python3"
    echo "pythonPath = ${pythonPath}"
    echo "stash = ${args['stash']}"
    stage('Build wheel') {
        node(args['label']){
            sh(
                label: "Building wheel",
                script: "${pythonPath} -m pip wheel . --no-deps -w dist"
            )
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

