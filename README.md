# 🚀 FastAPI Job Tracker API

A professional REST API for job application management built with FastAPI, PostgreSQL, and modern deployment practices.

## 🌟 Live Demo

- **API Documentation**: [https://your-api.onrender.com/docs](https://your-api.onrender.com/docs)
- **Health Check**: [https://your-api.onrender.com/health](https://your-api.onrender.com/health)

## ✨ Features

### Core API Functionality
- **Complete CRUD Operations** for job applications
- **User Authentication** with secure JWT tokens
- **PostgreSQL Integration** with SQLAlchemy ORM
- **Automatic API Documentation** with OpenAPI/Swagger
- **Input Validation** with Pydantic models
- **Error Handling** with detailed responses

### Production Features
- **Health Check Endpoints** for monitoring
- **CORS Configuration** for frontend integration
- **Database Connection Pooling** for performance
- **Environment-based Configuration** for deployment
- **Render.com Deployment** ready with auto-scaling

## 🔧 Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with bcrypt password hashing
- **Deployment**: Render.com with automatic CI/CD
- **Documentation**: OpenAPI/Swagger with interactive testing

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env

# Run development server
uvicorn main:app --reload

# Access API docs: http://localhost:8000/docs
```

### Production Deployment

1. **Push to GitHub** (this repository)
2. **Create Render Web Service**
3. **Add PostgreSQL Database**
4. **Deploy** - Automatic deployment on git push

## 📊 API Endpoints

### Job Applications
- `GET /api/jobs/` - List all applications
- `POST /api/jobs/` - Create new application
- `GET /api/jobs/{id}` - Get specific application
- `PUT /api/jobs/{id}` - Update application
- `DELETE /api/jobs/{id}` - Delete application

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### System
- `GET /health` - Health check
- `GET /docs` - Interactive documentation

## 🧪 Testing

```bash
# Test health endpoint
curl -X GET "http://localhost:8000/health"

# Create job application
curl -X POST "http://localhost:8000/api/jobs/" \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Tech Corp", "job_title": "Python Developer"}'
```

## 📦 Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
```

---

**Built by Aniket - Professional Python Developer**

*Production-ready FastAPI with PostgreSQL, authentication, and modern deployment practices.*
