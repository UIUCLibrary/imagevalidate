def upload(args = [:]){
    def credentialsId = args['credentialsId']
    def clientDir = args['clientDir'] ? args['clientDir']: './devpi'
    def index = args['index']
    withEnv([
            "DEVPI_INDEX=${index}",
            "DEVPI_SERVER=${args['server']}",
            "CLIENT_DIR=${clientDir}"
        ]) {
        withCredentials([usernamePassword(
                            credentialsId: credentialsId,
                            passwordVariable: 'PASSWORD',
                            usernameVariable: 'USR'
                        )
                            ])
        {
            sh(label: "Logging into DevPi Staging",
               script: '''devpi use $DEVPI_SERVER --clientdir $CLIENT_DIR
                          devpi login $USR --password=$PASSWORD --clientdir $CLIENT_DIR
                          '''
               )
       }
        sh(
            label: "Uploading to DevPi Staging",
            script: """devpi use /DS_Jenkins/${index} --clientdir ${clientDir}
                       devpi upload --from-dir dist --clientdir ${clientDir}
                       """
           )
    }
}

def testDevpiPackage(args = [:]){
    def devpiExec = args['devpiExec']
    def devpiIndex  = args['devpiIndex']
    def devpiUsername = args['devpiUsername']
    def devpiPassword = args['devpiPassword']
    def pkgName  = args['pkgName']
    def pkgVersion = args['pkgVersion']
    def pkgSelector = args['pkgSelector']
    def toxEnv = args['toxEnv']
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


return this
