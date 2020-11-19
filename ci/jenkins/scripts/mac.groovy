def build_mac_package(args = [:]){

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

