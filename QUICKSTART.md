# Resume Analyzer - Quick Start Guide

## 🚀 Getting Started

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables** (Optional)
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 📖 How to Use

### Step 1: Upload Resumes
- Click on "Choose resume files"
- Select one or more PDF or DOCX files
- Click "Extract Text from Resumes" to parse them

### Step 2: Enter Job Description
- Paste the complete job description in the text area
- Include:
  - Required skills (e.g., "Python", "AWS", "Docker")
  - Experience requirement (e.g., "5+ years experience")
  - Education requirement (e.g., "Master's degree required")

### Step 3: Analyze
- Click "🔍 Analyze Resumes" button
- Wait for AI-powered analysis to complete
- View ranked candidates with detailed scores

## 🎯 Understanding the Scores

### Final Score Components

| Component | Weight | Description |
|-----------|--------|-------------|
| **Skills Match** | 35% | Overlap between resume skills and job requirements |
| **Experience** | 25% | Years of experience vs. required experience |
| **Education** | 15% | Degree level vs. required degree |
| **Semantic Similarity** | 25% | AI-powered content matching |

### Score Interpretation

| Score Range | Rating | Recommendation |
|-------------|--------|----------------|
| 80-100% | 🌟 Strong Match | Highly recommended for interview |
| 60-79% | 👍 Good Match | Recommended for consideration |
| 40-59% | 🤔 Moderate Match | Review carefully |
| 0-39% | ❌ Weak Match | May not be suitable |

## 📊 Features

### 1. Ranked Candidate List
- Candidates automatically sorted by final score
- Top 3 candidates expanded by default
- Color-coded scores for quick assessment

### 2. Detailed Score Breakdown
Each candidate shows:
- **Final Score**: Overall match percentage
- **Skills Analysis**: Matched vs. missing skills
- **Experience Comparison**: Candidate years vs. required years
- **Education Validation**: Degree level check
- **Semantic Match**: AI-powered content similarity

### 3. Skills Overview
- **Skills Found**: Which skills are present in candidates
- **Skills Needed**: Which skills are universally missing
- **Candidate Coverage**: How many candidates have each skill

### 4. Summary Statistics
- Total candidates analyzed
- Average score across all candidates
- Number of strong matches (80%+)
- Average years of experience

## 🔧 Customization

### Adjust Scoring Weights

Edit `app.py` to customize weights:

```python
st.session_state.scorer = ResumeScorer(
    skill_weight=0.4,      # Emphasize skills more
    experience_weight=0.3,
    education_weight=0.1,
    semantic_weight=0.2
)
```

### Use Pinecone for Vector Storage

Set environment variables in `.env`:

```bash
PINECONE_API_KEY=your_api_key_here
PINECONE_ENVIRONMENT=your_environment_here
```

### Use OpenAI for Enhanced Parsing

Add to `.env`:

```bash
OPENAI_API_KEY=your_api_key_here
```

## 💡 Tips for Best Results

### Writing Good Job Descriptions
1. **Be Specific**: List exact skills needed (e.g., "Python 3.x", not just "programming")
2. **Include Numbers**: Use "5+ years" instead of "several years"
3. **State Education**: Clearly mention "Bachelor's required" or "Master's preferred"
4. **Use Keywords**: Include industry-standard terms that appear on resumes

### Preparing Resumes
1. **Format Consistency**: Use standard PDF or DOCX formats
2. **Clear Structure**: Organize into sections (Skills, Experience, Education)
3. **Keywords**: Include relevant technical terms and certifications
4. **Years Format**: Use "5 years experience" or "2020-2025" formats

## 🐛 Troubleshooting

### Resume Parsing Issues
- **Problem**: Skills not extracted correctly
- **Solution**: Ensure skills are in a dedicated "Skills" section

### Low Scores for Good Candidates
- **Problem**: Qualified candidates getting low scores
- **Solution**: Check if job description uses same terminology as resume

### Semantic Similarity Low
- **Problem**: Low semantic scores despite good match
- **Solution**: This is normal - it's just one of four components

### Slow Performance
- **Problem**: Analysis takes too long
- **Solution**: 
  - Use fewer resumes at once
  - Disable Pinecone if not needed
  - Check internet connection for AI features

## 📚 Module Documentation

### Resume Parser
See `RESUME_PARSER_README.md` for detailed parser documentation

### Embeddings
See `EMBEDDINGS_DOCUMENTATION.md` for vector database setup

### Scoring
See `scoring.py` for scoring algorithm details

## 🔍 Example Workflow

```
1. Upload 10 resumes for "Senior ML Engineer" position
   ↓
2. Paste job description with requirements:
   - 5+ years ML experience
   - Python, TensorFlow, AWS
   - Master's degree preferred
   ↓
3. Click "Analyze"
   ↓
4. Review results:
   - Candidate A: 87% match (Strong)
   - Candidate B: 72% match (Good)
   - Candidate C: 54% match (Moderate)
   ↓
5. Check detailed breakdown for top candidates
   ↓
6. Export JSON data if needed for further processing
```

## 🎓 Advanced Usage

### Batch Processing
```python
from scoring import score_resumes_batch

resumes = [resume1, resume2, resume3]
job_desc = "Python developer needed..."

results = score_resumes_batch(resumes, job_desc)
```

### Custom Scoring Logic
```python
from scoring import ResumeScorer

scorer = ResumeScorer(
    skill_weight=0.5,
    experience_weight=0.3,
    education_weight=0.1,
    semantic_weight=0.1
)

breakdown = scorer.score_resume(resume, job_description)
```

### Export Results
```python
# Get score breakdown as dictionary
result_dict = breakdown.to_dict()

# Save to JSON
import json
with open('scores.json', 'w') as f:
    json.dump(result_dict, f, indent=2)
```

## 📞 Support

For issues or questions:
1. Check example files: `example_scoring.py`, `example_embeddings.py`
2. Run tests: `python test_scoring.py`
3. Review documentation files in the project directory

## 🔄 Updates

The system automatically:
- Downloads sentence-transformers model on first run
- Initializes FAISS index for vector storage
- Caches parsed resume data in session state

No manual setup required beyond installing dependencies!

---

**Happy analyzing! 🎉**
