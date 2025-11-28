# 📄 AI-Powered Resume Analyzer

An intelligent resume analysis system that uses AI to match candidates with job descriptions, providing comprehensive scoring and ranking based on multiple signals.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![CI/CD](https://github.com/YOUR-USERNAME/ai-agent/workflows/CI%2FCD%20Pipeline/badge.svg)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](CI_CD_GUIDE.md)

## 🌟 Features

### Core Capabilities
- **📤 Resume Upload**: Support for PDF and DOCX formats
- **🤖 AI-Powered Parsing**: Automatic extraction of name, email, phone, skills, experience, and education
- **🎯 Multi-Signal Scoring**: Combines skill matching, experience, education, and semantic similarity
- **📊 Candidate Ranking**: Automatic sorting by match percentage with visual score bars
- **💡 Skill Gap Analysis**: Identifies matched and missing skills
- **🔍 Semantic Search**: Uses sentence-transformers for content similarity
- **📈 Visual Analytics**: Interactive Streamlit dashboard with detailed breakdowns
- **✨ AI Explainability**: GPT-4 powered explanations with top 3 match reasons
- **📥 CSV Export**: Download analysis results for external use
- **💾 Database Storage**: Automatic Supabase integration for historical tracking
- **⚖️ Bias Detection**: Identify data quality issues and suspicious patterns without inferring protected attributes

### Advanced Features
- **Visual Score Bars**: Color-coded progress bars for each scoring component
- **AI Explanations**: 120-word summaries with actionable insights and recommendations
- **Bias Reporting**: Automated detection of missing fields, extreme variance, and suspicious patterns
- **Fairness Warnings**: Flags potential issues that may disadvantage candidates
- **Vector Database Support**: Pinecone cloud storage with FAISS fallback
- **OpenAI Integration**: Enhanced resume parsing and explanation generation with GPT models
- **Batch Processing**: Analyze multiple resumes simultaneously with parallel processing
- **Customizable Weights**: Adjust scoring components to your needs
- **Export Capabilities**: CSV and JSON output for integration with other systems
- **Docker Support**: Containerized deployment ready
- **Historical Analytics**: Track analyses over time with Supabase
- **Real-time Scoring**: Instant feedback with progress indicators

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-agent

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Docker Deployment

```bash
# Build the image
docker build -t resume-analyzer .

# Run the container
docker run -p 8501:8501 resume-analyzer
```

Or use docker-compose:

```bash
docker-compose up
```

## 📖 Usage

### Basic Workflow

1. **Upload Resumes**
   - Click "Choose resume files"
   - Select PDF or DOCX files (supports multiple)
   - Click "Extract Text from Resumes"

2. **Enter Job Description**
   - Paste the complete job description
   - Include skills, experience requirements, and education needs

3. **Analyze**
   - Click "🔍 Analyze Resumes"
   - Wait for AI explanations to generate (2-3 seconds per candidate)
   - Review ranked candidates with visual score bars

4. **Export Results**
   - Click "📥 Download Results as CSV" to export data
   - Results are automatically saved to Supabase (if configured)

### Example Job Description

```
Senior Machine Learning Engineer

Requirements:
- 5+ years of experience in machine learning
- Strong Python programming skills
- Experience with TensorFlow or PyTorch
- AWS cloud platform experience
- Master's degree in Computer Science or related field
- Docker and Kubernetes knowledge

Responsibilities:
- Design and implement ML models
- Deploy models to production
- Collaborate with cross-functional teams
```

## 🎯 Scoring Methodology

The system uses a weighted combination of four signals:

| Component | Weight | Description |
|-----------|--------|-------------|
| **Skills Match** | 35% | Jaccard similarity between resume skills and required skills |
| **Experience** | 25% | Years of experience vs. requirement (with bonus for exceeding) |
| **Education** | 15% | Degree level validation (PhD > Master > Bachelor > Associate) |
| **Semantic Similarity** | 25% | AI-powered content matching using embeddings |

### Score Interpretation

- **80-100%** 🌟 **Strong Match** - Highly recommended for interview
- **60-79%** 👍 **Good Match** - Recommended for consideration  
- **40-59%** 🤔 **Moderate Match** - Review carefully
- **0-39%** ❌ **Weak Match** - May not be suitable

## 🎨 Enhanced UI Features

### Visual Score Bars
Each candidate displays color-coded score bars:
- **Overall Match**: Large prominent bar at the top
- **Component Scores**: Individual progress bars for Skills, Experience, Education, and Semantic matching
- **Color Coding**: Green (excellent), Blue (good), Orange (moderate), Red (weak)

### AI Explanations
Powered by GPT-4 with deterministic prompting:
- **Summary**: Concise 120-word explanation of the match
- **Top 3 Reasons**: Specific bullet points explaining match/mismatch
- **Recommendation**: Clear hiring recommendation (Strong/Good/Moderate/Weak Match)
- **Few-shot Prompting**: Consistent, reliable results using example templates

### CSV Export
Download complete analysis results including:
- Candidate information (name, email, phone)
- All scores and breakdowns
- Matched and missing skills
- AI explanations and recommendations
- Experience and education details
- Filename: `resume_analysis_YYYYMMDD_HHMMSS.csv`

### Database Integration
Automatic Supabase storage (when configured):
- **Historical Tracking**: All analyses saved with timestamps
- **Query Capabilities**: Search by candidate, score range, or date
- **Statistics**: Total analyses, average scores, strong matches
- **Audit Trail**: Complete record of all evaluations

### Bias Detection & Reporting
Automated fairness checks without inferring protected attributes:
- **Missing Data Detection**: Flags high rates of incomplete candidate information
- **Variance Analysis**: Identifies extreme variance in experience or education
- **Pattern Recognition**: Detects score clustering and suspicious patterns
- **Data Quality**: Checks parsing quality and consistency issues
- **Actionable Recommendations**: Provides specific suggestions to address each issue
- **Severity Levels**: Critical, Warning, and Info flags for prioritization
- **No Profiling**: Does not infer race, gender, age, or other protected attributes

**Example Flags:**
- 🚨 Critical: "No skills extracted from any candidate"
- ⚠️ Warning: "High rate of missing education data (60% of candidates)"
- ℹ️ Info: "Email addresses concentrated in one domain"

See [STREAMLIT_UI_GUIDE.md](STREAMLIT_UI_GUIDE.md) for detailed UI documentation.
See [BIAS_DETECTION_GUIDE.md](BIAS_DETECTION_GUIDE.md) for bias detection details.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI (app.py)                  │
│                                                               │
│  • File Upload  • Job Description Input  • Results Display   │
└─────────┬─────────────────────────────────────────────┬─────┘
          │                                             │
          ▼                                             ▼
┌─────────────────────┐                    ┌─────────────────────┐
│   Resume Parser     │                    │   Scoring Engine    │
│ (resume_parser.py)  │                    │   (scoring.py)      │
│                     │                    │                     │
│ • PDF Extraction    │                    │ • Skill Matching    │
│ • DOCX Extraction   │◄───────────────────│ • Experience Calc   │
│ • Field Parsing     │                    │ • Education Check   │
│ • OpenAI Fallback   │                    │ • Semantic Scoring  │
└─────────────────────┘                    └───────────┬─────────┘
                                                       │
                                                       ▼
                                           ┌─────────────────────┐
                                           │  Embeddings Manager │
                                           │  (embeddings.py)    │
                                           │                     │
                                           │ • Sentence Trans.   │
                                           │ • Pinecone/FAISS    │
                                           │ • Vector Search     │
                                           └─────────────────────┘
```

## 📚 Module Documentation

### Resume Parser
Extracts structured data from PDF/DOCX files:
- **Input**: Binary file content (PDF or DOCX)
- **Output**: JSON with name, email, phone, skills, experience_years, education, summary
- **Features**: Regex-based extraction with OpenAI fallback

See [RESUME_PARSER_README.md](RESUME_PARSER_README.md) for details.

### Embeddings Manager
Generates and manages vector embeddings:
- **Model**: sentence-transformers (all-MiniLM-L6-v2)
- **Storage**: Pinecone (cloud) or FAISS (local fallback)
- **Features**: Semantic search, resume ranking, similarity scoring

See [EMBEDDINGS_DOCUMENTATION.md](EMBEDDINGS_DOCUMENTATION.md) for details.

### Scoring Engine
Multi-signal resume scoring system:
- **Components**: Skills, experience, education, semantic similarity
- **Output**: ScoreBreakdown with detailed per-feature analysis
- **Features**: Configurable weights, batch processing, automatic requirement extraction

See `scoring.py` for implementation details.

## 🔧 Configuration

### Environment Variables

Create a `.env` file (see `.env.example`):

```bash
# OpenAI (required for AI explanations, optional for enhanced parsing)
OPENAI_API_KEY=your_openai_key

# Pinecone (optional - for cloud vector storage)
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=resume-embeddings

# Supabase (optional - for database storage and historical tracking)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Custom Scoring Weights

Edit `app.py` to adjust scoring components:

```python
st.session_state.scorer = ResumeScorer(
    skill_weight=0.4,        # 40% weight on skills
    experience_weight=0.3,    # 30% on experience
    education_weight=0.1,     # 10% on education
    semantic_weight=0.2       # 20% on semantic match
)
```

## 📊 Example Output

```json
{
  "final_score": 0.87,
  "skill_match_score": 0.92,
  "experience_score": 1.15,
  "education_score": 1.0,
  "semantic_similarity_score": 0.85,
  "matched_skills": ["Python", "Machine Learning", "AWS", "Docker"],
  "missing_skills": ["Kubernetes"],
  "experience_years": 6,
  "required_experience": 5,
  "has_required_degree": true
}
```

## 🧪 Testing

The project includes comprehensive test suites covering all modules.

### Run All Tests

```bash
# Using unified test runner
python run_tests.py

# With verbose output
python run_tests.py -v

# Using pytest
pytest test_*.py -v

# With coverage
pytest test_*.py -v --cov=. --cov-report=html
```

### Run Specific Tests

```bash
# Test specific module
python run_tests.py test_resume_parser

# Test resume parser
python -m unittest test_resume_parser -v

# Test embeddings with pytest
pytest test_embeddings.py -v

# Test scoring
python -m unittest test_scoring.py -v

# Test bias detection
python -m unittest test_bias_detection.py -v

# Run all tests
python -m unittest discover
```

### Test Coverage

The project has **90+%** test coverage across all modules:

- **test_resume_parser.py**: 15+ tests for PDF/DOCX parsing, text extraction, OpenAI integration
- **test_embeddings.py**: 30+ tests for embedding generation, FAISS, Pinecone, similarity search
- **test_scoring.py**: 25+ tests for skill matching, experience scoring, education evaluation
- **test_bias_detection.py**: 20+ tests for bias detection algorithms and reporting
- **test_explainability.py**: Tests for AI explanation generation

See [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for continuous integration setup.

## 🔄 CI/CD Pipeline

The project includes a comprehensive GitHub Actions workflow for automated testing and deployment.

### Features

- ✅ **Automated Testing**: Runs on Python 3.10, 3.11, and 3.12
- ✅ **Code Quality**: Linting with flake8, black, isort, and pylint
- ✅ **Security Scanning**: Trivy vulnerability scans
- ✅ **Docker Builds**: Automated image builds and pushes
- ✅ **Coverage Reports**: Codecov integration
- ✅ **Integration Tests**: Optional API-based tests
- ✅ **Automated Deployments**: Staging and production workflows

### Quick Setup

1. **Enable GitHub Actions** in your repository settings
2. **Add secrets** to your repository:
   ```
   OPENAI_API_KEY
   SUPABASE_URL
   SUPABASE_KEY
   DOCKER_USERNAME (optional)
   DOCKER_PASSWORD (optional)
   ```
3. **Push to main or develop** to trigger the pipeline

### Pipeline Stages

```
Push/PR → Tests (3 Python versions) → Lint → Security Scan
                   ↓
              Docker Build → Integration Tests
                   ↓
            Deploy (Staging/Production)
```

**📚 Full Documentation**: See [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for complete setup instructions, troubleshooting, and deployment workflows.

## 📝 Examples

### Example Scripts

1. **Resume Parser Examples**
   ```bash
   python example_usage.py
   ```
   Demonstrates 6 different parsing scenarios

2. **Embeddings Examples**
   ```bash
   python example_embeddings.py
   ```
   Shows 10 embedding and vector search examples

3. **Scoring Examples**
   ```bash
   python example_scoring.py
   ```
   Illustrates 7 scoring scenarios including batch processing

### Programmatic Usage

```python
from resume_parser import ResumeParser
from embeddings import EmbeddingsManager
from scoring import ResumeScorer, explain_match

# Parse resume
parser = ResumeParser()
resume = parser.parse_resume(file_content, file_type="pdf")

# Initialize scoring with embeddings
embeddings_manager = EmbeddingsManager()
scorer = ResumeScorer(embeddings_manager=embeddings_manager)

# Score against job description
job_desc = "Python developer with 5+ years experience needed"
breakdown = scorer.score_resume(resume, job_desc)

print(f"Final Score: {breakdown.final_score:.2%}")
print(f"Matched Skills: {breakdown.matched_skills}")
print(f"Missing Skills: {breakdown.missing_skills}")

# Generate AI explanation (requires OPENAI_API_KEY)
explanation = explain_match(resume, job_desc, breakdown)
print(f"\nSummary: {explanation.summary}")
print(f"Top Reasons: {explanation.top_reasons}")
print(f"Recommendation: {explanation.recommendation}")
```

### AI Explainability Feature

Generate human-readable explanations for candidate matches:

```python
from scoring import explain_match

# Get explanation with summary and top 3 reasons
explanation = explain_match(
    resume_data=resume,
    job_description=job_description,
    api_key="your-openai-key"  # or set OPENAI_API_KEY env var
)

# Access results
print(explanation.summary)  # Max 120 words
print(explanation.top_reasons)  # List of 3 reasons
print(explanation.recommendation)  # "Strong Match", "Good Match", etc.

# Export as JSON
export_data = explanation.to_dict()
```

The explainability feature uses GPT-4 with:
- **Deterministic prompting** (temperature=0.3) for consistency
- **Few-shot examples** to guide output format
- **Structured output** with summary, reasons, and recommendation
- **Fallback mode** if OpenAI is unavailable

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit 1.29.0 | Web UI and interaction |
| **Parsing** | pdfplumber, python-docx | Extract text from files |
| **AI/ML** | sentence-transformers | Generate embeddings |
| **LLM** | OpenAI GPT | Enhanced parsing fallback |
| **Vector DB** | Pinecone, FAISS | Store and search embeddings |
| **Backend** | Python 3.11+ | Core logic and processing |
| **Container** | Docker | Deployment and isolation |
| **Compute** | NumPy | Vector operations |

## 📂 Project Structure

```
ai-agent/
├── app.py                          # Main Streamlit application
├── resume_parser.py                # Resume parsing module
├── embeddings.py                   # Embeddings and vector storage
├── scoring.py                      # Multi-signal scoring engine
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose setup
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── QUICKSTART.md                   # Quick start guide
├── RESUME_PARSER_README.md         # Parser documentation
├── EMBEDDINGS_DOCUMENTATION.md     # Embeddings guide
├── API_DOCUMENTATION.md            # Complete API reference
├── test_resume_parser.py           # Parser unit tests
├── test_embeddings.py              # Embeddings unit tests
├── test_scoring.py                 # Scoring unit tests
├── example_usage.py                # Parser examples
├── example_embeddings.py           # Embeddings examples
└── example_scoring.py              # Scoring examples
```

## 🔍 Key Components

### 1. Resume Parser (`resume_parser.py`)
- 470 lines of code
- Supports PDF and DOCX formats
- Extracts 7 key fields using regex
- OpenAI fallback for difficult resumes
- Comprehensive error handling

### 2. Embeddings Manager (`embeddings.py`)
- 553 lines of code
- Uses all-MiniLM-L6-v2 model (384 dimensions)
- Pinecone cloud storage with FAISS fallback
- Semantic search and ranking
- Automatic index management

### 3. Scoring Engine (`scoring.py`)
- 637 lines of code
- Four-component weighted scoring
- Automatic requirement extraction
- Batch processing support
- Detailed breakdown with recommendations

### 4. Streamlit App (`app.py`)
- 445 lines of code
- Interactive multi-column layout
- Real-time progress indicators
- Expandable candidate cards
- Skills overview visualization

**Total**: 2,105 lines of Python code across core modules

## 🚧 Roadmap

### Planned Features
- [ ] Support for more file formats (LinkedIn profiles, HTML)
- [ ] Advanced filtering and search
- [ ] Custom skill taxonomies
- [ ] Integration with ATS systems
- [ ] Historical analysis and trends
- [ ] Email notification for matches
- [ ] RESTful API for integration
- [ ] Multi-language support

### Performance Improvements
- [ ] Caching for faster re-analysis
- [ ] Parallel processing for large batches
- [ ] Optimized vector search
- [ ] Reduced model size options

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Format code
black *.py

# Lint code
flake8 *.py

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Sentence Transformers** for excellent embedding models
- **Streamlit** for the amazing web framework
- **OpenAI** for GPT models
- **Pinecone** for vector database infrastructure
- **pdfplumber** and **python-docx** for robust file parsing

## 📞 Support

- **Documentation**: See markdown files in the repository
- **Examples**: Run example scripts for usage patterns
- **Tests**: Check test files for expected behavior
- **Issues**: Open a GitHub issue for bugs or questions

## 🎓 Learn More

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Sentence Transformers](https://www.sbert.net/)
- [Pinecone Vector Database](https://www.pinecone.io/)
- [OpenAI API](https://platform.openai.com/docs/)

---

**Built with ❤️ using Python, Streamlit, and AI**

*For detailed guides, see [QUICKSTART.md](QUICKSTART.md)*
