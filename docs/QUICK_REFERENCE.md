# 🚀 Quick Reference - Resume Analyzer Enhancements

## 🎯 Quick Start

```bash
# 1. Install dependencies (if needed)
pip install pandas==2.1.3

# 2. Set environment variables (optional)
export OPENAI_API_KEY="sk-your-key"           # For AI explanations
export SUPABASE_URL="https://xxx.supabase.co" # For database
export SUPABASE_KEY="your-key"                # For database

# 3. Run the app
streamlit run app.py
```

## 📊 New Features at a Glance

| Feature | Location | Required Setup |
|---------|----------|----------------|
| Visual Score Bars | Built-in | None |
| AI Explanations | `scoring.py` | `OPENAI_API_KEY` |
| CSV Export | Built-in | None |
| Supabase Storage | `supabase_client.py` | `SUPABASE_URL` + `SUPABASE_KEY` |
| Bias Detection | `bias_detection.py` | None |

## 🎨 Visual Score Bars

**What**: Color-coded progress bars for each score component

**Colors**:
- 🟢 80-100%: Excellent (Green)
- 🔵 60-79%: Good (Blue)
- 🟠 40-59%: Moderate (Orange)
- 🔴 0-39%: Weak (Red)

**Where**: Automatically shown for each candidate

## 🤖 AI Explanations

**What**: GPT-4 generated match explanations

**Output**:
- Summary (≤120 words)
- Top 3 reasons
- Recommendation

**Setup**:
```bash
export OPENAI_API_KEY="sk-your-key"
```

**Cost**: ~$0.03-0.06 per candidate

**Fallback**: Rule-based if OpenAI unavailable

## 📥 CSV Export

**What**: Download complete analysis results

**Includes**:
- Ranks, scores, contact info
- Matched/missing skills
- AI explanations
- Recommendations

**Usage**: Click "📥 Download Results as CSV" button

**Filename**: `resume_analysis_YYYYMMDD_HHMMSS.csv`

## 💾 Supabase Integration

**What**: Cloud database for all analyses

**Setup**:
1. Create account at [supabase.com](https://supabase.com)
2. Run `supabase_setup.sql` in SQL Editor
3. Set environment variables

**Benefits**:
- Historical tracking
- Query capabilities
- Statistics dashboard

**Code**:
```python
from supabase_client import SupabaseManager

manager = SupabaseManager()
recent = manager.get_recent_analyses(limit=10)
stats = manager.get_statistics()
```

## ⚖️ Bias Detection

**What**: Automated fairness checks

**Detects**:
- Missing data (>30%)
- Experience variance (CV > 0.7)
- Education patterns
- Score clustering
- Duplicates
- Parsing quality

**Does NOT**:
- Infer race, gender, age
- Make decisions
- Profile candidates

**Severity Levels**:
- 🚨 Critical: Address immediately
- ⚠️ Warning: Review carefully
- ℹ️ Info: Be aware

**Code**:
```python
from bias_detection import generate_bias_report

report = generate_bias_report(resumes, scores)
print(report.summary)

for flag in report.flags:
    print(f"[{flag.severity}] {flag.message}")
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `STREAMLIT_UI_GUIDE.md` | UI features & setup |
| `BIAS_DETECTION_GUIDE.md` | Bias detection details |
| `EXPLAINABILITY_GUIDE.md` | AI explanations |
| `FEATURE_ENHANCEMENTS_SUMMARY.md` | Complete change summary |
| `supabase_setup.sql` | Database schema |

## 🧪 Testing

```bash
# Test bias detection
python test_bias_detection.py

# Test UI features
python test_ui_features.py

# Run examples
python example_bias_detection.py
```

## 🎯 Common Tasks

### View Bias Report
1. Run analysis
2. Scroll to "⚖️ Bias Detection Report" section
3. Expand to see detailed flags
4. Review recommendations

### Export Results
1. Complete analysis
2. Click "📥 Download Results as CSV"
3. Open in Excel/Sheets
4. Filter, sort, analyze as needed

### Check Database Stats
```python
from supabase_client import SupabaseManager

manager = SupabaseManager()
stats = manager.get_statistics()

print(f"Total analyses: {stats['total_analyses']}")
print(f"Average score: {stats['average_score']:.1%}")
print(f"Strong matches: {stats['strong_matches']}")
```

### Generate AI Explanation
```python
from scoring import explain_match

explanation = explain_match(
    resume_data=resume,
    job_description=job_description
)

print(explanation.summary)
print(explanation.top_reasons)
print(explanation.recommendation)
```

### Detect Bias Issues
```python
from bias_detection import generate_bias_report

report = generate_bias_report(resumes)

if report.has_critical_flags():
    print("🚨 Critical issues detected!")
    for flag in report.get_flags_by_severity("critical"):
        print(f"  {flag.message}")
```

## ⚙️ Configuration

### Custom Bias Thresholds
```python
from bias_detection import BiasDetector

detector = BiasDetector(
    missing_field_threshold=0.4,  # 40% instead of 30%
    variance_threshold=0.8,       # 0.8 instead of 0.7
    score_spread_threshold=0.5    # 0.5 instead of 0.6
)

report = detector.generate_report(resumes)
```

### Custom Scoring Weights
```python
# In app.py
scorer = ResumeScorer(
    embeddings_manager=embeddings_manager,
    skill_weight=0.40,      # 40% (default: 35%)
    experience_weight=0.30, # 30% (default: 25%)
    education_weight=0.10,  # 10% (default: 15%)
    semantic_weight=0.20    # 20% (default: 25%)
)
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No explanations | Set `OPENAI_API_KEY` |
| Database error | Check Supabase credentials |
| Slow performance | AI explanations take 2-3s per candidate |
| Missing pandas | `pip install pandas` |
| Bias report empty | This is expected for high-quality data |

## 📊 Performance

| Operation | Time |
|-----------|------|
| Parse resume | 1-2s |
| Calculate scores | 0.5s |
| Generate explanation | 2-3s |
| Detect bias | <0.1s |
| Save to database | 0.2s |
| **Total per candidate** | **4-6s** |

## 🔐 Privacy & Security

✅ **Safe**:
- All processing local (except OpenAI API calls)
- No external tracking
- No demographic profiling
- Supabase optional

⚠️ **Consider**:
- OpenAI processes resume text (review their privacy policy)
- Supabase stores analysis results (configure RLS policies)
- CSV exports contain PII (handle securely)

## 🎓 Learning Path

1. **Start**: Run basic analysis with UI
2. **Explore**: Review bias detection report
3. **Export**: Download CSV for analysis
4. **Advanced**: Set up Supabase for tracking
5. **Expert**: Customize thresholds and weights

## 💡 Pro Tips

1. **Batch Processing**: Upload all resumes at once
2. **Review Top 3**: Focus on highest-ranked candidates first
3. **Check Bias Report**: Address warnings before making decisions
4. **Export Early**: CSV for record-keeping
5. **Track Over Time**: Use Supabase for analytics

## 🆘 Get Help

1. Check documentation files
2. Run example scripts
3. Review test cases
4. Check terminal logs
5. Verify environment variables

## 🎉 Quick Wins

**Immediate Value**:
- ✅ Visual score bars (no setup)
- ✅ CSV export (no setup)
- ✅ Bias detection (no setup)

**With 5 Minutes Setup**:
- ✅ AI explanations (OpenAI key)
- ✅ Database tracking (Supabase)

---

**Remember**: Use as a tool to support fair hiring, not replace human judgment.
