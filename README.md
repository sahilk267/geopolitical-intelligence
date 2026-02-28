# Geopolitical Intelligence Platform

An academic, modular geopolitical intelligence platform for structured news analysis, risk governance, and content production.

## 🎯 System Overview

This platform provides:
- **News Ingestion** from RSS/API sources
- **Entity & Claim Extraction** for intelligence analysis
- **Contradiction Detection** across sources
- **Risk Governance Engine** with 4-dimensional scoring
- **Escalation Risk Index (ERI)** for conflict monitoring
- **Weekly Intelligence Briefs** with PDF export
- **AI-Assisted Script Generation**
- **Video Production Pipeline** orchestration
- **Audit & Governance** with immutable logs

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                       │
│  Dashboard | Content | Risk | ERI | Briefs | Audit | Admin  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                    │
│  Auth | Sources | Articles | Risk | ERI | Scripts | Videos  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Neo4j     │    │    Redis     │
│  (Primary)   │    │   (Graph)    │    │   (Queue)    │
└──────────────┘    └──────────────┘    └──────────────┘
```

## 📁 Project Structure

```
geopolitical-intelligence/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/   # API Routes
│   │   ├── core/               # Config & Security
│   │   ├── db/                 # Database
│   │   ├── models/             # SQLAlchemy Models
│   │   ├── services/           # Business Logic
│   │   │   ├── ingestion/      # RSS/API Fetching
│   │   │   ├── risk/           # Risk Assessment
│   │   │   ├── eri/            # ERI Calculation
│   │   │   ├── script/         # AI Script Generation
│   │   │   └── video/          # Video Pipeline
│   │   ├── engines/            # Core Engines
│   │   ├── graph/              # Neo4j Integration
│   │   └── utils/              # Utilities
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/         # UI Components
│   │   ├── pages/              # Page Components
│   │   ├── hooks/              # Custom Hooks
│   │   ├── services/           # API Clients
│   │   └── store/              # State Management
│   └── package.json
│
└── docs/                       # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Neo4j 5+
- Redis 7+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📊 Database Schema

### Core Tables

| Table | Description |
|-------|-------------|
| `users` | User accounts with roles |
| `sources` | RSS/API source configurations |
| `raw_articles` | Original fetched content |
| `normalized_articles` | Processed articles |
| `entities` | Extracted entities (people, countries, orgs) |
| `claims` | Structured claims from articles |
| `contradictions` | Detected claim conflicts |
| `risk_scores` | 4-dimensional risk assessments |
| `eri_assessments` | Escalation Risk Index data |
| `scripts` | AI-generated video scripts |
| `video_jobs` | Video production queue |
| `weekly_briefs` | Intelligence briefs |
| `audit_logs` | Immutable audit trail |

## 🔐 Authentication & Roles

| Role | Permissions |
|------|-------------|
| `admin` | Full system access |
| `editor_in_chief` | Can approve all content |
| `senior_editor` | Can approve moderate risk (≤60) |
| `junior_editor` | Can approve low risk (≤40) |
| `viewer` | Read-only access |

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Current user info

### Sources
- `GET /api/v1/sources` - List data sources
- `POST /api/v1/sources` - Create source
- `POST /api/v1/sources/{id}/test` - Test source
- `POST /api/v1/sources/{id}/fetch` - Fetch from source

### Articles
- `GET /api/v1/articles` - List articles
- `GET /api/v1/articles/{id}` - Get article
- `PUT /api/v1/articles/{id}/status` - Update status

### Risk Assessment
- `GET /api/v1/risk` - List risk assessments
- `POST /api/v1/risk/assess/{article_id}` - Assess article
- `POST /api/v1/risk/{id}/approve` - Approve assessment
- `PUT /api/v1/risk/config/safe-mode` - Toggle Safe Mode

### ERI
- `GET /api/v1/eri` - List ERI assessments
- `GET /api/v1/eri/current` - Current ERI
- `POST /api/v1/eri` - Create ERI assessment
- `POST /api/v1/eri/{id}/publish` - Publish ERI

### Weekly Briefs
- `GET /api/v1/briefs` - List briefs
- `POST /api/v1/briefs` - Create brief
- `POST /api/v1/briefs/{id}/publish` - Publish brief
- `GET /api/v1/briefs/{id}/export/pdf` - Export PDF

### Audit
- `GET /api/v1/audit` - List audit logs
- `GET /api/v1/audit/stats/summary` - Audit statistics

## 🛡 Risk Governance Engine

### 4-Dimensional Risk Scoring

| Dimension | Weight | Factors |
|-----------|--------|---------|
| Legal Risk | 30% | Defamation, accusations, named individuals |
| Defamation Risk | 30% | Reputational harm, source reliability |
| Platform Risk | 20% | Policy violations, religious framing |
| Political Risk | 20% | Sensitivity, geopolitical factors |

### Safe Mode

When enabled, content with high-risk factors is automatically blocked from publication.

## 📈 Escalation Risk Index (ERI)

### Dimensions

| Dimension | Weight | Indicators |
|-----------|--------|------------|
| Military Activity | 30% | Troop movements, airstrikes, deployments |
| Political Signaling | 15% | Diplomatic statements, sanctions |
| Proxy Activation | 20% | Militia activity, cross-border incidents |
| Economic Pressure | 15% | Oil prices, trade restrictions |
| Diplomatic Breakdown | 20% | Negotiation status, mediator engagement |

### Classifications

- **Low** (0-20): Stable situation
- **Moderate** (20-40): Some tensions
- **Elevated** (40-60): Increased risk
- **High** (60-80): Serious concern
- **Critical** (80-100): Imminent escalation

## 🎬 Video Production Pipeline

```
Script → TTS Generation → Avatar Rendering → FFmpeg Compositing → Export
```

### Pipeline Stages

1. **Script Generation** - AI generates structured script
2. **TTS Generation** - Convert script to audio
3. **Avatar Rendering** - Lip-sync avatar video
4. **Video Compositing** - Combine assets with FFmpeg
5. **Export** - Final video output

## 📋 Audit & Governance

All actions are logged with:
- User ID and role
- Action type and timestamp
- Risk score at time of action
- Safe Mode state
- Version hash

**Logs are immutable** - no deletion allowed.

## 🔧 Configuration

Key environment variables:

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_DB=geopolitical_intel

# Neo4j
NEO4J_URI=bolt://localhost:7687

# OpenAI
OPENAI_API_KEY=sk-...

# Risk Settings
SAFE_MODE_ENABLED=false
RISK_THRESHOLD=40
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📚 Documentation

- [API Documentation](http://localhost:8000/api/docs) - Swagger UI
- [Database Schema](docs/schema.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

Built for academic geopolitical analysis with focus on neutrality and structured methodology.
