pipeline {
  agent any
  stages {
    stage('Buildout') {
      steps {
        node(label: 'standalone') {
          dir(path: '/var/jenkins_home/worker/workspace/') {
            sh '''if [ ! -d "eea.plonebuildout.example" ]; then
  git clone https://github.com/eea/eea.plonebuildout.example.git
fi
cd eea.plonebuildout.example
git pull

./install.sh
bin/python bin/buildout -c jenkins.cfg
bin/python bin/test -v -vv -s eea.plonebuildout.profile
./bin/uptest
cd ../
rm -rf eea.plonebuildout.example'''
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
}