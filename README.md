<div align="center">
  <h1>NeuraMach LearningPath 🎓</h1>
  <p><b>AI-powered Scholarship Matching & Personalized Roadmap Generator</b></p>
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=googlebard" />
  <img src="https://img.shields.io/badge/Amazon_AWS-232F3E?style=for-the-badge&logo=amazon-aws" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql" />
</div>

<br>

## 📖 Overview

LearningPath is an intelligent scholarship aggregator built for Indian students. It uses a **custom Rule Engine** to match students to state/central scholarships based on Caste, Income, Gender, State, and Course. 

Once matched, it leverages **Google Gemini 2.0 AI** to generate a highly personalized, step-by-step application roadmap explaining exactly what documents to upload, what to do first, and when deadlines approach.

The backend is fully prepared for **Serverless Cloud Deployment** via AWS Lambda (Mangum), integrated with AWS Cognito for JWT Authentication, and uses Amazon S3 for cloud roadmap storage.

## ✨ Core Features

* **Advanced Rule Engine**: Filters SQL datastore for matching eligibility criteria instantly.
* **AI-Powered Roadmaps**: Integrates `google-genai` to dynamically draft personalized next steps.
* **Cloud Ready**: Configured for AWS Lambda, Cognito JWT Auth, and S3 file uploading.
* **Graceful Fallback**: If AWS configs or Gemini keys are missing, the app continues to function seamlessly in offline/fallback modes.
* **Interactive Dashboard**: Ships with a single-file minimal UI (`index.html`) demonstrating the full architectural workflow.

## 🏗️ Architecture

```mermaid
graph LR
    A[POST /match (requires JWT)] --> B[Cognito Auth Check]
    B --> C[Rule Engine / Neon DB]
    C -->|Eligible List| D[Gemini 2.0 AI]
    D --> E[Generate JSON Roadmap]
    E --> F[Upload to Amazon S3]
    F --> G[JSON Response with S3 URL]
```

## 🚀 Quickstart (Local Development)

### 1. Prerequisites
- Python 3.10+
- A Neon Serverless PostgreSQL Database (or local Postgres)

### 2. Installation
```bash
git clone https://github.com/tejasghoti/learningPath-NM.git
cd learningPath-NM
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
# Required for Database
DATABASE_URL="postgresql://user:password@hostname/dbname?sslmode=require"

# Required for AI Generation (Optional: falls back to manual roadmap if missing)
GEMINI_API_KEY="your-gemini-key"

# Optional AWS Setup (Falls back to bypassed mode if missing)
AWS_ACCESS_KEY_ID="your_aws_key"
AWS_SECRET_ACCESS_KEY="your_aws_secret"
AWS_REGION="ap-south-1"

S3_BUCKET_NAME="neuramach-roadmaps-bucket"
COGNITO_USER_POOL_ID="ap-south-1_xxxxxxxxx"
COGNITO_CLIENT_ID="xxxxxxxxxxxxxxxxxxxxxx"
```

### 4. Run the Server
```bash
uvicorn app.main:app --reload --port 8005
```

### 5. Test the UI
Open `index.html` in your web browser. 
1. The UI will automatically populate the database via `/seed`.
2. Enter a student profile and watch the Real-Time Workflow Stepper process the AI generation!

## 📡 API Endpoints

Explore the full interactive documentation at `http://127.0.0.1:8005/docs` once the server is running.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/match` | **Core** — Run rule engine and generate AI roadmap |
| `POST` | `/seed` | Auto-populates 6 Indian scholarships to begin testing |
| `POST` | `/scholarships` | Add a new scholarship providing eligibility criteria |
| `GET`  | `/scholarships` | List all available scholarships |

## 🛡️ AWS Lambda Deployment
The FastAPI `app.main:app` is wrapped with `Mangum`. You can directly zip the project and deploy it to AWS Lambda.
```python
from mangum import Mangum
handler = Mangum(app)
```
