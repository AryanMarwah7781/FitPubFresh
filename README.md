# AI Fitness Assistant API

Production-ready FastAPI application for AI-powered fitness coaching with comprehensive error handling, authentication, and cloud deployment support.

## 🚀 Features

- **Authentication & Authorization**: JWT-based user registration and login
- **AI Chat Interface**: Intelligent fitness coaching with conversation history
- **Health Monitoring**: Kubernetes-ready health checks and metrics
- **Production Patterns**: Proper error handling, logging, and validation
- **Cloud Ready**: Dockerized with Kubernetes deployment configurations

## 📋 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Chat & AI
- `POST /chat` - Chat with AI fitness assistant
- `GET /chat/history/{user_id}` - Get conversation history

### User Management
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `GET /stats` - Get user statistics

### Health & Monitoring
- `GET /health` - Comprehensive health check
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

## 🛠 Quick Start

### Local Development

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
python main_simple.py
# or
uvicorn main_simple:app --host 0.0.0.0 --port 8000 --reload
```

4. **Access API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Development

```bash
# Build the image
docker build -f Dockerfile.production -t fitpub-api .

# Run container
docker run -p 8000:8000 fitpub-api
```

### Docker Compose (Full Stack)

```bash
# Start all services (API + Database + Redis + Monitoring)
docker-compose up -d

# View logs
docker-compose logs -f fitpub-api

# Stop services
docker-compose down
```

## 🧪 Testing the API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. User Registration
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "John",
    "last_name": "Doe",
    "fitness_goals": "Build muscle and lose weight"
  }'
```

### 3. User Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 4. Chat with AI (with auth token)
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "What is a good workout for building chest muscles?",
    "context": {"user_level": "beginner"}
  }'
```

### 5. Get User Profile
```bash
curl -X GET "http://localhost:8000/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🏗 Architecture

### Project Structure
```
FitPubFresh/
├── main.py                 # Enhanced FastAPI app with full features
├── main_simple.py          # Simple version for testing
├── config.py              # Configuration management
├── exceptions.py          # Error handling
├── logging_config.py      # Logging setup
├── models/                # Pydantic data models
│   ├── __init__.py
│   ├── auth_models.py     # Authentication models
│   ├── chat_models.py     # Chat and conversation models
│   ├── health_models.py   # Health check models
│   ├── error_models.py    # Error response models
│   └── base_models.py     # Base model patterns
├── requirements-production.txt
├── Dockerfile.production
├── docker-compose.yml
├── k8s-production-api.yaml
└── .env.example
```

### Data Models

#### User Registration
```json
{
  "email": "user@example.com",
  "password": "secure123",
  "first_name": "John",
  "last_name": "Doe",
  "fitness_goals": "Build muscle and improve cardio"
}
```

#### Chat Request
```json
{
  "message": "What's a good workout for chest?",
  "conversation_id": "optional-conversation-id",
  "context": {
    "user_level": "intermediate",
    "available_equipment": ["dumbbells", "bench"]
  }
}
```

#### Chat Response
```json
{
  "message": "What's a good workout for chest?",
  "response": "Here's a great chest workout...",
  "conversation_id": "conv-123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2023-09-28T15:30:00Z",
  "tokens_used": 45,
  "response_time_ms": 1200
}
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-this` | JWT secret key |
| `DEBUG` | `false` | Debug mode |
| `ENVIRONMENT` | `production` | Deployment environment |
| `DATABASE_URL` | `None` | PostgreSQL connection string |
| `REDIS_URL` | `None` | Redis connection string |
| `MODEL_PATH` | `./models/mistral-7b-instruct` | AI model path |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `LOG_LEVEL` | `INFO` | Logging level |

### Production Configuration

For production deployment, ensure you set:
- Strong `SECRET_KEY`
- Proper database connections
- CORS origins restricted to your domains
- Enable monitoring and logging

## 🚢 Deployment

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

3. **Check health endpoints**
```bash
kubectl port-forward svc/fitpub-api-service 8000:80
curl http://localhost:8000/health/ready
curl http://localhost:8000/health/live
```

### AWS EKS Deployment

The API is configured to work with the existing EKS cluster:

```bash
# Ensure kubectl is configured for your EKS cluster
aws eks update-kubeconfig --region us-west-2 --name ai-fitness-dev

# Deploy the application
kubectl apply -f k8s-production-api.yaml

# Check deployment
kubectl get all -l app=fitpub-api
```

## 🔍 Monitoring & Observability

### Health Checks
- `/health` - Comprehensive health with system metrics
- `/health/ready` - Kubernetes readiness probe
- `/health/live` - Kubernetes liveness probe

### Logging
- Structured JSON logging in production
- Request/response logging with timing
- Error tracking with unique request IDs

### Metrics
- Response times
- Request counts
- System resource usage
- AI model performance

## 🔒 Security

- JWT-based authentication
- Password hashing with salt
- Input validation with Pydantic
- CORS configuration
- Rate limiting ready
- Environment-based security settings

## 🧪 Development Workflow

### Branch Structure
- `main` - Production ready code
- `feature/production-api` - Current development branch
- Feature branches for new development

### Testing
```bash
# Run tests
pytest

# Code formatting
black .
isort .

# Type checking  
mypy .
```

### API Documentation
- Auto-generated OpenAPI/Swagger docs at `/docs`
- ReDoc documentation at `/redoc`
- Interactive testing interface

## 🚀 Next Steps

1. **Database Integration**: Replace in-memory storage with PostgreSQL
2. **Real AI Model**: Integrate actual vLLM model in cloud deployment
3. **Caching**: Add Redis for session management and response caching
4. **Monitoring**: Set up Prometheus metrics and Grafana dashboards
5. **CI/CD**: Implement automated testing and deployment pipelines

## 📞 Support

For issues and questions:
- Check the `/health` endpoint for system status
- Review logs for error details
- Ensure proper environment configuration
- Verify JWT tokens are valid and not expired

## 📄 License

This project is part of the FitPubFresh fitness AI platform.