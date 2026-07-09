# 🎫 AI Ticket Classifier

An AI-powered ticket classification system that automatically categorizes customer support tickets using Large Language Models (LLMs), vector embeddings, and Retrieval-Augmented Generation (RAG). The application is built with FastAPI, PostgreSQL, ChromaDB, Docker, and GitHub Actions, making it production-ready with monitoring and CI/CD.

---

# 📌 Overview

The AI Ticket Classifier helps support teams automatically classify customer tickets into the appropriate categories and priorities.

Instead of manually reviewing every ticket, the application uses semantic search and an LLM to understand the ticket content and generate intelligent classifications.

The project also includes containerization, monitoring, and CI/CD to simulate a real-world production environment.

---

# ✨ Features

- 🤖 AI-powered ticket classification
- 🧠 Semantic search using vector embeddings
- 📚 Retrieval-Augmented Generation (RAG)
- ⚡ FastAPI REST APIs
- 🐘 PostgreSQL database integration
- 🔍 ChromaDB vector database
- 🦙 Ollama LLM integration
- 🐳 Docker & Docker Compose support
- 📊 Prometheus metrics
- 📈 Grafana dashboards
- 🔄 GitHub Actions CI pipeline
- 🚀 Automatic Docker image deployment to Docker Hub

---

# 🏗️ Architecture

```
                    +----------------+
                    |    Frontend    |
                    +--------+-------+
                             |
                             |
                             ▼
                    +----------------+
                    |    FastAPI     |
                    +--------+-------+
                             |
          -------------------------------------
          |                  |               |
          ▼                  ▼               ▼
   PostgreSQL          ChromaDB         Ollama LLM
 (Ticket Storage)   (Vector Search)   (Classification)
          |
          ▼
    JSON Response
          |
          ▼
       Frontend

-----------------------------------------------

Monitoring

FastAPI
    │
    ▼
Prometheus
    │
    ▼
Grafana

-----------------------------------------------

CI/CD

Developer
     │
 git push
     │
     ▼
GitHub Actions
     │
     ▼
Build Docker Image
     │
     ▼
Push Image to Docker Hub
```

---

# 🛠️ Tech Stack

## Backend

- Python 3.11
- FastAPI
- Uvicorn

## AI & Machine Learning

- Ollama
- Embeddings
- ChromaDB
- RAG

## Database

- PostgreSQL
- SQLAlchemy

## Authentication

- JWT Authentication

## Containerization

- Docker
- Docker Compose

## Monitoring

- Prometheus
- Grafana

## CI/CD

- GitHub Actions
- Docker Hub

---

# 📂 Project Structure

```
ticket-classifier/
│
├── api/
├── core/
├── db/
├── models/
├── schemas/
├── services/
├── scripts/
├── frontend/
├── data/
├── chroma_db/
├── prometheus/
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Install the following software:

- Python 3.11+
- Docker Desktop
- Git
- Ollama

---

## Installation

Clone the repository

```bash
git clone https://github.com/Abhinayasomishetty/ticket-classifier.git

cd ticket-classifier
```

Create virtual environment

```bash
python -m venv venv311
```

Activate environment

Windows

```bash
venv311\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run with Docker

```bash
docker compose up --build
```

---

## Run Locally

Start FastAPI

```bash
uvicorn api.main:app --reload
```

Swagger UI

```
http://localhost:8000/docs
```

---

# 🔄 Project Workflow

1. User submits a ticket from the frontend.
2. FastAPI receives the request.
3. Request is validated using Pydantic.
4. Ticket text is converted into embeddings.
5. ChromaDB searches for similar tickets.
6. Retrieved context is sent to Ollama.
7. Ollama classifies the ticket.
8. Result is stored in PostgreSQL.
9. API returns the classification to the frontend.

---

# 📡 API Endpoints

| Method | Endpoint | Description |
|----------|------------------------|-------------------------|
| POST | /auth/register | Register User |
| POST | /auth/login | Login |
| POST | /tickets/classify | Classify Ticket |
| GET | /tickets | Get Tickets |
| GET | /docs | Swagger Documentation |

---

# 📊 Monitoring

Prometheus

```
http://localhost:9090
```

Grafana

```
http://localhost:3000
```

Default Login

```
Username: admin

Password: admin
```

---

# 🔁 CI/CD Pipeline

Implemented using GitHub Actions.

Pipeline includes:

- Checkout Repository
- Install Dependencies
- Check Python Version
- Verify Imports
- Build Docker Image
- Login to Docker Hub
- Push Docker Image Automatically

Every push to the `main` branch automatically builds and uploads the latest Docker image to Docker Hub.

---

# 📸 Screenshots

Add screenshots for:

- Swagger UI
- Ticket Classification
- Docker Desktop
- Prometheus Dashboard
- Grafana Dashboard
- GitHub Actions Workflow
- Docker Hub Repository

---

# 🔮 Future Improvements

- Deploy on AWS EC2
- Kubernetes deployment
- Role-Based Access Control (RBAC)
- Email notifications
- Redis caching
- Advanced analytics dashboard
- Multi-model LLM support
- CI/CD deployment to cloud

---

# 👩‍💻 Author

**Abhinaya Somishetty**

- GitHub: https://github.com/Abhinayasomishetty
- Docker Hub: https://hub.docker.com/u/abhinayasomishetty

---

## ⭐ If you like this project, don't forget to give it a star on GitHub!
