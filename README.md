<div align="center">
  
  <img src="https://capsule-render.vercel.app/api?type=waving&color=timeGradient&height=200&section=header&text=PREP-PILOT-AI&fontSize=50&fontAlignY=35&desc=AI-Powered%20Placement%20Preparation%20&descAlignY=60&descAlign=50" alt="Prep-Pilot-AI Header">

  <img src="https://readme-typing-svg.demolab.com?font=Inter&weight=600&size=20&duration=3000&pause=1000&color=6366F1&center=true&vCenter=true&width=600&lines=Master+DSA+and+System+Design;Crush+FAANG+Interviews;Powered+by+CRAG+and+Hybrid+Retrieval;Interactive+Company+Simulations" alt="Typing SVG" />

  <p><strong>Your intelligent companion for conquering software engineering interviews at FAANG and beyond.</strong></p>

  <!-- Badges -->
  <p>
    <a href="https://github.com/AyushGU12/PREP-PILOT-AI"><img src="https://img.shields.io/badge/Status-Beta-blue?style=for-the-badge&logo=github" alt="Status"></a>
    <a href="https://github.com/AyushGU12/PREP-PILOT-AI/releases"><img src="https://img.shields.io/badge/Version-v1.0.0-brightgreen?style=for-the-badge&logo=semver" alt="Version"></a>
    <a href="https://github.com/AyushGU12/PREP-PILOT-AI/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge&logo=opensourceinitiative" alt="License"></a>
    <a href="https://docker.com"><img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker" alt="Docker"></a>
  </p>
  <p>
    <a href="https://github.com/AyushGU12/PREP-PILOT-AI/stargazers"><img src="https://img.shields.io/github/stars/AyushGU12/PREP-PILOT-AI?style=flat-square&color=yellow&logo=github" alt="Stars"></a>
    <a href="https://github.com/AyushGU12/PREP-PILOT-AI/network/members"><img src="https://img.shields.io/github/forks/AyushGU12/PREP-PILOT-AI?style=flat-square&color=blue&logo=github" alt="Forks"></a>
    <a href="https://github.com/AyushGU12/PREP-PILOT-AI/issues"><img src="https://img.shields.io/github/issues/AyushGU12/PREP-PILOT-AI?style=flat-square&color=red&logo=github" alt="Issues"></a>
    <a href="https://github.com/AyushGU12/PREP-PILOT-AI/pulls"><img src="https://img.shields.io/github/issues-pr/AyushGU12/PREP-PILOT-AI?style=flat-square&color=green&logo=github" alt="Pull Requests"></a>
  </p>
</div>

---

## 2️⃣ Executive Overview

PREP-PILOT-AI is a production-grade, AI-powered interview preparation platform. It solves the fragmentation and generic feedback problem of modern interview preparation by combining highly accurate Retrieval-Augmented Generation (RAG) with company-specific interview simulations. 

Using a Corrective RAG (CRAG) LangGraph workflow and a hybrid retrieval engine (BM25 + ChromaDB + Cross-Encoder Reranking), the platform provides verifiable, hallucination-free guidance for Data Structures & Algorithms, System Design, and Behavioral interviews.

### Key Highlights
* **Deterministic Accuracy:** Implements a strict CRAG pipeline with built-in grader and critic agents to eliminate AI hallucinations.
* **Hybrid Retrieval Engine:** Combines semantic search (MiniLM) and lexical search (BM25) with cross-encoder reciprocal rank fusion.
* **Company-Specific Simulators:** Tailors mock interviews for Amazon, Google, Microsoft, Adobe, Flipkart, and Goldman Sachs based on known evaluation criteria.
* **Performance Analytics:** Real-time dashboards visualizing topic mastery, streak tracking, and AI-driven study recommendations.

---

## 3️⃣ Architecture

PREP-PILOT-AI utilizes an Event-Driven Layered Architecture built around a state-machine orchestrator (LangGraph).

### System Flow
```mermaid
graph TD
    %% Frontend
    U([User]) --> |Queries / Answers| F[React Frontend]
    F --> |REST API| API[FastAPI Backend]

    %% Backend Layer
    API --> |Workflow Trigger| O[LangGraph Orchestrator]
    
    %% AI Pipeline
    subgraph CRAG Pipeline
        O --> QR[Query Rewriter Agent]
        QR --> PA[Planner Agent]
        PA --> RA[Retriever Agent]
        RA --> GA[Grader Agent]
        GA --> |Ambiguous/Incorrect| CR[Critic Agent]
        CR --> |Refined Query| RA
        GA --> |Correct| AA[Answer Agent]
    end

    %% Data Layer
    subgraph Retrieval Engine
        RA --> HR[Hybrid Retriever]
        HR --> |Semantic| VDB[(ChromaDB)]
        HR --> |Lexical| BM25[(BM25 Index)]
        VDB & BM25 --> RERANK[Cross-Encoder Reranker]
        RERANK --> RA
    end

    %% Database & State
    AA --> API
    API --> |State/Progress| PG[(PostgreSQL)]
    API --> |Caching/Sessions| REDIS[(Redis)]
```

