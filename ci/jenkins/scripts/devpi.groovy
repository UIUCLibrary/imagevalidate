def upload(args = [:]){
    def credentialsId = args['credentialsId']
    def clientDir = args['clientDir'] ? args['clientDir']: './devpi'
    def index = args['index']
    def devpiExec = args['devpiExec'] ? args['devpiExec']: "devpi"
    withEnv([
            "DEVPI_INDEX=${index}",
            "DEVPI_SERVER=${args['server']}",
            "CLIENT_DIR=${clientDir}",
            "DEVPI=${devpiExec}"
        ]) {
        withCredentials([usernamePassword(
                            credentialsId: credentialsId,
                            passwordVariable: 'DEVPI_PASSWORD',
                            usernameVariable: 'DEVPI_USERNAME'
                        )
                            ])
        {
            sh(label: "Logging into DevPi",
               script: '''$DEVPI use $DEVPI_SERVER --clientdir $CLIENT_DIR
                          $DEVPI login $DEVPI_USERNAME --password=$DEVPI_PASSWORD --clientdir $CLIENT_DIR
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
    def clientDir = args['clientDir'] ? args['clientDir']: './devpi'
    def devpiExec = args['devpiExec'] ? args['devpiExec']: "devpi"
    def devpiIndex  = args['devpiIndex']
    def pkgName  = args['pkgName']
    def pkgVersion = args['pkgVersion']
    def pkgSelector = args['pkgSelector']
    def toxEnv = args['toxEnv']
    withEnv([
            "DEVPI_INDEX=${devpiIndex}",
            "DEVPI_SERVER=${args['server']}",
            "CLIENT_DIR=${clientDir}",
            "DEVPI=${devpiExec}"
        ]) {
        withCredentials([usernamePassword(
                                credentialsId: args['credentialsId'],
                                passwordVariable: 'DEVPI_PASSWORD',
                                usernameVariable: 'DEVPI_USERNAME'
                            )
                        ])
            {
            if(isUnix()){
                sh(label: "Logging into DevPi",
                   script: '''$DEVPI use $DEVPI_SERVER --clientdir $CLIENT_DIR
                              $DEVPI login $DEVPI_USERNAME --password=$DEVPI_PASSWORD --clientdir $CLIENT_DIR
                              $DEVPI use $DEVPI_INDEX --clientdir $CLIENT_DIR
                              '''
                   )

            } else {
                bat(label: "Logging into DevPi Staging",
                   script: '''%DEVPI% use %DEVPI_SERVER% --clientdir %CLIENT_DIR%
                              %DEVPI% login %DEVPI_USERNAME% --password=%DEVPI_PASSWORD% --clientdir %CLIENT_DIR%
                              %DEVPI% use %DEVPI_INDEX% --clientdir %CLIENT_DIR%
                              '''
                   )

            }
        }
        if(isUnix()){
            sh(
                label: "Running tests on Packages on DevPi",
                script: "${devpiExec} test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${pkgSelector} --clientdir ${clientDir} -e ${toxEnv} -v"
            )
        } else{
            bat(
                label: "Running tests on Packages on DevPi",
                script: "${devpiExec} test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${pkgSelector}  --clientdir ${clientDir} -e ${toxEnv} -v"
            )
        }
    }
}


return this
