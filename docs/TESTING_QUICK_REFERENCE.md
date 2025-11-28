# Testing & CI/CD Quick Reference

A quick command reference for running tests and managing the CI/CD pipeline.

## 🧪 Running Tests

### Unified Test Runner

```bash
# Run all tests
python run_tests.py

# Verbose mode
python run_tests.py -v

# Quiet mode
python run_tests.py -q

# Specific test module
python run_tests.py test_resume_parser
python run_tests.py test_embeddings
python run_tests.py test_scoring
python run_tests.py test_bias_detection
```

### Using pytest

```bash
# Install pytest
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest test_*.py -v

# Run with coverage
pytest test_*.py -v --cov=. --cov-report=html
pytest test_*.py -v --cov=. --cov-report=term-missing

# Run specific test file
pytest test_resume_parser.py -v
pytest test_embeddings.py -v
pytest test_scoring.py -v

# Run by marker
pytest -m unit -v                    # Unit tests only
pytest -m integration -v              # Integration tests only
pytest -m "not slow" -v              # Skip slow tests
pytest -m requires_api -v            # Tests needing API keys

# Parallel execution
pip install pytest-xdist
pytest test_*.py -n auto             # Use all CPU cores
pytest test_*.py -n 4                # Use 4 workers
```

### Using unittest

```bash
# Discover and run all tests
python -m unittest discover -s . -p "test_*.py" -v

# Run specific module
python -m unittest test_resume_parser -v
python -m unittest test_embeddings -v
python -m unittest test_scoring -v

# Run specific test class
python -m unittest test_resume_parser.TestResumeParser -v

# Run specific test method
python -m unittest test_resume_parser.TestResumeParser.test_extract_email -v
```

### Coverage Reports

```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run -m pytest test_*.py -v
coverage report -m                   # Terminal report
coverage html                        # HTML report in htmlcov/
coverage xml                         # XML report for CI

# Alternative: pytest-cov
pytest test_*.py --cov=. --cov-report=html
open htmlcov/index.html             # View in browser
```

## 🐳 Docker Commands

### Local Development

```bash
# Build image
docker build -t resume-analyzer:local .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY="your-key" \
  -e SUPABASE_URL="your-url" \
  -e SUPABASE_KEY="your-key" \
  resume-analyzer:local

# Test imports
docker run --rm resume-analyzer:local \
  python -c "import resume_parser; import scoring; import embeddings; print('OK')"

# Interactive shell
docker run -it --rm resume-analyzer:local /bin/bash
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f app          # Specific service

# Stop services
docker-compose down

# Rebuild
docker-compose build --no-cache
docker-compose up -d --build

# Execute commands in container
docker-compose exec app python run_tests.py
docker-compose exec app /bin/bash
```

## 🔄 GitHub Actions

### Trigger Workflows

```bash
# Install GitHub CLI
brew install gh                      # macOS
# or download from https://cli.github.com/

# Login
gh auth login

# Trigger workflow manually
gh workflow run "CI/CD Pipeline"
gh workflow run "CI/CD Pipeline" --ref develop

# View workflow runs
gh run list
gh run list --workflow="CI/CD Pipeline"

# View specific run
gh run view <run-id>
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id> --failed
gh run rerun <run-id>               # Re-run all jobs

# Download artifacts
gh run download <run-id>

# Watch run in real-time
gh run watch
```

### Check Status

```bash
# View latest run status
gh run list --limit 1

# Check specific workflow
gh workflow view "CI/CD Pipeline"

# Enable/disable workflow
gh workflow enable "CI/CD Pipeline"
gh workflow disable "CI/CD Pipeline"
```

## ⚙️ Environment Setup

### Local Development

```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ...
PINECONE_API_KEY=your-key
EOF

# Load environment variables
export $(cat .env | xargs)

# Verify
echo $OPENAI_API_KEY
```

### GitHub Secrets

```bash
# Using GitHub CLI
gh secret set OPENAI_API_KEY
gh secret set SUPABASE_URL
gh secret set SUPABASE_KEY
gh secret set DOCKER_USERNAME
gh secret set DOCKER_PASSWORD

# List secrets
gh secret list

# Delete secret
gh secret delete OPENAI_API_KEY
```

## 🔍 Debugging

### Test Debugging

```bash
# Run tests with print statements
pytest test_scoring.py -v -s

# Stop on first failure
pytest test_*.py -x

# Show locals on failure
pytest test_*.py -l

# Enter debugger on failure
pytest test_*.py --pdb

# Specific test with debugging
pytest test_scoring.py::TestScoring::test_skill_match_score -v -s
```

### Docker Debugging

```bash
# Build with no cache
docker build --no-cache -t resume-analyzer:debug .

# Run with verbose output
docker run --rm resume-analyzer:debug python -v

# Check container logs
docker logs <container-id>
docker logs -f <container-id>

# Inspect container
docker inspect <container-id>

# Execute command in running container
docker exec -it <container-id> /bin/bash
docker exec -it <container-id> python run_tests.py
```

### CI/CD Debugging

