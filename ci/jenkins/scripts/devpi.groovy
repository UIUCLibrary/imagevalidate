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
return this
