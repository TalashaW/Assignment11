Assignment 11: Implement and Test a Calculation Model with Optional Factory Pattern
📋 Overview

This project implements a FastAPI calculator application with polymorphic calculation models using SQLAlchemy ORM. It includes password hashing, database validation, comprehensive testing, and automated CI/CD deployment to Docker Hub.
🔗 Links
GitHub Repository:     https://github.com/TalashaW/Assignment11
Docker Hub Repository: https://hub.docker.com/r/twin632/assignment11
Pull Docker Image:

docker pull twin632/assignment11:latest

🏗️ Architecture
User Model (SQLAlchemy)

    Fields: id, username, email, created_at, updated_atcreated_at, updated_at
    Constraints: Unique username and email
    Security: Bcrypt password hashing
    Base Model: Calculation with fields id, user_id, type, a, b, result, created_at, updated_at
    Subclasses: Addition, Subtraction, Multiplication, Division

Pydantic Schemas

    CalculationBase: Base validation for operations
    CalculationCreate: Validates calculation creation with user_id
    CalculationUpdate: Validates partial updates
    CalculationRead: Returns calculation results with metadata


Password Security

    Minimum 6 characters
    At least one uppercase letter
    At least one lowercase letter
    At least one digit
    Hashed using bcrypt before storage

🚀 Running Tests Locally
Prerequisites

    Python 3.10+
    PostgreSQL installed and running
    Git

1. Clone the Repository

git clone <your-repo-url>
cd <your-repo-name>

2. Set Up Virtual Environment

python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

3. Install Dependencies

pip install --upgrade pip
pip install -r requirements.txt

4. Set Up PostgreSQL Database

# Create a test database
createdb mytestdb

# Or using psql
psql -U postgres
CREATE DATABASE mytestdb;
\q

5. Configure Environment Variables

# Create a .env file or set environment variable
export DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_test_db

# On Windows PowerShell
$env:DATABASE_URL="postgresql://user:password@localhost:5432/fastapi_test_db"

6. Run All Tests

# Run all tests with coverage
pytest --cov=app --cov-report=term-missing -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run with detailed output
pytest -vv --tb=short

7. Run Specific Test Files

# Test calculation models (polymorphism)
pytest tests/integration/test_calculation.py -v

# Test user model
pytest tests/integration/test_user.py -v

# Test database functions
pytest tests/integration/test_database.py -v

# Test calculation schemas
pytest tests/integration/test_calculation_schema.py -v

# Test calculator operations
pytest tests/unit/test_calculator.py -v

# Test FastAPI endpoints
pytest tests/integration/test_fastapi_calculator.py -v

# Test E2E workflows
pytest tests/e2e/test_e2e.py -v

Expected Output

========================= test session starts =========================
collected 45 items

tests/e2e/test_e2e.py ......                                       [ 3%]
tests/integration/test_calculation.py..................            [ 36%]
tests/integration/test_calculation_schema_.py ..................   [ 68%]
tests/integration/test_fastapi_calculator.py ................      [ 74%]
tests/unit/test_calculator.py .....                                [100%]

collected 82 items


---------- coverage: platform win32, python 3.10.3-final-0 -----------
Name                         Stmts   Miss  Cover   Missing
----------------------------------------------------------
app/core/__init__.py             0      0   100%
app/core/config.py               8      0   100%
app/database.py                 17      0   100%
app/models/__init__.py           3      0   100%
app/models/calculation.py       74      0   100%
app/models/user.py              16      0   100%
app/operations/__init__.py      16      0   100%
app/schemas/__init__.py          2      0   100%
app/schemas/calculation.py      48      0   100%
----------------------------------------------------------
TOTAL                          184      0   100%

======================== 82 passed in 13.51s ================

🐳 Running with Docker
Pull and Run from Docker Hub

# Pull the latest image
docker pull twin632/assignment11:latest

# Run the container
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/db \
  --name fastapi-app \
  twin632/assignment11:latest

# Check logs
docker logs fastapi-app

# Access the application
curl http://localhost:8000/health

# Stop and remove
docker stop fastapi-app && docker rm fastapi-app

Build Locally

# Build the image
docker build -t assignment11:local .

# Run locally built image
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@localhost:5432/mytestdb \
  assignment10:local

Docker Compose (Optional)

# If you have docker-compose.yml
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

🔄 CI/CD Pipeline
GitHub Actions Workflow

The CI/CD pipeline automatically:

    Test Stage
        Spins up a PostgreSQL container
        Runs unit tests with coverage
        Runs integration tests (User + Calculation models)
        Runs E2E tests with Playwright
        Uploads test results and coverage reports

    Security Stage
        Builds Docker image
        Scans for vulnerabilities using Trivy
        Fails on CRITICAL or HIGH severity issues

    Deploy Stage
        Builds multi-platform image (amd64, arm64)
        Pushes to Docker Hub with tags:
            twin632/assignment11:latest
            twin632/assignment11:<commit-sha>

Triggering the Pipeline

# Push to main branch
git add .
git commit -m "Your commit message"
git push origin main

# Or create a pull request
git checkout -b feature/new-feature
git push origin feature/new-feature
# Then create PR on GitHub

Viewing Pipeline Results

    Go to your GitHub repository
    Click on the Actions tab
    View workflow runs and logs
    Check Docker Hub for pushed images

🧪 Test Coverage

Current test coverage: ~99%
Unit Tests (23 tests)

    Pydantic schema validation
    Password validation rules
    Database connection and session management
    Model method testing

Integration Tests (22 tests)

    User registration and authentication
    Database constraints (unique email/username)
    Password hashing and verification
    Token creation and validation
    Transaction rollback scenarios

🔐 Security Features

    ✅ Non-root Docker user (appuser)
    ✅ Bcrypt password hashing
    ✅ SQL injection prevention (SQLAlchemy ORM)
    ✅ Input validation (Pydantic)
    ✅ Unique constraints on email/username
    ✅ JWT token authentication
    ✅ Automated vulnerability scanning (Trivy)
    ✅ Environment variable configuration
    ✅ Health check endpoint

🛠️ Technologies Used

    FastAPI: Modern web framework
    SQLAlchemy: ORM for database operations
    Pydantic: Data validation
    PostgreSQL: Relational database
    Pytest: Testing framework
    Docker: Containerization
    GitHub Actions: CI/CD automation
    Trivy: Security scanning

📝 API Endpoints

    GET /health - Health check endpoint
    POST /register - User registration
    POST /login - User authentication
    GET /users/me - Get current user profile
