# 🎨 Streamlit UI - Enhanced Features Guide

## Overview

The Resume Analyzer Streamlit UI has been enhanced with advanced features including:
- 📊 Visual score bars and progress indicators
- 🤖 AI-powered explanations with GPT-4
- 📥 CSV export functionality
- 💾 Supabase database integration
- 🏆 Enhanced candidate ranking display

## Features

### 1. Visual Score Bars

Each candidate now displays beautiful, color-coded score bars:

- **🌟 Excellent (80%+)**: Green gradient
- **👍 Good (60-79%)**: Blue gradient
- **🤔 Moderate (40-59%)**: Orange gradient
- **❌ Weak (<40%)**: Red gradient

**Components:**
- Overall match score bar (large, prominent)
- Individual progress bars for each scoring component:
  - Skills Match (35% weight)
  - Experience Match (25% weight)
  - Education Match (15% weight)
  - Semantic Match (25% weight)

### 2. AI Explanations

Each candidate receives an AI-generated explanation powered by GPT-4:

**Explanation Components:**
- **Summary**: Concise 120-word explanation of the match
- **Top 3 Reasons**: Specific bullet points explaining why the candidate matches or doesn't match
- **Recommendation**: Clear hiring recommendation (Strong Match, Good Match, etc.)

**Example Output:**
```
Summary: John Smith is an excellent fit for the Senior Backend Engineer role. 
With 6 years of experience and a Master's degree, he exceeds the minimum 
qualifications. His technical skills align perfectly...

Top 3 Reasons:
1. Strong technical match: Possesses all core required skills (Python, Django, PostgreSQL)
2. Experience level exceeds requirement: 6 years vs 5+ required
3. Educational qualification met: Master's in Computer Science

Recommendation: Strong Match - Highly recommended for interview
```

### 3. CSV Export

Download analysis results as a CSV file for further processing:

**Exported Columns:**
- Rank
- Name, Email, Phone
- Final Score
- Skills Match, Experience Match, Education Match, Semantic Match
- Experience Years, Required Experience
- Has Required Degree
- Matched Skills, Missing Skills
- Recommendation
- Explanation Summary
- Filename

**Usage:**
Click the "📥 Download Results as CSV" button at the top of the results section.

**Filename Format:**
`resume_analysis_YYYYMMDD_HHMMSS.csv`

### 4. Supabase Integration

All analysis results are automatically saved to Supabase (if configured):

**Stored Data:**
- Candidate information
- All scores and breakdowns
- AI explanations
- Resume data (JSON)
- Timestamp

**Benefits:**
- Historical tracking
- Analytics and reporting
- Multi-user collaboration
- Audit trail

## Setup Instructions

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required for AI explanations
export OPENAI_API_KEY="sk-your-openai-api-key"

