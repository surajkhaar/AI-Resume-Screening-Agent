# ⚖️ Bias Detection and Reporting - Documentation

## Overview

The Bias Detection module identifies potential issues in resume screening processes without inferring protected attributes (race, gender, age, religion, etc.). It analyzes data quality, statistical patterns, and potential systemic issues that could lead to unfair evaluation.

## Key Principles

### What It Does ✅
- **Detects missing or incomplete data** that may disadvantage candidates
- **Identifies extreme statistical variance** in experience, education, etc.
- **Flags suspicious patterns** like score clustering or perfect score rates
- **Checks data consistency** for duplicates and parsing quality
- **Warns about potential bias sources** without making assumptions

### What It Does NOT Do ❌
- **Does NOT infer protected attributes** (race, gender, age, etc.)
- **Does NOT make hiring decisions** (only provides warnings)
- **Does NOT replace human judgment** (augments recruiter decision-making)
- **Does NOT access external demographic data**
- **Does NOT profile candidates** based on personal characteristics

## Features

### 1. Missing Field Detection

Identifies candidates with missing critical information:
- Name, email, phone
- Skills, experience, education
- Flags high rates of missing data (>30% by default)

**Why it matters**: Missing data may cause qualified candidates to be unfairly scored lower.

### 2. Experience Variance Analysis

Detects extreme variance in experience distribution:
- Calculates coefficient of variation (CV)
- Flags if CV > 0.7 (highly heterogeneous pool)
- Identifies candidates at extremes

**Why it matters**: Large experience spreads may indicate unclear job requirements or over-broad candidate pool.

### 3. Education Distribution Patterns

Analyzes education level distribution:
- Checks for missing education data
- Detects heavily skewed distributions (>80% same level)
- Identifies homogeneity or heterogeneity

**Why it matters**: Extreme homogeneity may indicate overly restrictive requirements that exclude qualified candidates.

### 4. Skill Diversity Checks

Evaluates skill extraction quality:
- Monitors average skills per candidate
- Flags low skill counts (<3 per candidate)
- Identifies total skill diversity

**Why it matters**: Low skill extraction may indicate parsing issues or overly strict extraction logic.

### 5. Scoring Pattern Analysis

Identifies suspicious scoring patterns:
- **Score clustering**: All scores within narrow range (<0.6 spread)
- **Perfect scores**: Unusually high rate of near-perfect scores (>30%)
- **Distribution issues**: Lack of differentiation between candidates

**Why it matters**: Narrow distributions may indicate scoring system isn't effectively differentiating candidates.

### 6. Data Consistency Checks

Validates data integrity:
- **Duplicate detection**: Same name appearing multiple times
- **Email patterns**: High concentration in single domain (>70%)
- **Parsing quality**: Incomplete data extraction

**Why it matters**: Data quality issues can lead to unfair evaluations and skewed statistics.

## Usage

### Basic Usage

```python
from bias_detection import generate_bias_report

# Generate report
report = generate_bias_report(
    resumes=parsed_resumes,
    score_breakdowns=score_data  # Optional
)

# Check for issues
if report.has_critical_flags():
    print("🚨 Critical issues detected!")

if report.has_warnings():
    print("⚠️  Warnings found!")

# Print summary
print(report.summary)

# Review flags
for flag in report.flags:
    print(f"[{flag.severity}] {flag.message}")
    print(f"Recommendation: {flag.recommendation}")
```

### Streamlit Integration

The bias report is automatically displayed in the Streamlit UI after analysis:

```python
# In app.py - automatically generated during analysis
bias_report = generate_bias_report(
    st.session_state.parsed_resumes,
    score_breakdown_dicts
)

# Display in UI with color-coded warnings
if bias_report.has_critical_flags():
    st.error(bias_report.summary)
elif bias_report.has_warnings():
    st.warning(bias_report.summary)
else:
    st.success(bias_report.summary)
```

### Custom Thresholds

Adjust sensitivity to match your needs:

```python
from bias_detection import BiasDetector

detector = BiasDetector(
    missing_field_threshold=0.3,  # Flag if >30% missing
    variance_threshold=0.7,       # Flag if CV > 0.7
    score_spread_threshold=0.6    # Flag if spread < 0.6
)

report = detector.generate_report(resumes, scores)
```

