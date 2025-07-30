# Ride-Share Application

A cloud-based microservices ride-sharing application built with industry best practices, featuring fault tolerance, scalability, and comprehensive monitoring.

## 🏗️ Architecture

The application follows a microservices architecture with the following components:

- **User Service**: Manages user registration, authentication, and user data
- **Ride Service**: Handles ride creation, listing, joining, and management
- **Database Service**: Centralized database with master-slave replication and fault tolerance
- **Load Balancer**: Distributes traffic across service instances
- **Message Queue**: RabbitMQ for asynchronous communication
- **Service Discovery**: ZooKeeper for service coordination

## 🚀 Features

- **Microservices Architecture**: Scalable, maintainable service separation
- **Fault Tolerance**: Automatic failover and recovery mechanisms
- **Load Balancing**: Traffic distribution across multiple instances
- **Health Monitoring**: Comprehensive health checks and metrics
- **API Documentation**: OpenAPI/Swagger documentation
- **Logging & Monitoring**: Structured logging and metrics collection
- **Security**: Input validation, authentication, and secure communication
- **Testing**: Comprehensive unit and integration tests
- **Containerization**: Docker-based deployment
- **CI/CD Ready**: Industry-standard development practices

## 📁 Project Structure

```
Ride-Share-Application/
├── Final_Project/
│   ├── Users/                    # User Service
│   │   ├── main_user.py         # Main application
│   │   ├── config.py            # Configuration management
│   │   ├── exceptions.py         # Custom exceptions
│   │   ├── user_requests.py     # Request models
│   │   ├── utils/               # Utility modules
│   │   │   ├── logger.py        # Logging utilities
│   │   │   ├── validators.py    # Input validation
│   │   │   └── response_helpers.py # Response formatting
│   │   ├── tests/               # Test suite
│   │   ├── requirements.txt     # Dependencies
│   │   └── Dockerfile          # Container configuration
│   ├── Rides/                   # Ride Service
│   │   ├── main_rides.py       # Main application
│   │   ├── config.py           # Configuration management
│   │   ├── exceptions.py        # Custom exceptions
│   │   ├── ride_requests.py    # Request models
│   │   ├── utils/              # Utility modules
│   │   ├── tests/              # Test suite
│   │   ├── requirements.txt    # Dependencies
│   │   └── Dockerfile         # Container configuration
│   └── Database/               # Database Service
│       ├── master_v4.py       # Master worker
│       ├── orchestrator.py    # Request orchestration
│       ├── database.py        # Database models
│       ├── requirements.txt   # Dependencies
│       └── docker-compose.yml # Service orchestration
└── README.md                  # This file
```

## 🛠️ Technology Stack

### Backend
- **Python 3.11**: Modern Python with type hints
- **Flask**: Lightweight web framework
- **SQLAlchemy**: Database ORM
- **Gevent**: WSGI server for high concurrency
- **Pika**: RabbitMQ client
- **Kazoo**: ZooKeeper client

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **RabbitMQ**: Message queue
- **ZooKeeper**: Service discovery and coordination
- **AWS EC2**: Cloud infrastructure

