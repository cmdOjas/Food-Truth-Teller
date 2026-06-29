# Food Truth Teller

AI-powered personalized food product health analyzer with chatbot, barcode scanning, ML ingredient analysis, and full React Native mobile app.

## Architecture

```
food-truth-teller/
├── backend/        Flask REST API + JWT auth + OpenAI chatbot
├── frontend/       React Native mobile app (TypeScript + Redux)
├── ml/             scikit-learn training pipeline (Decision Tree + Random Forest)
├── database/       PostgreSQL schema
├── docker/         Dockerfiles
├── tests/          Pytest + Jest tests
└── docs/           API reference & deployment guide
```

## Quick Start (Docker)

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — set OPENAI_API_KEY and strong SECRET_KEY / JWT_SECRET_KEY

# Build and start ML training + backend + Postgres + Redis
docker compose --profile ml build
docker compose --profile ml up -d ml      # trains and saves models
docker compose up -d                       # starts backend + db + cache
```

Backend API: http://localhost:5000/api  
Swagger UI:  http://localhost:5000/api/docs

## Local Development

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env        # fill in your values

# Requires a running Postgres + Redis (or use Docker for those only)
docker compose up -d postgres redis

flask --app run.py create-db
flask --app run.py seed-db
python run.py
```

### ML Pipeline

```bash
cd ml
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords wordnet punkt

python dataset/generate_dataset.py   # creates food_health_dataset.csv
python train.py                       # trains + saves models/health_model.pkl
python predict.py "sugar, hydrogenated oil, red 40"   # quick test
```

### Frontend (React Native)

```bash
cd frontend
npm install
# iOS: cd ios && pod install && cd ..
npx react-native start
npx react-native run-android   # or run-ios
```

Set `REACT_NATIVE_API_URL=http://YOUR_LOCAL_IP:5000/api` in your environment.

## Running Tests

```bash
# Backend
cd backend && pip install -r requirements.txt
cd ../tests/backend && pytest -v

# ML
cd tests/ml && pytest -v

# Frontend
cd frontend && npm test
```

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis URL |
| `SECRET_KEY` | Flask secret key |
| `JWT_SECRET_KEY` | JWT signing key |
| `OPENAI_API_KEY` | OpenAI API key (GPT-4o-mini) |
| `ML_MODEL_PATH` | Path to trained `health_model.pkl` |
| `ML_VECTORIZER_PATH` | Path to trained `vectorizer.pkl` |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, receive JWT |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/profile` | Create/update health profile |
| GET | `/api/profile` | Get health profile |
| GET | `/api/product/:barcode` | Get product (+ OFF fallback) |
| POST | `/api/scan` | Scan barcode |
| POST | `/api/analyze` | ML analysis against user profile |
| POST | `/api/chat` | Streamed AI chat |
| GET | `/api/history` | List conversations |
| DELETE | `/api/history/:id` | Delete conversation |
| GET | `/api/recommendations` | Healthy product suggestions |

Full Swagger docs at `/api/docs` when backend is running.

## ML Pipeline

1. **Dataset**: 500+ labeled ingredient samples (Safe / Avoid)
2. **NLP**: lowercase → punctuation removal → lemmatization → additive normalization → TF-IDF
3. **Models**: Decision Tree vs Random Forest (best selected by F1)
4. **Outputs**: `models/health_model.pkl`, `plots/confusion_matrix_*.png`, `plots/roc_curve_*.png`

## Tech Stack

| Layer | Technology |
|---|---|
| Mobile | React Native 0.74, TypeScript, Redux Toolkit |
| Backend | Python 3.12, Flask 3, SQLAlchemy, Flask-JWT-Extended |
| Database | PostgreSQL 16, Redis 7 |
| ML | scikit-learn, pandas, NLTK, spaCy |
| AI | OpenAI GPT-4o-mini (streaming) |
| DevOps | Docker, Docker Compose |
