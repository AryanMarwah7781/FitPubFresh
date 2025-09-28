# FitPubFresh - AI Fitness Assistant Platform

A comprehensive AI-powered fitness platform combining cloud infrastructure management and production-ready API services.

## 🏗️ Platform Overview

This project consists of two main components:
1. **AWS EKS Infrastructure** - Cost-optimized Kubernetes cluster for AI workloads
2. **AI Fitness API** - Production-ready FastAPI application for fitness coaching

---

## 🏠 AI Fitness Assistant API

Production-ready FastAPI application for AI-powered fitness coaching with comprehensive error handling, authentication, and cloud deployment support.

### 🚀 API Features

- **Authentication & Authorization**: JWT-based user registration and login
- **AI Chat Interface**: Intelligent fitness coaching with conversation history
- **Health Monitoring**: Kubernetes-ready health checks and metrics
- **Production Patterns**: Proper error handling, logging, and validation
- **Cloud Ready**: Dockerized with Kubernetes deployment configurations

### 📋 API Endpoints

#### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

#### Chat & AI
- `POST /chat` - Chat with AI fitness assistant
- `GET /chat/history/{user_id}` - Get conversation history

#### User Management
- `GET /profile` - Get user profile
- `GET /stats` - Get user statistics

#### Health & Monitoring
- `GET /health` - Comprehensive health check
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### 🛠 Quick Start

#### Local Development

1. **Install Dependencies**
```bash
pip install -r requirements-production.txt
```

2. **Set Environment Variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run the Application**
```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

4. **Access API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## ☁️ AWS EKS Infrastructure

Cost-optimized AWS EKS cluster setup for AI fitness application development and deployment.

### 📊 Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AWS EKS Cluster                      │
│                   ai-fitness-dev                        │
├─────────────────────────────────────────────────────────┤
│  Control Plane (Managed by AWS)                        │
│  ├── API Server                                        │
│  ├── etcd                                              │
│  └── Controller Manager                                │
├─────────────────────────────────────────────────────────┤
│  Worker Nodes (Auto-scaling: 1-4 nodes)                │
│  ├── Node Group: ai-fitness-workers (Spot)             │
│  ├── Instance Type: t3.medium                          │
│  ├── OS: Amazon Linux 2                                │
│  └── Storage: 20GB gp3 (encrypted)                     │
├─────────────────────────────────────────────────────────┤
│  Add-ons & Monitoring                                  │
│  ├── VPC CNI                                           │
│  ├── CoreDNS                                           │
│  ├── kube-proxy                                        │
│  ├── EBS CSI Driver                                    │
│  └── CloudWatch Logging                                │
└─────────────────────────────────────────────────────────┘
```

### 💰 Cost Management

| Resource | Quantity | Monthly Cost (USD) |
|----------|----------|-------------------|
| EKS Control Plane | 1 | ~$73.00 |
| t3.medium Spot Instances | 1-4 nodes | ~$15.00/node |
| EBS gp3 Storage | 20GB/node | ~$2.00/node |
| Data Transfer | Est. | ~$5.00 |
| **Total Estimated** | | **~$95-140/month** |

---

## � Deployment

### Kubernetes Deployment

1. **Apply Kubernetes manifests**
```bash
kubectl apply -f k8s-production-api.yaml
```

2. **Check deployment status**
```bash
kubectl get pods -l app=fitpub-api
kubectl get services fitpub-api-service
```

### Docker Deployment

```bash
# Build and run with Docker
docker build -f Dockerfile.production -t fitpub-api .
docker run -p 8000:8000 fitpub-api

# Or use Docker Compose
docker-compose up -d
```

## 🧪 Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

### User Registration & Login
```bash
# Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "John",
    "last_name": "Doe",
    "fitness_goals": "Build muscle and lose weight"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### Chat with AI
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "What is a good workout for building chest muscles?",
    "context": {"user_level": "beginner"}
  }'
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-this` | JWT secret key |
| `DEBUG` | `false` | Debug mode |
| `ENVIRONMENT` | `production` | Deployment environment |
| `MODEL_PATH` | `./models/mistral-7b-instruct` | AI model path |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `LOG_LEVEL` | `INFO` | Logging level |

## 🔒 Security Features

- JWT-based authentication with secure token handling
- Password hashing with salt
- Input validation with Pydantic models
- CORS configuration for cross-origin requests
- Environment-based security settings
- Encrypted EBS volumes in Kubernetes

## 🔍 Monitoring & Health Checks

- **Comprehensive health endpoint** with system metrics
- **Kubernetes readiness/liveness probes**
- **Request/response logging** with timing
- **Error tracking** with unique request IDs
- **Resource monitoring** (CPU, memory, disk usage)

## 🚀 Development Workflow

### Branch Structure
- `main` - Production ready code
- `feature/production-api` - API development
- `feature/eks-cluster-setup` - Infrastructure setup
- Feature branches for new development

### Getting Started
```bash
# Clone repository
git clone https://github.com/AryanMarwah7781/FitPubFresh.git
cd FitPubFresh

# For API development
git checkout feature/production-api
pip install -r requirements-production.txt
python main.py

# For infrastructure setup
git checkout feature/eks-cluster-setup
# Follow EKS setup instructions
```

## 🏷️ Project Structure

```
FitPubFresh/
├── main.py                 # Production FastAPI application
├── main_complex.py         # Enhanced version with advanced features
├── config.py              # Configuration management
├── exceptions.py           # Custom exception handling
├── logging_config.py       # Logging configuration
├── api_models/             # Pydantic data models
│   ├── auth_models.py      # Authentication models
│   ├── chat_models.py      # Chat and conversation models
│   ├── health_models.py    # Health check models
│   └── error_models.py     # Error response models
├── requirements-production.txt
├── Dockerfile.production
├── docker-compose.yml
├── k8s-production-api.yaml
├── .env.example
└── README.md
```

## � Next Steps

1. **Enhanced AI Integration**: Deploy actual AI models (Mistral, LLaMA)
2. **Database Integration**: PostgreSQL for persistent storage
3. **Caching Layer**: Redis for session management
4. **CI/CD Pipeline**: Automated testing and deployment
5. **Monitoring Stack**: Prometheus + Grafana
6. **API Gateway**: Load balancing and rate limiting

## 📞 Support & Documentation

- **API Docs**: Visit `/docs` when running locally
- **Health Status**: Check `/health` endpoint
- **Infrastructure**: EKS cluster monitoring via AWS console
- **Logs**: Application logs via kubectl or Docker logs

---

**⚡ Happy Building!** 🚀

This platform combines robust cloud infrastructure with production-ready API services for AI-powered fitness coaching.
