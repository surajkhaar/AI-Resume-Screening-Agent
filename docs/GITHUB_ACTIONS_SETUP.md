# GitHub Actions Setup Checklist

Complete this checklist to fully configure CI/CD for the Resume Analyzer project.

## ✅ Repository Setup

### 1. Enable GitHub Actions

- [ ] Go to **Settings** → **Actions** → **General**
- [ ] Select "Allow all actions and reusable workflows"
- [ ] Under "Workflow permissions":
  - [ ] Select "Read and write permissions"
  - [ ] Check "Allow GitHub Actions to create and approve pull requests"
- [ ] Click **Save**

### 2. Configure Branch Protection (Optional but Recommended)

- [ ] Go to **Settings** → **Branches**
- [ ] Click **Add branch protection rule**
- [ ] Branch name pattern: `main`
- [ ] Enable the following:
  - [ ] Require status checks to pass before merging
  - [ ] Require branches to be up to date before merging
  - [ ] Status checks: Select `test`, `lint`, `docker-build`
  - [ ] Require pull request reviews (recommended: 1 reviewer)
  - [ ] Require conversation resolution before merging
- [ ] Click **Create** / **Save changes**

## 🔐 GitHub Secrets Setup

### Required Secrets

Add these secrets in **Settings** → **Secrets and variables** → **Actions**:

- [ ] **OPENAI_API_KEY**
  - Description: OpenAI API key for GPT-4
  - Value: `sk-proj-...`
  - Get from: https://platform.openai.com/api-keys

- [ ] **SUPABASE_URL**
  - Description: Supabase project URL
  - Value: `https://your-project-id.supabase.co`
  - Get from: Supabase project settings

- [ ] **SUPABASE_KEY**
  - Description: Supabase anon or service role key
  - Value: `eyJhbGc...`
  - Get from: Supabase project settings → API

### Optional Secrets (for Docker Hub push)

- [ ] **DOCKER_USERNAME**
  - Description: Docker Hub username
  - Value: Your Docker Hub username
  - Get from: https://hub.docker.com/settings/general

- [ ] **DOCKER_PASSWORD**
  - Description: Docker Hub access token (NOT your password!)
  - Value: Create at https://hub.docker.com/settings/security
  - Steps:
    1. Go to Docker Hub → Account Settings → Security
    2. Click **New Access Token**
    3. Name: `github-actions-resume-analyzer`
    4. Permissions: Read, Write, Delete
    5. Click **Generate**
    6. Copy the token immediately (shown only once!)

### Optional Secrets (for vector DB)

- [ ] **PINECONE_API_KEY** (if using Pinecone)
  - Description: Pinecone API key
  - Value: Your Pinecone API key
  - Get from: https://app.pinecone.io/

### Optional Secrets (for coverage)

- [ ] **CODECOV_TOKEN** (if using private repo)
  - Description: Codecov upload token
  - Value: From Codecov dashboard
  - Get from:
    1. Go to https://codecov.io/
    2. Sign in with GitHub
    3. Add your repository
    4. Copy the upload token

## 🚀 First Pipeline Run

### Pre-Push Checklist

Before pushing to trigger the pipeline:

- [ ] All files created:
  - [ ] `.github/workflows/ci-cd.yml`
  - [ ] `run_tests.py`
  - [ ] `pytest.ini`
  - [ ] `CI_CD_GUIDE.md`
  - [ ] `TESTING_QUICK_REFERENCE.md`
  - [ ] `TESTING_CI_CD_SUMMARY.md`
  - [ ] `GITHUB_ACTIONS_SETUP.md` (this file)

- [ ] Test locally first:
  ```bash
  python run_tests.py -v
  ```

- [ ] Format code:
  ```bash
  pip install black isort
  black . --exclude="venv|env"
  isort . --skip venv --skip env
  ```

- [ ] Test Docker build:
  ```bash
  docker build -t resume-analyzer:test .
  ```

