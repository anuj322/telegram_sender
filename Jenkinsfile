pipeline {
    agent any

   stages {
    stage('git clone') {
        echo 'Cloning repository...'
        git url: 'https://github.com/anujp4061/telegram-sender.git', branch: 'main'
        echo 'Repository cloned.'
    }
    stage('Build and Deploy with Docker Compose') {
        steps {
            echo 'Building and deploying with Docker Compose...'
            sh 'docker-compose up -d --build'
            echo 'Application deployed.'
        }
    }
    
   } 
}