# Optional - for database storage
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-supabase-anon-key"
```

### Supabase Setup

1. **Create a Supabase Account**: Visit [supabase.com](https://supabase.com)

2. **Create a New Project**

3. **Run the Setup SQL**:
   - Go to SQL Editor in Supabase dashboard
   - Copy contents of `supabase_setup.sql`
   - Run the SQL to create the table and indexes

4. **Get Your Credentials**:
   - Go to Project Settings > API
   - Copy "Project URL" → `SUPABASE_URL`
   - Copy "anon/public" key → `SUPABASE_KEY`

5. **Set Environment Variables**:
   ```bash
   export SUPABASE_URL="https://xxxxx.supabase.co"
   export SUPABASE_KEY="eyJhbGc..."
   ```

### Running the Application

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## User Interface Guide

### Step 1: Upload Resumes

1. Click "Choose resume files" in the left panel
2. Select one or more PDF or DOCX files
3. Click "📖 Extract Text from Resumes"
4. Review the extracted text and parsed data

### Step 2: Enter Job Description

1. Paste the complete job description in the text area
2. Include requirements, responsibilities, and qualifications
3. The app will show character and word count

### Step 3: Analyze

1. Click "🔍 Analyze Resumes" button
2. Wait for the analysis to complete (includes AI explanations)
3. If Supabase is configured, results are automatically saved

### Step 4: Review Results

**Top Section:**
- Download CSV button for exporting results

**Ranked Candidates:**
Each candidate card shows:
- Rank and overall match percentage
- Large visual score bar
- Score breakdown with progress bars
- AI explanation (summary, reasons, recommendation)
- Detailed information (contact, experience, education)
- Matched and missing skills
- Quick assessment
- Full data (expandable)

**Summary Statistics:**
- Total candidates
- Average score
- Strong matches count
- Average experience

**Skills Overview:**
- Skills found across candidates
- Skills missing in all candidates

## Advanced Features

### 1. Score Breakdown Visualization

Each candidate displays 4 component scores with progress bars:

```python
# The scores are weighted as follows:
Final Score = (
    Skills Match × 0.35 +
    Experience × 0.25 +
    Education × 0.15 +
    Semantic Match × 0.25
)
```

### 2. Smart Ranking

Candidates are automatically sorted by final score (highest first):
- Top 3 candidates expanded by default
- Color-coded emojis for quick identification
- Rank displayed in header

### 3. Database Features

When Supabase is enabled:

**Automatic Storage:**
- Every analysis is saved with timestamp
- Includes all scores and explanations
- Preserves resume data for later review

**Future Queries:**
- View historical analyses
- Track candidate progress
- Generate reports
- Compare across time periods

### 4. Explanation Quality

AI explanations are generated using:
- **Model**: GPT-4 (high quality)
- **Temperature**: 0.3 (consistent, deterministic)
- **Few-shot prompting**: 3 examples for consistency
- **Structured output**: Summary + Reasons + Recommendation

## Troubleshooting

### No Explanations Showing

**Cause**: OpenAI API key not configured

**Solution**:
```bash
export OPENAI_API_KEY="sk-your-key"
```

### Database Not Connected

**Status**: Yellow warning "Database: Not configured"

**Solution**:
1. Set up Supabase (see setup instructions)
2. Set environment variables
3. Restart the app

### CSV Download Not Working

**Cause**: No pandas installed or no results available

**Solution**:
```bash
pip install pandas==2.1.3
```

### Slow Performance

**Causes**:
- AI explanations take 2-3 seconds per candidate
- Large number of resumes

**Solutions**:
- Process resumes in batches
- Disable AI explanations temporarily (modify code)
- Use faster hardware/connection

## Code Examples

### Custom Scoring Weights

Edit `app.py` to modify scoring weights:

```python
# In ResumeScorer initialization
scorer = ResumeScorer(
    embeddings_manager=embeddings_manager,
    weights={
        'skills': 0.40,      # Increase skills importance
        'experience': 0.30,  # Increase experience importance
        'education': 0.10,   # Decrease education importance
        'semantic': 0.20     # Decrease semantic importance
    }
)
```

### Disable AI Explanations

To skip explanations for faster processing:

```python
# Comment out the explanation generation section
# results_with_explanations = []
# for resume_data, breakdown in scored_results:
#     results_with_explanations.append((resume_data, breakdown, None))
```

### Custom Export Format

Modify the CSV export columns in `app.py`:

```python
row = {
    "Rank": rank,
    "Name": resume_data.get("name"),
    "Score": f"{breakdown.final_score:.2%}",
    # Add custom fields here
    "Custom Field": your_custom_data,
}
```

## API Integration

The Supabase client can be used independently:

```python
from supabase_client import SupabaseManager

# Initialize
manager = SupabaseManager()

# Store analysis
manager.store_analysis(
    job_description="...",
    resume_data=resume_dict,
    score_breakdown=breakdown_dict,
    explanation=explanation_dict
)

# Query results
recent = manager.get_recent_analyses(limit=50)
top_candidates = manager.get_analyses_by_score_range(min_score=0.8)

# Statistics
stats = manager.get_statistics()
print(f"Total analyses: {stats['total_analyses']}")
print(f"Average score: {stats['average_score']:.2%}")
```

## Performance Metrics

**Analysis Time per Candidate:**
- Resume parsing: ~1-2 seconds
- Score calculation: ~0.5 seconds
- AI explanation: ~2-3 seconds
- Database storage: ~0.2 seconds
- **Total**: ~4-6 seconds per candidate

**For 10 candidates:**
- ~40-60 seconds total
- Most time spent on AI explanations

## Best Practices

1. **Batch Processing**: Upload all resumes at once for efficiency
2. **Clear Job Descriptions**: More detailed JDs = better matching
3. **Review Top 3**: Focus on the top-ranked candidates first
4. **Export Data**: Use CSV exports for record-keeping
5. **Monitor Database**: Regularly clean old analyses (90+ days)

## Future Enhancements

Planned features:
- [ ] Compare multiple candidates side-by-side
- [ ] Interview question generation
- [ ] Custom scoring templates
- [ ] Email integration
- [ ] Calendar scheduling
- [ ] Candidate feedback tracking
- [ ] Analytics dashboard
- [ ] Multi-language support

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the error messages in the UI
3. Check Streamlit logs in terminal
4. Verify environment variables are set

---

**Built with ❤️ using Streamlit, OpenAI, and Supabase**
