---
title: Gaceta PDF Worker
emoji: 📑
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Gaceta PDF Worker
This is a background worker for the Colombian Congress Monitoring System.
It consumes tasks from RabbitMQ (CloudAMQP), downloads PDFs, and processes them using OCR and AI.
