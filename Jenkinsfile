pipeline {
  agent any
  triggers {
    cron('H 0 * * 1-5')
  }

  stages {
    stage('Buildout') {
      steps {
        node(label: 'standalone') {
          dir(path: '/var/jenkins_home/worker/workspace/') {
            sh '''
if [ ! -d "eea.plonebuildout.example" ]; then
  git clone https://github.com/eea/eea.plonebuildout.example.git
fi
cd eea.plonebuildout.example
git pull

./install.sh
bin/python bin/buildout -c jenkins.cfg
bin/python bin/test -v -vv -s eea.plonebuildout.profile
./bin/uptest
cd ../
rm -rf eea.plonebuildout.example
'''
          }
        }
      }
    }

    stage('KGS') {
      steps {
        build '../eea.docker.kgs/master'
      }
    }

    stage('WWW') {
      steps {
        build '../eea.docker.plone-eea-www/master'
      }
    }

  }

  post {
    changed {
      script {
        def url = "${env.BUILD_URL}/display/redirect"
        def status = currentBuild.currentResult
        def subject = "${status}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
        def summary = "${subject} (${url})"
        def details = """<h1>${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - ${status}</h1>
                         <p>Check console output at <a href="${url}">${env.JOB_BASE_NAME} - #${env.BUILD_NUMBER}</a></p>
                      """

        def color = '#FFFF00'
        if (status == 'SUCCESS') {
          color = '#00FF00'
        } else if (status == 'FAILURE') {
          color = '#FF0000'
        }
        slackSend (color: color, message: summary)
        emailext (subject: '$DEFAULT_SUBJECT', to: '$DEFAULT_RECIPIENTS', body: details)
      }
    }
  }
}