### Push and Monitor

- [ ] Commit all changes:
  ```bash
  git add .
  git commit -m "Add CI/CD pipeline with comprehensive testing"
  git push origin main
  ```

- [ ] Go to **Actions** tab in GitHub
- [ ] Watch "CI/CD Pipeline" workflow execution
- [ ] Verify all jobs complete successfully:
  - [ ] Test (Python 3.10, 3.11, 3.12)
  - [ ] Lint
  - [ ] Docker Build
  - [ ] Security Scan
  - [ ] Notify

## 📊 Post-Setup Verification

### Verify Pipeline Status

- [ ] Check **Actions** tab shows green checkmark
- [ ] Review job logs for any warnings
- [ ] Verify coverage report uploaded (if Codecov configured)
- [ ] Check Docker Hub for new image (if credentials configured)

### Add Status Badges to README

Replace `YOUR-USERNAME` with your GitHub username in `README.md`:

```markdown
![CI/CD](https://github.com/YOUR-USERNAME/ai-agent/workflows/CI%2FCD%20Pipeline/badge.svg)
```

- [ ] Updated badge URL with correct username
- [ ] Pushed changes to repository
- [ ] Badge shows "passing" status

### Test Pull Request Workflow

- [ ] Create test branch:
  ```bash
  git checkout -b test-ci-cd
  ```

- [ ] Make small change (e.g., add comment to README)
- [ ] Commit and push:
  ```bash
  git add .
  git commit -m "Test CI/CD on PR"
  git push origin test-ci-cd
  ```

- [ ] Create Pull Request on GitHub
- [ ] Verify CI/CD runs on PR
- [ ] Check status checks appear on PR
- [ ] Merge or close PR

## 🔧 Optional Enhancements

### Codecov Integration

- [ ] Sign up at https://codecov.io/
- [ ] Install Codecov GitHub App
- [ ] Add `CODECOV_TOKEN` secret
- [ ] Add badge to README:
  ```markdown
  [![codecov](https://codecov.io/gh/YOUR-USERNAME/ai-agent/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR-USERNAME/ai-agent)
  ```

### Dependabot (Dependency Updates)

- [ ] Create `.github/dependabot.yml`:
  ```yaml
  version: 2
  updates:
    - package-ecosystem: "pip"
      directory: "/"
      schedule:
        interval: "weekly"
      open-pull-requests-limit: 5
    - package-ecosystem: "docker"
      directory: "/"
      schedule:
        interval: "weekly"
    - package-ecosystem: "github-actions"
      directory: "/"
      schedule:
        interval: "weekly"
  ```
- [ ] Commit and push
- [ ] Verify Dependabot creates PRs for updates

### Pre-commit Hooks

- [ ] Install pre-commit:
  ```bash
  pip install pre-commit
  ```

- [ ] Create `.pre-commit-config.yaml`:
  ```yaml
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
          args: [--max-line-length=127]
  ```

- [ ] Install hooks:
  ```bash
  pre-commit install
  ```

- [ ] Test:
  ```bash
  pre-commit run --all-files
  ```

### GitHub Actions CLI

- [ ] Install GitHub CLI:
  ```bash
  # macOS
  brew install gh
  
  # Or download from https://cli.github.com/
  ```

- [ ] Authenticate:
  ```bash
  gh auth login
  ```

- [ ] Test commands:
  ```bash
  gh run list
  gh workflow view "CI/CD Pipeline"
  ```

### Notifications

#### Slack Notifications

- [ ] Create Slack incoming webhook
- [ ] Add `SLACK_WEBHOOK` secret
- [ ] Update `notify` job in workflow:
  ```yaml
  - name: Send Slack notification
    uses: 8398a7/action-slack@v3
    with:
      status: ${{ job.status }}
      text: 'Pipeline ${{ job.status }}'
      webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  ```

#### Email Notifications

