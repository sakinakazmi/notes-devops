pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    triggers {
        githubPush()
    }

    environment {
        COMPOSE_FILE = 'docker-compose.ci.yml'
        PROJECT      = 'notes-ci'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Syntax check (Docker Pipeline)') {
            steps {
                script {
                    docker.image('python:3.11-slim').inside {
                        sh 'python -m py_compile app.py'
                    }
                }
            }
        }

        stage('Build and deploy') {
            steps {
                sh 'docker compose -p $PROJECT -f $COMPOSE_FILE up -d --force-recreate'
            }
        }

        stage('Verify') {
            steps {
                sh '''
                    for i in $(seq 1 36); do
                        if curl -sf http://localhost:8082/health; then
                            echo
                            exit 0
                        fi
                        sleep 5
                    done
                    docker compose -p $PROJECT -f $COMPOSE_FILE logs --tail=50
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            emailext(
                subject: '$PROJECT_NAME - Build #$BUILD_NUMBER - $BUILD_STATUS',
                body: 'Build result: $BUILD_STATUS\nJob: $PROJECT_NAME\nBuild: #$BUILD_NUMBER\nURL: $BUILD_URL\n\nChanges:\n${CHANGES}\n\nLog (last lines):\n${BUILD_LOG, maxLines=40}',
                recipientProviders: [developers(), requestor()],
                to: 'sakinaabbas2017@gmail.com'
            )
        }
    }
}
