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

    stage('Release') {
      steps {
        parallel(

          "EEA Pull Requests": {
            node(label: 'eea') {
                sh '''wget -O github.py https://raw.githubusercontent.com/eea/eea.plonebuildout.core/master/tools/github.py'''
                sh '''python github.py warn'''
            }
          },

          "EEA Release candidates": {
            node(label: 'docker-1.13') {
              script {
                try {
                  sh '''docker run -i --net=host --name="$BUILD_TAG-eea" eeacms/www-devel /debug.sh bin/print_unreleased_packages src'''
                } catch (err) {
                  echo "Unstable: ${err}"
                } finally {
                  sh '''docker rm -v $BUILD_TAG-eea'''
                }
              }
            }
          },

          "PyPI Release candidates": {
            node(label: 'docker-1.13') {
              script {
                try {
                  sh '''docker run -i --net=host --name="$BUILD_TAG-pypi" eeacms/www-devel /debug.sh bin/print_pypi_plone_unreleased_eggs'''
                } catch (err) {
                  echo "Unstable: ${err}"
                } finally {
                  sh '''docker rm -v $BUILD_TAG-pypi'''
                }
              }
            }
          }

        )
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