- [ ] Go to **Settings** → **Notifications**
- [ ] Configure email preferences:
  - [ ] Actions: "Send notifications for failed workflows only"
  - [ ] Include workflow names

## 🐛 Troubleshooting

### If Pipeline Fails

1. **Check the logs:**
   - [ ] Go to Actions tab
   - [ ] Click on failed run
   - [ ] Expand failed job
   - [ ] Read error message

2. **Common fixes:**
   - [ ] Missing secret → Add in Settings
   - [ ] Test failure → Fix code and push
   - [ ] Lint error → Run `black .` and `isort .`
   - [ ] Docker build error → Test locally with `docker build`

3. **Re-run pipeline:**
   - [ ] Click **Re-run jobs** → **Re-run failed jobs**
   - OR push new commit with fix

### If Tests Pass Locally But Fail in CI

- [ ] Check Python version matches (3.10, 3.11, or 3.12)
- [ ] Verify all dependencies in `requirements.txt`
- [ ] Check for missing environment variables
- [ ] Look for file path issues (absolute vs relative)
- [ ] Verify mock objects are correctly configured

### If Docker Build Fails

- [ ] Test locally: `docker build -t test .`
- [ ] Check Dockerfile syntax
- [ ] Verify all files copied exist
- [ ] Check requirements.txt is valid
- [ ] Look for permission issues

### If Coverage Upload Fails

- [ ] Add `CODECOV_TOKEN` secret
- [ ] OR set `fail_ci_if_error: false` in workflow
- [ ] Check Codecov service status
- [ ] Verify coverage.xml is generated

## 📚 Documentation Review

### Files to Review

- [ ] Read [CI_CD_GUIDE.md](CI_CD_GUIDE.md) - Comprehensive guide
- [ ] Review [TESTING_QUICK_REFERENCE.md](TESTING_QUICK_REFERENCE.md) - Command reference
- [ ] Check [TESTING_CI_CD_SUMMARY.md](TESTING_CI_CD_SUMMARY.md) - Implementation summary
- [ ] Update [README.md](README.md) - Main documentation

### Update Documentation

- [ ] Replace `YOUR-USERNAME` with actual GitHub username
- [ ] Update badge URLs
- [ ] Add any project-specific notes
- [ ] Document custom deployment steps (if any)

## ✨ Success Criteria

Your CI/CD is fully set up when:

- ✅ Pipeline runs automatically on push/PR
- ✅ All tests pass (90+ tests)
- ✅ Code coverage tracked and reported
- ✅ Docker image builds successfully
- ✅ Security scans complete
- ✅ Status badges show "passing"
- ✅ All secrets configured
- ✅ Branch protection enabled (optional)
- ✅ Documentation complete and accurate

## 🎉 Next Steps After Setup

1. **Monitor Pipeline**
   - Watch first few runs
   - Fix any issues that arise
   - Optimize for speed if needed

2. **Train Team**
   - Share documentation with team
   - Explain CI/CD workflow
   - Set expectations for PR process

3. **Iterate**
   - Add more tests as project grows
   - Enhance deployment automation
   - Improve coverage over time

4. **Maintain**
   - Update dependencies regularly
   - Review and rotate secrets quarterly
   - Keep documentation current

## 📞 Support

If you encounter issues:

1. **Check documentation**: All guides in repository
2. **Review logs**: GitHub Actions provides detailed logs
3. **Test locally**: Reproduce issues on your machine
4. **Search issues**: Check if others had similar problems
5. **Ask for help**: Open issue with:
   - Pipeline run URL
   - Error logs
   - Steps to reproduce

---

**Congratulations on setting up CI/CD! 🎊**

Your Resume Analyzer now has enterprise-grade automated testing and deployment.

**Pipeline Health Check**: https://github.com/YOUR-USERNAME/ai-agent/actions

Remember to replace `YOUR-USERNAME` with your actual GitHub username!
