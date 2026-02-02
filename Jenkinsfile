pipeline {
    agent any

    stages {
        stage('Build and Deploy with Docker Compose') {
            steps {
                echo 'Building and deploying with Docker Compose...'

                sh '''
                    docker compose -f docker-compose.yml up -d --build
                '''

                echo 'Application deployed.'
            }
        }
    }
}