```bash
# View workflow file
cat .github/workflows/ci-cd.yml

# Validate workflow syntax
gh workflow view "CI/CD Pipeline"

# Download logs
gh run download <run-id>

# Test workflow locally with act
brew install act                     # Install act
act -j test                         # Run test job
act -j docker-build                 # Run docker-build job
act -l                              # List available jobs
```

## 📊 Code Quality

### Linting

```bash
# Install linting tools
pip install black isort flake8 pylint mypy

# Format code
black . --exclude="venv|env|.git|__pycache__"
black app.py resume_parser.py scoring.py

# Sort imports
isort . --skip venv --skip env
isort app.py resume_parser.py scoring.py

# Check with flake8
flake8 . --exclude=venv,env,.git,__pycache__ --max-line-length=127
flake8 app.py --max-line-length=127

# Lint with pylint
pylint **/*.py --disable=all --enable=E,F --ignore=venv,env
pylint app.py scoring.py resume_parser.py

# Type checking with mypy
mypy app.py --ignore-missing-imports
mypy . --exclude=venv --ignore-missing-imports
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
EOF

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🔐 Security

### Dependency Scanning

```bash
# Install safety
pip install safety

# Check for vulnerabilities
safety check
safety check --json > security-report.json

# Update dependencies
pip list --outdated
pip install --upgrade <package>
```

### Container Scanning

```bash
# Install trivy
brew install aquasecurity/trivy/trivy  # macOS
# or download from https://github.com/aquasecurity/trivy

# Scan image
trivy image resume-analyzer:latest
trivy image --severity HIGH,CRITICAL resume-analyzer:latest

# Scan filesystem
trivy fs .
trivy fs --severity HIGH,CRITICAL .

# Generate report
trivy image resume-analyzer:latest --format json --output trivy-report.json
```

## 📦 Dependency Management

### Update Dependencies

```bash
# Show outdated packages
pip list --outdated

# Update specific package
pip install --upgrade streamlit
pip install --upgrade openai

# Update all packages (careful!)
pip freeze | grep -v "^-e" | cut -d = -f 1 | xargs pip install -U

# Generate new requirements.txt
pip freeze > requirements.txt
```

### Dependency Tree

```bash
# Install pipdeptree
pip install pipdeptree

# Show dependency tree
pipdeptree
pipdeptree -p streamlit            # Specific package
pipdeptree --json > deps.json      # JSON output
```

## 🚀 Deployment

### Manual Deploy

```bash
# Push to staging
git push origin develop

# Push to production
git push origin main

# Create release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Deploy with Docker
docker build -t resume-analyzer:v1.0.0 .
docker push your-registry/resume-analyzer:v1.0.0
```

### Kubernetes (if applicable)

```bash
# Apply configurations
kubectl apply -f k8s/

# Check deployment
kubectl get deployments
kubectl get pods
kubectl describe pod <pod-name>

# View logs
kubectl logs -f deployment/resume-analyzer
kubectl logs -f <pod-name>

# Rollback
kubectl rollout undo deployment/resume-analyzer
kubectl rollout status deployment/resume-analyzer
```

## 📈 Monitoring

### GitHub Actions Metrics

```bash
# View workflow runs
gh run list --workflow="CI/CD Pipeline" --limit 20

# Get run statistics
gh run view <run-id> --json conclusion,status,createdAt,updatedAt

# List failed runs
gh run list --workflow="CI/CD Pipeline" --status failure
```

### Container Metrics

```bash
# View container stats
docker stats
docker stats <container-id>

# Check container health
docker inspect <container-id> --format='{{.State.Health.Status}}'

# View resource usage
docker system df
docker system df -v
```

## 🆘 Common Issues

### Test Failures

```bash
# Clear pytest cache
rm -rf .pytest_cache __pycache__

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python --version
python -c "import sys; print(sys.version)"

# Verify imports
python -c "import resume_parser; import scoring; import embeddings"
```

### Docker Build Failures

```bash
# Remove all containers and images
docker system prune -a

# Build with verbose output
docker build --progress=plain -t resume-analyzer:debug .

# Check disk space
docker system df
df -h
```

### CI/CD Failures

```bash
# Re-run failed jobs
gh run rerun <run-id> --failed

# Check workflow syntax
yamllint .github/workflows/ci-cd.yml

# Test locally
act -j test -s OPENAI_API_KEY="your-key"
```

## 📚 Documentation

### Generate Documentation

```bash
# Install sphinx
pip install sphinx sphinx-rtd-theme

# Initialize
sphinx-quickstart docs

# Build documentation
cd docs
make html
open _build/html/index.html
```

### Update README

```bash
# Generate table of contents
pip install mdtoc
mdtoc -o 2 README.md

# Check markdown
pip install markdownlint-cli
markdownlint README.md
```

---

**Quick Links:**
- [Full CI/CD Guide](CI_CD_GUIDE.md)
- [Bias Detection Guide](BIAS_DETECTION_GUIDE.md)
- [Streamlit UI Guide](STREAMLIT_UI_GUIDE.md)
- [Main README](README.md)