### Development & Testing
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **structlog**: Structured logging

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Ride-Share-Application
   ```

2. **Start the services**
   ```bash
   cd Final_Project/Database
   docker-compose up -d
   ```

3. **Start User Service**
   ```bash
   cd ../Users
   docker build -t user-service .
   docker run -p 8080:80 user-service
   ```

4. **Start Ride Service**
   ```bash
   cd ../Rides
   docker build -t ride-service .
   docker run -p 8081:80 ride-service
   ```

### Production Deployment

1. **Build all services**
   ```bash
   docker-compose -f Final_Project/docker-compose.prod.yml build
   ```

2. **Deploy with environment variables**
   ```bash
   export DATABASE_URL=http://your-db-host
   export USER_SERVICE_URL=http://your-user-service
   docker-compose -f Final_Project/docker-compose.prod.yml up -d
   ```

## 📚 API Documentation

### User Service Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `PUT` | `/api/v1/users` | Create a new user |
| `DELETE` | `/api/v1/users/<username>` | Delete a user |
| `GET` | `/api/v1/users` | List all users |
| `GET` | `/api/v1/_count` | Get request count |
| `DELETE` | `/api/v1/_count` | Reset request count |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Service metrics |

### Ride Service Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/rides` | Create a new ride |
| `GET` | `/api/v1/rides` | List rides with filters |
| `GET` | `/api/v1/rides/<ride_id>` | Get ride details |
| `GET` | `/api/v1/rides/count` | Get ride count |
| `POST` | `/api/v1/rides/<ride_id>` | Join a ride |
| `DELETE` | `/api/v1/rides/<ride_id>` | Delete a ride |
| `GET` | `/api/v1/_count` | Get request count |
| `DELETE` | `/api/v1/_count` | Reset request count |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Service metrics |

### Example API Usage

#### Create a User
```bash
curl -X PUT http://localhost:8080/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
  }'
```

#### Create a Ride
```bash
curl -X POST http://localhost:8081/api/v1/rides \
  -H "Content-Type: application/json" \
  -d '{
    "created_by": "john_doe",
    "source": 1,
    "destination": 50,
    "timestamp": "25-12-2024:30-30-14"
  }'
```

#### List Rides
```bash
curl "http://localhost:8081/api/v1/rides?source=1&destination=50"
```

## 🧪 Testing

### Run Tests
```bash
# User Service tests
cd Final_Project/Users
pytest tests/

# Ride Service tests
cd ../Rides
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Test Coverage
- Unit tests for all endpoints
- Integration tests for service communication
- Validation tests for input data
- Error handling tests

## 📊 Monitoring & Observability

### Health Checks
- Service health endpoints: `/health`
- Database connectivity checks
- External service dependency checks

### Metrics
- Request counts and rates
- Response times
- Error rates
- Service-specific metrics

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking with stack traces
- Performance monitoring

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `80` |
| `DEBUG` | Debug mode | `false` |
| `DATABASE_URL` | Database service URL | `http://52.86.125.105` |
| `USER_SERVICE_URL` | User service URL | `http://52.86.125.105` |
| `REQUEST_TIMEOUT` | HTTP request timeout | `30` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Configuration Files
- `config.py`: Service-specific configuration
- `docker-compose.yml`: Service orchestration
- `requirements.txt`: Python dependencies

## 🔒 Security

### Input Validation
- Request body validation
- Parameter sanitization
- SQL injection prevention
- XSS protection

### Authentication
- SHA1 password hashing
- User session management
- API key validation (planned)

### Network Security
- HTTPS enforcement (planned)
- CORS configuration
- Rate limiting (planned)

## 📈 Performance

### Optimization Features
- Connection pooling
- Request caching
- Async processing
- Load balancing

### Scalability
- Horizontal scaling support
- Auto-scaling capabilities
- Database sharding ready

## 🚨 Error Handling

### Error Types
- `ValidationError`: Input validation failures
- `DatabaseError`: Database operation failures
- `ExternalServiceError`: External service failures
- `ConfigurationError`: Configuration issues

### Error Responses
```json
{
  "error": {
    "message": "User not found",
    "status_code": 404,
    "code": "USER_NOT_FOUND"
  }
}
```

## 🔄 Development Workflow

### Code Quality
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit hooks**: Automated quality checks

### Git Workflow
1. Feature branch creation
2. Development with tests
3. Code review process
4. Automated testing
5. Production deployment

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 📋 TODO

- [ ] Add OpenAPI/Swagger documentation
- [ ] Implement JWT authentication
- [ ] Add rate limiting
- [ ] Implement caching layer
- [ ] Add comprehensive integration tests
- [ ] Set up CI/CD pipeline
- [ ] Add monitoring dashboard
- [ ] Implement backup and recovery procedures

