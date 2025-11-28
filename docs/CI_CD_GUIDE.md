# CI/CD Pipeline Guide

This guide explains the automated CI/CD pipeline for the Resume Analyzer project, including test automation, code quality checks, Docker builds, and deployment workflows.

## Table of Contents
- [Overview](#overview)
- [Pipeline Jobs](#pipeline-jobs)
- [Setup Instructions](#setup-instructions)
- [GitHub Secrets](#github-secrets)
- [Running Tests Locally](#running-tests-locally)
- [Docker Build Process](#docker-build-process)
- [Deployment Workflow](#deployment-workflow)
- [Troubleshooting](#troubleshooting)

---

## Overview

The CI/CD pipeline is triggered on:
- **Push** to `main` or `develop` branches
- **Pull requests** to `main` or `develop` branches
- **Manual workflow dispatch** from GitHub Actions UI

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Trigger Event                      │
│         (Push/PR to main/develop)                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────┐
    │         Parallel Jobs Start          │
    └─────────────────────────────────────┘
              │
    ┌─────────┼──────────┬──────────┐
    │         │          │          │
    ▼         ▼          ▼          ▼
┌─────┐  ┌──────┐  ┌──────────┐  ┌────────┐
│Test │  │ Lint │  │ Security │  │        │
│ Job │  │ Job  │  │   Scan   │  │        │
└──┬──┘  └──────┘  └──────────┘  │        │
   │                               │        │
   ▼                               │        │
┌─────────────┐                   │        │
│Docker Build │◄──────────────────┘        │
└──────┬──────┘                            │
       │                                   │
       ▼                                   ▼
┌──────────────┐                  ┌────────────────┐
│Integration   │                  │     Notify     │
│    Tests     │                  │                │
└──────┬───────┘                  └────────────────┘
       │
       ▼
┌──────────────┐
│   Deploy     │
│ (Staging/    │
│  Production) │
└──────────────┘
```

---

## Pipeline Jobs

### 1. **Test Job**

Runs comprehensive unit tests across multiple Python versions.

**Matrix Strategy:**
- Python 3.10, 3.11, 3.12

**Steps:**
1. Checkout code
2. Set up Python environment
3. Cache pip dependencies
4. Install dependencies from `requirements.txt`
5. Install test frameworks (pytest, pytest-cov, pytest-mock)
6. Run linting with flake8
7. Execute unit tests with `run_tests.py`
8. Generate coverage report (Python 3.11 only)
9. Upload coverage to Codecov

**Environment Variables:**
```yaml
OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
```

### 2. **Lint Job**

Ensures code quality and consistency.

**Tools:**
- **black**: Code formatting (PEP 8)
- **isort**: Import sorting
- **pylint**: Static code analysis

**Checks:**
- Code formatting compliance
- Import order consistency
- Common errors and code smells

### 3. **Docker Build Job**

Builds and tests Docker image.

**Steps:**
1. Set up Docker Buildx
2. Log in to Docker Hub (if credentials available)
3. Extract metadata (tags, labels)
4. Build test image
5. Test import functionality
6. Push to Docker Hub (main branch only)

**Image Tags:**
- Branch name (e.g., `main`, `develop`)
- PR number (e.g., `pr-123`)
- Git SHA (e.g., `sha-abc1234`)
- Semantic version (if tagged)

### 4. **Security Scan Job**

Performs security vulnerability scanning.

**Tools:**
- **Trivy**: Filesystem and dependency scanning
- **Safety**: Python dependency vulnerability checks

**Outputs:**
- SARIF report uploaded to GitHub Security tab
- JSON report of known vulnerabilities

### 5. **Integration Test Job**

Runs integration tests with real API connections (main branch only).

**Requirements:**
- Valid API credentials in GitHub Secrets
- Runs after unit tests pass

**Test Markers:**
```bash
pytest test_*.py -v -m "integration or not slow"
```

### 6. **Deploy Jobs**

Automated deployment to staging and production.

**Staging Deploy:**
- Triggered on push to `develop` branch
- Deploys to staging environment

**Production Deploy:**
- Triggered on push to `main` branch
- Requires all tests to pass
- Creates GitHub release with version tag

### 7. **Notify Job**

Sends pipeline status notifications.

**Always runs**, even if previous jobs fail.

**Outputs:**
- Test job status
- Docker build status
- Overall pipeline result

---

## Setup Instructions

### 1. Enable GitHub Actions

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Actions** → **General**
3. Under "Actions permissions", select:
   - ✅ Allow all actions and reusable workflows
4. Under "Workflow permissions", select:
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests

### 2. Configure Branch Protection

1. Go to **Settings** → **Branches**
2. Add branch protection rule for `main`:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select required checks: `test`, `lint`, `docker-build`
   - ✅ Require pull request reviews before merging

### 3. Set Up GitHub Secrets

Navigate to **Settings** → **Secrets and variables** → **Actions** and add:

```yaml
# Required Secrets
OPENAI_API_KEY: sk-...
SUPABASE_URL: https://your-project.supabase.co
SUPABASE_KEY: eyJ...

# Optional Secrets (for Docker Hub push)
DOCKER_USERNAME: your-docker-username
DOCKER_PASSWORD: your-docker-password

# Optional Secrets (for Pinecone)
PINECONE_API_KEY: your-pinecone-key
```

---

## GitHub Secrets

### Required Secrets

| Secret Name | Description | Example |
|------------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | `sk-proj-abc123...` |
| `SUPABASE_URL` | Supabase project URL | `https://xyz.supabase.co` |
| `SUPABASE_KEY` | Supabase anon/service key | `eyJhbGc...` |

### Optional Secrets

| Secret Name | Description | Required For |
|------------|-------------|--------------|
| `DOCKER_USERNAME` | Docker Hub username | Docker image push |
| `DOCKER_PASSWORD` | Docker Hub password/token | Docker image push |
| `PINECONE_API_KEY` | Pinecone API key | Vector DB integration |
| `CODECOV_TOKEN` | Codecov upload token | Coverage reporting |

### How to Create Secrets

1. Go to repository **Settings**
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter name and value
5. Click **Add secret**

---

## Running Tests Locally

### Option 1: Using Test Runner Script

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py -v

# Run specific test module
python run_tests.py test_resume_parser

# Run quietly (minimal output)
python run_tests.py -q
```

### Option 2: Using pytest

```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest test_*.py -v

# Run with coverage
pytest test_*.py -v --cov=. --cov-report=html

# Run specific markers
pytest -m "unit" -v
pytest -m "integration" -v
pytest -m "not slow" -v

# Run specific test file
pytest test_scoring.py -v
```

### Option 3: Using unittest

```bash
# Run all tests
python -m unittest discover -s . -p "test_*.py" -v

# Run specific test module
python -m unittest test_resume_parser -v

# Run specific test class
python -m unittest test_resume_parser.TestResumeParser -v

# Run specific test method
python -m unittest test_resume_parser.TestResumeParser.test_extract_email -v
```

### Test Markers

Configure test execution with pytest markers:

```python
# Mark as unit test
@pytest.mark.unit
def test_something():
    pass

# Mark as integration test
@pytest.mark.integration
def test_integration():
    pass

# Mark as slow test (skipped by default)
@pytest.mark.slow
def test_slow_operation():
    pass

# Mark as requiring API
@pytest.mark.requires_api
def test_api_call():
    pass
```

---

## Docker Build Process

### Local Docker Build

```bash
# Build image
docker build -t resume-analyzer:local .

# Test image
docker run --rm resume-analyzer:local python -c "import resume_parser; print('OK')"

# Run Streamlit app
docker run -p 8501:8501 \
  -e OPENAI_API_KEY="your-key" \
  -e SUPABASE_URL="your-url" \
  -e SUPABASE_KEY="your-key" \
  resume-analyzer:local
```

### Docker Compose (Multi-Container)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache
```

### CI/CD Docker Build

The pipeline automatically:
1. Builds Docker image with cache optimization
2. Tests imports within container
3. Tags with multiple naming schemes
4. Pushes to Docker Hub (main branch only)

**Cache Strategy:**
- Uses GitHub Actions cache for layer reuse
- Reduces build time by ~70%
- Automatically invalidated on Dockerfile changes

---

## Deployment Workflow

### Staging Deployment

**Trigger:** Push to `develop` branch

**Process:**
1. Tests pass ✓
2. Docker image builds ✓
3. Integration tests pass ✓
4. Deploy to staging environment

**Commands:**
```bash
# Example Kubernetes deployment
kubectl apply -f k8s/staging/ --namespace=staging
kubectl rollout status deployment/resume-analyzer -n staging
```

### Production Deployment

**Trigger:** Push to `main` branch

**Process:**
1. All tests pass ✓
2. Security scans complete ✓
3. Integration tests pass ✓
4. Docker image published ✓
5. Deploy to production
6. Create GitHub release

**Commands:**
```bash
# Example production deployment
kubectl apply -f k8s/production/ --namespace=production
kubectl rollout status deployment/resume-analyzer -n production

# Verify deployment
kubectl get pods -n production
kubectl logs -f deployment/resume-analyzer -n production
```

### Manual Deployment

Trigger workflow manually from GitHub UI:

1. Go to **Actions** tab
2. Select **CI/CD Pipeline**
3. Click **Run workflow**
4. Select branch
5. Click **Run workflow**

---

## Troubleshooting

### Common Issues

#### 1. **Tests Failing Due to Missing API Keys**

**Symptom:** Tests fail with authentication errors

**Solution:**
- Add API keys to GitHub Secrets
- For local testing, create `.env` file:
  ```bash
  OPENAI_API_KEY=sk-...
  SUPABASE_URL=https://...
  SUPABASE_KEY=eyJ...
  ```
- Load environment variables:
  ```bash
  export $(cat .env | xargs)
  python run_tests.py
  ```

#### 2. **Docker Build Fails**

**Symptom:** Docker build job fails with errors

**Solution:**
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Test locally:
  ```bash
  docker build --no-cache -t test .
  ```
- Review build logs in GitHub Actions

#### 3. **Coverage Upload Fails**

**Symptom:** Codecov upload times out or fails

**Solution:**
- Add `CODECOV_TOKEN` secret
- Or set `fail_ci_if_error: false` in workflow
- Coverage upload is optional and won't block CI

#### 4. **Linting Errors Block CI**

**Symptom:** Black or isort checks fail

**Solution:**
- Run formatters locally:
  ```bash
  pip install black isort
  black . --exclude="venv|env"
  isort . --skip venv --skip env
  ```
- Commit formatting changes
- Or set `continue-on-error: true` for lint job

#### 5. **Integration Tests Fail**

**Symptom:** Integration tests timeout or error

**Solution:**
- Ensure API keys are valid
- Check API rate limits
- Integration tests only run on main branch
- Use `continue-on-error: true` if tests are flaky

### Debugging Pipeline

#### View Workflow Logs

1. Go to **Actions** tab
2. Click on workflow run
3. Click on specific job
4. Expand steps to view logs

#### Re-run Failed Jobs

1. Open failed workflow run
2. Click **Re-run jobs** dropdown
3. Select:
   - **Re-run failed jobs**: Only failed jobs
   - **Re-run all jobs**: All jobs from scratch

#### Download Artifacts

```bash
# Download coverage reports, logs, etc.
gh run download <run-id>
```

#### Test Workflow Locally

Use `act` to test workflows locally:

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow
act -j test  # Run test job
act -j docker-build  # Run docker build job
act  # Run entire workflow
```

### Performance Optimization

#### Speed Up Tests

1. **Use pytest-xdist for parallel execution:**
   ```bash
   pip install pytest-xdist
   pytest test_*.py -n auto  # Auto-detect CPU cores
   ```

2. **Skip slow tests:**
   ```bash
   pytest test_*.py -m "not slow"
   ```

3. **Cache dependencies:**
   - Already configured in workflow with `actions/cache@v3`

#### Reduce Build Time

1. **Multi-stage Docker builds:**
   - Separate build and runtime dependencies
   - Reduce final image size

2. **Use cache mounts:**
   ```dockerfile
   RUN --mount=type=cache,target=/root/.cache/pip \
       pip install -r requirements.txt
   ```

3. **GitHub Actions cache:**
   - Already configured for pip and Docker layers

---

## Monitoring and Alerts

### GitHub Actions Status Badge

Add to README.md:

```markdown
![CI/CD](https://github.com/your-username/resume-analyzer/workflows/CI%2FCD%20Pipeline/badge.svg)
```

### Codecov Badge

```markdown
[![codecov](https://codecov.io/gh/your-username/resume-analyzer/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/resume-analyzer)
```

### Set Up Notifications

Configure GitHub notification settings:

1. Go to **Settings** → **Notifications**
2. Under "Actions":
   - ✅ Only failed workflows
   - ✅ Email notifications
   - ✅ GitHub notification bell

### Custom Notifications

Extend `notify` job with:

```yaml
- name: Send Slack notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'CI/CD pipeline completed'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Best Practices

### 1. **Keep Tests Fast**
- Mock external API calls
- Use fixtures for test data
- Parallelize test execution

### 2. **Maintain High Coverage**
- Aim for >80% code coverage
- Focus on critical paths
- Test edge cases and error handling

### 3. **Security First**
- Never commit secrets to repository
- Rotate API keys regularly
- Use least-privilege access for service accounts

### 4. **Optimize Build Times**
- Cache dependencies aggressively
- Use Docker layer caching
- Skip redundant jobs on documentation-only changes

### 5. **Version Control**
- Tag releases with semantic versioning
- Maintain CHANGELOG.md
- Use conventional commit messages

### 6. **Documentation**
- Document CI/CD changes in this guide
- Add inline comments to workflow YAML
- Keep README badges up to date

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Codecov Documentation](https://docs.codecov.com/)
- [Trivy Security Scanner](https://github.com/aquasecurity/trivy)

---

## Support

For CI/CD pipeline issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review workflow logs in GitHub Actions
3. Test locally before pushing
4. Open issue with pipeline logs attached

**Happy shipping! 🚀**
