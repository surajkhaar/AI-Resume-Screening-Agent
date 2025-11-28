# 🎯 AI Explainability Feature - Documentation

## Overview

The explainability feature generates human-readable explanations for why a candidate matches or doesn't match a job position. It uses OpenAI's GPT-4 with deterministic prompting and few-shot examples to produce consistent, actionable insights.

## Key Features

### ✅ What It Provides

1. **Concise Summary** (max 120 words)
   - Human-readable explanation of the match
   - References specific skills and qualifications
   - Contextualizes the score components

2. **Top 3 Reasons** (bullet points)
   - Specific rationale for match/mismatch
   - References actual candidate data
   - Actionable insights for decision-making

3. **Clear Recommendation**
   - "Strong Match - Highly recommended for interview"
   - "Good Match - Worth considering"
   - "Moderate Match - Review carefully"
   - "Weak Match - Not suitable for this position"

## Usage

### Basic Usage

```python
from scoring import explain_match

# Simple usage
explanation = explain_match(
    resume_data=resume,
    job_description=job_description
)

print(explanation.summary)
print(explanation.top_reasons)
print(explanation.recommendation)
```

### With Pre-Computed Score

```python
from scoring import score_resume, explain_match

# Compute score first (more efficient for batch processing)
breakdown = score_resume(resume, job_description)

# Generate explanation using pre-computed score
explanation = explain_match(
    resume_data=resume,
    job_description=job_description,
    score_breakdown=breakdown
)
```

### With Custom API Key

```python
# Pass API key directly
explanation = explain_match(
    resume_data=resume,
    job_description=job_description,
    api_key="sk-your-api-key"
)

# Or use environment variable
import os
os.environ["OPENAI_API_KEY"] = "sk-your-api-key"
explanation = explain_match(resume, job_description)
```

### Using the Scorer Class

```python
from scoring import ResumeScorer

scorer = ResumeScorer()

# Score and explain
breakdown = scorer.score_resume(resume, job_description)
explanation = scorer.explain_match(resume, job_description, breakdown)
```

## Output Format

### MatchExplanation Object

```python
@dataclass
class MatchExplanation:
    summary: str              # Max 120 words
    top_reasons: List[str]    # Exactly 3 reasons
    recommendation: str       # Overall recommendation
```

### Example Output

```python
MatchExplanation(
    summary="John Smith is an excellent fit for the Senior Backend Engineer role. 
             With 6 years of experience and a Master's degree, he exceeds the minimum 
             qualifications. His technical skills align perfectly with the job requirements, 
             particularly his expertise in Python and Django.",
    
    top_reasons=[
        "Strong technical match: Possesses all core required skills (Python, Django, PostgreSQL) with demonstrated AWS cloud experience",
        "Experience level exceeds requirement: 6 years of experience surpasses the 5+ years requirement, indicating senior-level capability",
        "Educational qualification met: Master's in Computer Science aligns with preferred degree requirement"
    ],
    
    recommendation="Strong Match - Highly recommended for interview"
)
```

### JSON Export

```python
# Convert to dictionary for export
explanation_dict = explanation.to_dict()

import json
json.dumps(explanation_dict, indent=2)
```

Output:
```json
{
  "summary": "John Smith is an excellent fit...",
  "top_reasons": [
    "Strong technical match: Possesses all core required skills...",
    "Experience level exceeds requirement: 6 years...",
    "Educational qualification met: Master's in CS..."
  ],
  "recommendation": "Strong Match - Highly recommended for interview"
}
```

## Technical Implementation

### GPT-4 Configuration

```python
response = client.chat.completions.create(
    model="gpt-4",
    temperature=0.3,      # Low for consistency
    max_tokens=500,
    top_p=0.9
)
```

### Few-Shot Prompting

The system uses 3 carefully crafted examples:

1. **Example 1**: Strong match (87% score)
   - All requirements met
   - Experience exceeds requirement
   - Proper education level

2. **Example 2**: Weak match (34% score)
   - Skills mismatch
   - Insufficient experience
   - Education gap

3. **Example 3**: Moderate match (68% score)
   - Good foundation
   - Slightly under experience requirement
   - Education requirement met

These examples guide GPT-4 to produce consistent, structured responses.

### Deterministic Behavior

- **Temperature 0.3**: Reduces randomness while maintaining quality
- **Fixed format**: Examples enforce consistent output structure
- **Structured parsing**: Regex extracts sections reliably

### Fallback Mechanism

If OpenAI call fails, the system provides a rule-based explanation:

```python
if score_breakdown.final_score >= 0.8:
    rec = "Strong Match"
    summary = f"{candidate_name} shows strong alignment with requirements."
elif score_breakdown.final_score >= 0.6:
    rec = "Good Match"
    summary = f"{candidate_name} demonstrates good fit with some improvements."
# ... etc
```

## Error Handling

### Missing OpenAI Library

```python
try:
    explanation = explain_match(resume, job_description)
except ImportError:
    print("Install OpenAI: pip install openai")
```

### Missing API Key

