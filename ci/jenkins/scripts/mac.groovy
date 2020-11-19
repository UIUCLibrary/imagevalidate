def build_mac_package(args = [:]){
    echo "label = ${args['label']}"
    echo "stash = ${args['stash']}"
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