## Flag Severity Levels

### 🚨 Critical
Issues that may significantly impact fairness:
- No skills extracted from any candidate
- >50% missing critical fields
- Severe parsing failures

**Action**: Address immediately before making hiring decisions.

### ⚠️ Warning
Issues that warrant review:
- 30-50% missing fields
- Extreme variance or homogeneity
- Suspicious patterns
- Duplicate candidates

**Action**: Review and adjust process as needed.

### ℹ️ Info
Informational notices:
- Minor patterns worth noting
- Edge cases
- Statistical observations

**Action**: Be aware but may not require immediate action.

## Flag Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `missing_data` | Missing or incomplete fields | No email, no skills, no education |
| `variance` | Extreme statistical variance | Experience spread too wide |
| `pattern` | Suspicious patterns | Score clustering, perfect scores |
| `consistency` | Data consistency issues | Duplicates, parsing errors |
| `parsing_quality` | Poor parsing results | <50% fields extracted |

## BiasReport Structure

```python
@dataclass
class BiasReport:
    total_candidates: int
    flags: List[BiasFlag]
    summary: str
    
    def has_critical_flags() -> bool
    def has_warnings() -> bool
    def get_flags_by_severity(severity: str) -> List[BiasFlag]
    def to_dict() -> Dict[str, Any]
```

## BiasFlag Structure

```python
@dataclass
class BiasFlag:
    severity: str              # "critical", "warning", "info"
    category: str              # "missing_data", "variance", etc.
    message: str               # Human-readable description
    affected_candidates: List[str]  # Names of affected candidates
    recommendation: str        # Action to take
    details: Dict[str, Any]    # Technical details
```

## Examples

### Example 1: Missing Skills

```python
resumes = [
    {"name": "Alice", "skills": ["Python"], "experience_years": 5},
    {"name": "Bob", "experience_years": 4},  # Missing skills
    {"name": "Carol", "experience_years": 6},  # Missing skills
]

report = generate_bias_report(resumes)

# Output:
# [WARNING] High rate of missing 'skills' field (66.7% of candidates)
# Recommendation: Review resume parsing for 'skills' extraction.
# Missing data may lead to unfair evaluation.
```

### Example 2: Experience Variance

```python
resumes = [
    {"name": "Junior", "skills": ["Python"], "experience_years": 1},
    {"name": "Senior", "skills": ["Python"], "experience_years": 25},
]

report = generate_bias_report(resumes)

# Output:
# [WARNING] Extreme variance in experience distribution (CV=1.13)
# Recommendation: Review if job requirements are clearly defined.
# Large experience spread may indicate unclear requirements.
```

### Example 3: Score Clustering

```python
resumes = [...]
scores = [
    {"final_score": 0.75},
    {"final_score": 0.76},
    {"final_score": 0.77},
]

report = generate_bias_report(resumes, scores)

# Output:
# [WARNING] Scores clustered in narrow range (spread: 2.0%)
# Recommendation: Review scoring methodology. Narrow score 
# distribution may indicate system is not differentiating candidates.
```

## Integration with Streamlit UI

The bias report appears automatically after analysis:

1. **Summary Banner**: Color-coded (red for critical, yellow for warnings, green for clean)
2. **Expandable Details**: Click to view all flags
3. **Grouped by Severity**: Critical, Warning, Info sections
4. **Affected Candidates**: See who is impacted
5. **Technical Details**: JSON data for deeper investigation
6. **Disclaimer**: Reminds users about responsible usage

## Best Practices

### 1. Review Context
Always review flags in the context of your specific hiring process. What's normal for one role may be unusual for another.

### 2. Use as a Tool, Not a Rule
Bias detection provides warnings, not mandates. Use professional judgment.

### 3. Fix Data Quality Issues First
Address critical and warning flags related to parsing and data quality before making decisions.

### 4. Document Actions Taken
Keep records of bias reports and actions taken to address issues.

### 5. Adjust Thresholds
Customize thresholds based on your organization's standards and typical candidate pools.

### 6. Regular Audits
Periodically review bias reports across multiple hiring cycles to identify systemic issues.

## Limitations

### What This Module Cannot Do