```python
try:
    explanation = explain_match(resume, job_description)
except ValueError:
    print("Set OPENAI_API_KEY environment variable")
```

### API Errors

The system automatically falls back to rule-based explanations if the API call fails.

## Best Practices

### 1. Batch Processing

```python
scorer = ResumeScorer()

for resume in resumes:
    # Compute score once
    breakdown = scorer.score_resume(resume, job_description)
    
    # Generate explanation using cached score
    explanation = scorer.explain_match(resume, job_description, breakdown)
    
    # Store or display
    results.append({
        "candidate": resume["name"],
        "score": breakdown.final_score,
        "explanation": explanation.to_dict()
    })
```

### 2. Caching Explanations

```python
import json

# Generate once
explanation = explain_match(resume, job_description)

# Cache as JSON
with open(f"explanations/{resume['name']}.json", "w") as f:
    json.dump(explanation.to_dict(), f)

# Load later
with open(f"explanations/{resume['name']}.json", "r") as f:
    cached_explanation = json.load(f)
```

### 3. Rate Limiting

```python
import time

for resume in resumes:
    explanation = explain_match(resume, job_description)
    time.sleep(1)  # Respect OpenAI rate limits
```

## Examples

### Example 1: Strong Match

**Input:**
- Candidate: 6 years ML experience, Master's in CS, Python/TensorFlow/AWS
- Job: Senior ML Engineer, 5+ years, Python, TensorFlow, Master's preferred

**Output:**
```
Summary: Excellent fit with all requirements exceeded. Strong technical alignment 
         and senior-level experience make this candidate highly suitable.

Top 3 Reasons:
1. All core technical skills present including Python, TensorFlow, and AWS
2. 6 years experience exceeds 5+ requirement showing senior capability
3. Master's in CS meets preferred educational qualification

Recommendation: Strong Match - Highly recommended for interview
```

### Example 2: Weak Match

**Input:**
- Candidate: 3 years frontend (React/JS), Bachelor's in Design
- Job: Senior ML Engineer, 5+ years, Python/ML, Master's required

**Output:**
```
Summary: Poor alignment with position requirements. Background in frontend 
         development lacks ML specialization. Experience and education both 
         fall short of requirements.

Top 3 Reasons:
1. Skills mismatch: React/JavaScript vs required Python/ML frameworks
2. Insufficient experience: 3 years vs 5+ required
3. Education gap: Bachelor's in Design vs required Master's in CS

Recommendation: Weak Match - Not suitable for this position
```

### Example 3: Moderate Match

**Input:**
- Candidate: 4 years ML, scikit-learn, Master's in Data Science
- Job: ML Engineer, 5+ years, TensorFlow, Master's preferred

**Output:**
```
Summary: Good foundation with relevant education and ML background. Slightly 
         under experience requirement and missing specific TensorFlow expertise, 
         but shows strong potential.

Top 3 Reasons:
1. Solid ML foundation though with scikit-learn vs required TensorFlow
2. Master's in Data Science meets educational preference
3. 4 years vs 5+ required is close enough to demonstrate capability

Recommendation: Good Match - Worth considering with TensorFlow training
```

## Performance

- **Latency**: ~2-3 seconds per explanation (GPT-4 API call)
- **Cost**: ~$0.03-0.06 per explanation (GPT-4 pricing)
- **Quality**: Highly consistent with few-shot examples
- **Fallback**: <100ms for rule-based explanations

## Testing

Run tests:
```bash
python test_explainability.py
```

Test coverage includes:
- MatchExplanation dataclass structure
- OpenAI integration
- API key validation
- Error handling and fallbacks
- Prompt construction
- Response parsing
- Few-shot examples inclusion

## Integration

### With Streamlit App

```python
# In app.py
from scoring import explain_match

if analyze_button:
    for resume, breakdown in scored_results:
        # Generate explanation
        try:
            explanation = explain_match(resume, job_description, breakdown)
            
            # Display in UI
            st.markdown("**AI Explanation:**")
            st.write(explanation.summary)
            
            st.markdown("**Top Reasons:**")
            for reason in explanation.top_reasons:
                st.write(f"• {reason}")
            
            st.info(explanation.recommendation)
        except Exception as e:
            st.warning("Explanation not available")
```

### With REST API

```python
from fastapi import FastAPI
from scoring import explain_match

app = FastAPI()

@app.post("/explain")
async def get_explanation(resume: dict, job_description: str):
    try:
        explanation = explain_match(resume, job_description)
        return explanation.to_dict()
    except Exception as e:
        return {"error": str(e)}
```

## Future Enhancements

Potential improvements:
- [ ] Support for different LLM providers (Anthropic, etc.)
- [ ] Customizable prompt templates
- [ ] Multi-language support
- [ ] Explanation caching layer
- [ ] Comparative explanations (why A > B)
- [ ] Interview question suggestions based on gaps
- [ ] Skill development recommendations

## References

- OpenAI API: https://platform.openai.com/docs/
- Few-shot learning: https://arxiv.org/abs/2005.14165
- Prompt engineering: https://www.promptingguide.ai/

---

**For more examples, see `example_explainability.py`**
