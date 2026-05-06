#!/bin/bash
git init
git config user.name "Aravind Rao"
git config user.email "aravind@example.com"
git add frontend/ docker-compose.yml
git commit -m "feat: scaffold react frontend and docker orchestration"

git add backend/app/db/
git commit -m "feat: initialize postgresql database schema and connection"

git add backend/app/services/
git commit -m "feat: implement mediapipe face detector and pillow annotator"

git add backend/app/routes/ backend/app/main.py
git commit -m "feat: integrate streaming api endpoints and async background worker"

git add backend/tests/
git commit -m "test: implement pytest suite for detection and ingestion routes"

git add .
git commit -m "docs: finalize readme and environment configs"

git branch -M main
git remote add origin git@github.com:rekcilyssup/Face-Detection-Video-Streaming-System.git