1. **Cannot Detect All Biases**: Only statistical and data quality issues
2. **Cannot Infer Demographics**: Does not access or infer protected attributes
3. **Cannot Replace Human Review**: Augments, not replaces, human judgment
4. **Cannot Guarantee Fairness**: Flagging issues doesn't automatically ensure fair outcomes
5. **Cannot Handle Context**: Doesn't understand business-specific nuances

### False Positives

Some flags may not indicate actual problems:
- **Domain concentration**: May be normal for internal referrals
- **Education homogeneity**: May be appropriate for specialized roles
- **Experience variance**: May be intentional for diverse team building

**Always apply professional judgment when interpreting flags.**

## Ethical Considerations

### Privacy
- **No external data**: Only analyzes provided resume data
- **No profiling**: Does not create demographic profiles
- **No tracking**: Does not track candidates across submissions

### Fairness
- **Warns, not decides**: Provides information for recruiters to consider
- **Transparent**: All logic is open and auditable
- **Configurable**: Organizations can adjust to their standards

### Responsibility
- **Human oversight required**: Never automate decisions based solely on bias reports
- **Context matters**: Professional judgment is essential
- **Continuous improvement**: Use feedback to refine detection logic

## Export and Reporting

### JSON Export

```python
report = generate_bias_report(resumes)
report_dict = report.to_dict()

import json
with open('bias_report.json', 'w') as f:
    json.dump(report_dict, f, indent=2)
```

### CSV Export (for tracking)

```python
import pandas as pd

flags_data = []
for flag in report.flags:
    flags_data.append({
        "Severity": flag.severity,
        "Category": flag.category,
        "Message": flag.message,
        "Affected Count": len(flag.affected_candidates),
        "Recommendation": flag.recommendation
    })

df = pd.DataFrame(flags_data)
df.to_csv('bias_flags.csv', index=False)
```

## Testing

Run the test suite:

```bash
python test_bias_detection.py
```

Run examples:

```bash
python example_bias_detection.py
```

## API Reference

### Functions

#### `generate_bias_report(resumes, score_breakdowns=None)`
Generate a comprehensive bias detection report.

**Parameters:**
- `resumes` (List[Dict]): List of parsed resume dictionaries
- `score_breakdowns` (List[Dict], optional): List of score breakdowns

**Returns:**
- `BiasReport`: Complete report with flags and summary

### Classes

#### `BiasDetector(missing_field_threshold=0.3, variance_threshold=0.7, score_spread_threshold=0.6)`
Main detector class with configurable thresholds.

**Methods:**
- `generate_report(resumes, score_breakdowns=None)`: Generate full report

#### `BiasReport`
Contains detection results.

**Attributes:**
- `total_candidates`: Number of candidates analyzed
- `flags`: List of BiasFlag objects
- `summary`: Human-readable summary

**Methods:**
- `has_critical_flags()`: Check for critical issues
- `has_warnings()`: Check for warnings
- `get_flags_by_severity(severity)`: Filter by severity
- `to_dict()`: Export to dictionary

#### `BiasFlag`
Represents a single bias warning.

**Attributes:**
- `severity`: "critical", "warning", or "info"
- `category`: Type of issue
- `message`: Description
- `affected_candidates`: List of candidate names
- `recommendation`: Suggested action
- `details`: Technical details dictionary

## Troubleshooting

### No Flags Generated
- **Cause**: Data quality is good
- **Solution**: This is expected for clean data

### Too Many Flags
- **Cause**: Thresholds too strict or data quality issues
- **Solution**: Review data quality first, then adjust thresholds

### Missing Expected Flags
- **Cause**: Thresholds too lenient
- **Solution**: Use stricter custom thresholds

## Future Enhancements

Planned features:
- [ ] Time-based trend analysis
- [ ] Comparative analysis across job postings
- [ ] Machine learning for pattern detection
- [ ] Integration with external fairness metrics
- [ ] Customizable flag definitions
- [ ] Historical tracking dashboard

## Support and Feedback

For issues or suggestions:
1. Review this documentation
2. Check example files
3. Run test suite
4. Adjust thresholds as needed

---

**Remember**: Bias detection is a tool to support fair hiring, not a replacement for human judgment and ethical hiring practices.
