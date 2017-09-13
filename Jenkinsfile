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
        build '../eea.docker.www/master'
      }
    }

  }

  post {
    changed {
      def message = "${currentBuild.result}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})"
      def colorCode = '#00FF00'
      if (currentBuild.result == 'FAILED') {
        colorCode = '#FF0000'
      }

      slackSend (color: colorCode, message: message)

      emailext (body: '$DEFAULT_BODY', subject: '$DEFAULT_SUBJECT', to: '$DEFAULT_RECIPIENTS')
    }
  }
}