---

## 4️⃣ Tech Stack

<div align="center">

### Frontend
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)

### Backend & AI
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Llama 3](https://img.shields.io/badge/Llama_3-0466C8?style=for-the-badge&logo=meta&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink&logoColor=white) 

### Data & Infrastructure
![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white) ![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## 5️⃣ Project Structure

```text
📦 project-root
┣ 📂 backend
┃ ┣ 📂 agents          # LangChain agents (Rewriter, Planner, Grader)
┃ ┣ 📂 api             # FastAPI routes (Chat, Interview, Progress)
┃ ┣ 📂 data            # PDF Chunking, Embedders, Ingestion scripts
┃ ┣ 📂 database        # SQLAlchemy Models and connection
┃ ┣ 📂 graph           # LangGraph state machine and node definitions
┃ ┣ 📂 interview       # Company profiles and evaluator logic
┃ ┣ 📂 retrieval       # Hybrid retrieval and Cross-Encoder logic
┃ ┗ 📂 utils           # Configs, prompts, logging
┣ 📂 frontend
┃ ┣ 📂 src
┃ ┃ ┣ 📂 components    # ChatInterface, ProgressDashboard, CitationCard
┃ ┃ ┣ 📂 pages         # Home, Dashboard, Interview
┃ ┃ ┗ 📜 api.js        # Axios configuration
┃ ┣ 📜 tailwind.config.js
┃ ┗ 📜 vite.config.js
┣ 📜 requirements.txt
┣ 📜 docker-compose.yml
┗ 📜 .env.example
```

---

## 6️⃣ Features

### ✅ Completed
- **CRAG Workflow:** Full Corrective RAG pipeline ensuring verifiable AI responses.
- **Hybrid Retrieval:** BM25 lexical + MiniLM semantic search with cross-encoder reranking.
- **FAANG Simulators:** Tailored mock interviews for top tech companies.
- **Analytics Dashboard:** Streak tracking, skill mastery, and automated recommendations.
- **Glassmorphism UI:** Premium dark-mode React frontend with Tailwind CSS.

### 🚧 In Progress
- Voice-to-Text Interview Input
- Real-time Code Execution Environment (Sandbox)

### 📌 Planned
- Peer-to-Peer Mock Interviews
- Deep integration with LeetCode/GitHub profiles

---

## 7️⃣ Installation

### Prerequisites
* Node.js 18+
* Python 3.10+
* Docker & Docker Compose
* Groq API Key

### Local Setup via Docker

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AyushGU12/PREP-PILOT-AI.git
   cd PREP-PILOT-AI
   ```

2. **Environment Configuration:**
   ```bash
   cp .env.example .env
   # Edit .env and insert your GROQ_API_KEY
   ```

3. **Start Infrastructure (Postgres & Redis):**
   ```bash
   docker-compose up -d
   ```

4. **Start the Backend:**
   ```bash
   python -m venv venv
   source venv/bin/activate # Windows: .\venv\Scripts\Activate
   pip install -r requirements.txt
   
   cd backend
   uvicorn api.main:app --reload --port 8000
   ```

5. **Start the Frontend (in a new terminal):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

Access the UI at `http://localhost:5173`.

---

## 8️⃣ Configuration

### `.env.example`
```env
# Application Settings
ENVIRONMENT=development
APP_HOST=0.0.0.0
APP_PORT=8000

# Security (Placeholder)
SECRET_KEY=your_super_secret_key_here

# AI / LLM Configuration
GROQ_API_KEY=your_groq_api_key_here

# Database Configuration (Docker defaults)
DATABASE_URL=postgresql://prep_user:prep_pass@localhost:5432/placement_db
REDIS_URL=redis://localhost:6379/0
```

---

## 9️⃣ API Documentation

The backend exposes a self-documenting OpenAPI specification. Once running, visit:
* **Swagger UI:** `http://localhost:8000/docs`
* **ReDoc:** `http://localhost:8000/redoc`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/ask` | `POST` | Engage the CRAG pipeline for Q&A |
| `/api/interview/company/question` | `POST` | Generate targeted company questions |
| `/api/interview/company/evaluate` | `POST` | Grade candidate answers |
| `/api/progress/dashboard/{id}` | `GET` | Retrieve complete user analytics |

---

## 🔟 AI/ML Section

* **Orchestration:** LangGraph (State Machine for cyclical reasoning)
* **Inference Engine:** Groq API (Running `llama3-70b-8192`)
* **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (Local inference)
* **Reranker:** `cross-encoder/ms-marco-MiniLM-L-6-v2`
* **Lexical Index:** `rank-bm25` (Okapi)

### RAG Pipeline Flow
1. **Query Expansion:** Extracts missing context from chat history.
2. **Hybrid Retrieval:** Executes top-K parallel searches across ChromaDB and BM25.
3. **Reciprocal Rank Fusion:** Merges and deduplicates hits.
4. **Cross-Encoder Scoring:** Re-scores chunks for deep semantic relevance.
5. **Grading & Correction:** The `GraderAgent` evaluates relevance. If ambiguous, the `CriticAgent` corrects the context or forces a web fallback (simulated).

---

## 1️⃣1️⃣ Database Design

```mermaid
erDiagram
    USERS ||--o{ INTERVIEW_SESSIONS : starts
    USERS ||--o{ CHAT_HISTORY : logs
    INTERVIEW_SESSIONS ||--o{ QUESTION_ATTEMPTS : contains

    USERS {
        int id PK
        string username
        string email
    }
    INTERVIEW_SESSIONS {
        int id PK
        string session_id
        string company
        boolean is_completed
    }
    QUESTION_ATTEMPTS {
        int id PK
        string question
        string user_answer
        float score
        boolean would_proceed
    }
```

---

## 1️⃣2️⃣ Security

* **CORS:** Configured explicitly for frontend domains.
* **SQL Injection Protection:** Enforced via SQLAlchemy ORM parameter binding.
* **Dependency Scanning:** Automated via GitHub Dependabot (Planned).
* **Secret Management:** Strict `.env` parsing; keys never committed.

---

## 1️⃣3️⃣ Performance & Scalability

* **Connection Pooling:** SQLAlchemy configured with optimal connection pooling limits.
* **Local Embeddings:** Embedding and reranking run entirely locally on the CPU to eliminate network latency and third-party API costs for vector operations.
* **Inference Speed:** Utlizing Groq's LPU architecture achieves sub-second LLM inference latency even on the 70B parameter Llama 3 model.

---

## 1️⃣7️⃣ Deployment

The architecture supports horizontal scaling. For cloud environments:

* **Backend:** Deployable to AWS ECS or Render as a Docker container.
* **Frontend:** Optimized for Vercel or Netlify via Vite build.
* **Databases:** AWS RDS (Postgres) + AWS ElastiCache (Redis).

*Detailed Terraform scripts coming soon.*

---

## 1️⃣9️⃣ Roadmap

```mermaid
gantt
    title PREP-PILOT-AI Development Roadmap
    dateFormat  YYYY-MM-DD
    section Phase 1
    Core Foundation & CRAG Pipeline       :done,    des1, 2026-06-01, 2026-06-15
    section Phase 2
    FAANG Simulators & Analytics UI       :done,    des2, 2026-06-15, 2026-07-07
    section Phase 3
    Sandbox Code Execution                :active,  des3, 2026-07-08, 2026-07-20
    section Phase 4
    Voice Input & Multi-player Mock       :         des4, 2026-07-21, 2026-08-10
```

---

## 2️⃣0️⃣ Contributing

We welcome contributions! 
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 2️⃣6️⃣ License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=timeGradient&height=100&section=footer" alt="Footer">
  
  <p>Made with ❤️ by engineers, for engineers.</p>
  <p>⭐ Star this repository if you found it useful.</p>
</div>
## Deployment

## 🚀 Cloud Deployment Architecture

This project is fully optimized for cloud deployment with 100% parity to the local development environment. It supports a dual-architecture deployment model:

### 1. Platform Native (PaaS)
Pre-configured for zero-downtime deployment on platforms like Render, Vercel, or Firebase.
- Native configuration files (e.g., ender.yaml) are included for one-click deployments.
- Environment variables prioritize cloud APIs (Groq, Gemini, OpenAI) to ensure compatibility with free-tier memory limits.

### 2. Dockerized Containers
For isolated, infrastructure-agnostic deployment on VPS or Cloud Run.
- **Multi-stage Dockerfile**: Optimized for lightweight, fast builds.
- **docker-compose.yml**: Configured with strict health checks, network isolation, and unless-stopped restart policies.
- Automatically handles local dependencies and avoids local OOM crashes by prioritizing cloud inference APIs.

### 🔄 CI/CD Pipeline
Continuous Integration and Deployment is handled via GitHub Actions.
- Workflows are configured in .github/workflows/ to automatically test and deploy changes pushed to the main branch.
