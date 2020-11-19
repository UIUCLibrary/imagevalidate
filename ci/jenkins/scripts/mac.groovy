def build_mac_package(args = [:]){
    echo "label = ${args['label']}"
    echo "stash = ${args['stash']}"
    stage('Build wheel') {
        node(args['label']){
            echo "HERE"
            sh "ls -la"
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

