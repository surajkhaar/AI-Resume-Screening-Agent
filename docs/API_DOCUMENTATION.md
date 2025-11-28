# Resume Parser API Documentation

## Table of Contents
- [Classes](#classes)
- [Functions](#functions)
- [Return Types](#return-types)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Classes

### `ResumeParser`

Main class for parsing resume files and extracting structured information.

#### Constructor

```python
ResumeParser(openai_api_key: Optional[str] = None)
```

**Parameters:**
- `openai_api_key` (str, optional): OpenAI API key for enhanced extraction. If not provided, will attempt to read from `OPENAI_API_KEY` environment variable.

**Example:**
```python
# With explicit API key
parser = ResumeParser(openai_api_key="sk-...")

# From environment variable
parser = ResumeParser()

# Without OpenAI (regex only)
parser = ResumeParser(openai_api_key=None)
```

---

#### Methods

##### `parse_resume()`

Parse resume from binary content.

```python
parse_resume(file_content: bytes, file_type: str) -> Dict
```

**Parameters:**
- `file_content` (bytes): Binary content of the resume file
- `file_type` (str): File type - either `'pdf'` or `'docx'`

**Returns:**
- `Dict`: Dictionary containing structured resume data

**Raises:**
- `ValueError`: If file_type is not supported
- `Exception`: If text extraction fails

**Example:**
```python
with open("resume.pdf", "rb") as f:
    content = f.read()

result = parser.parse_resume(content, "pdf")
```

---

##### `parse_resume_from_file()`

Convenience method to parse resume directly from file path.

```python
parse_resume_from_file(file_path: str) -> Dict
```

**Parameters:**
- `file_path` (str): Path to the resume file

**Returns:**
- `Dict`: Dictionary containing structured resume data

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `Exception`: If parsing fails

**Example:**
```python
result = parser.parse_resume_from_file("path/to/resume.pdf")
```

---

### Internal Methods

These methods are used internally by the parser but can be accessed if needed.

##### `_extract_text()`
Extract raw text from file content.

```python
_extract_text(file_content: bytes, file_type: str) -> str
```

##### `_extract_from_pdf()`
Extract text from PDF file using pdfplumber.

```python
_extract_from_pdf(file_content: bytes) -> str
```

##### `_extract_from_docx()`
Extract text from DOCX file using python-docx.

```python
_extract_from_docx(file_content: bytes) -> str
```

##### `_extract_structured_data()`
Extract structured information using regex patterns.

```python
_extract_structured_data(text: str) -> Dict
```

##### `_extract_name()`
Extract candidate name from text.

```python
_extract_name(text: str) -> Optional[str]
```

##### `_extract_email()`
Extract email address from text.

```python
_extract_email(text: str) -> Optional[str]
```

##### `_extract_phone()`
Extract phone number from text.

```python
_extract_phone(text: str) -> Optional[str]
```

##### `_extract_skills()`
Extract skills from text.

```python
_extract_skills(text: str) -> List[str]
```

##### `_extract_experience_years()`
Extract or calculate years of experience.

```python
_extract_experience_years(text: str) -> Optional[float]
```

##### `_extract_education()`
Extract education information.

```python
_extract_education(text: str) -> List[Dict[str, str]]
```

##### `_extract_summary()`
Extract professional summary or objective.

```python
_extract_summary(text: str) -> Optional[str]
```

##### `_extract_section()`
Extract a specific section from resume text.

```python
_extract_section(text: str, keywords: List[str]) -> Optional[str]
```

##### `_is_data_incomplete()`
Check if extracted data needs OpenAI fallback.

```python
_is_data_incomplete(data: Dict) -> bool
```

##### `_extract_with_openai()`
Use OpenAI to extract or enhance data.

```python
_extract_with_openai(text: str, existing_data: Dict) -> Dict
```

---

## Functions

### `parse_resume()`

Standalone convenience function for quick parsing.

```python
parse_resume(
    file_content: bytes,
    file_type: str,
    openai_api_key: Optional[str] = None
) -> Dict
```

**Parameters:**
- `file_content` (bytes): Binary content of the resume file
- `file_type` (str): File type - `'pdf'` or `'docx'`
- `openai_api_key` (str, optional): OpenAI API key

**Returns:**
- `Dict`: Dictionary containing structured resume data

**Example:**
```python
from resume_parser import parse_resume

with open("resume.pdf", "rb") as f:
    result = parse_resume(f.read(), "pdf")
```

---

## Return Types

### Resume Data Dictionary

The parser returns a dictionary with the following structure:

```python
{
    "name": str | None,           # Full name of candidate
    "email": str | None,          # Email address
    "phone": str | None,          # Phone number
    "skills": List[str],          # List of skills
    "experience_years": float | None,  # Years of experience
    "education": List[Dict[str, str]], # Education entries
    "summary": str | None         # Professional summary
}
```

### Education Entry

Each education entry in the `education` list has:

```python
{
    "degree": str,      # Degree name
    "year": str | None, # Graduation year
    "details": str      # Full details string
}
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | `str` or `None` | Candidate's full name | "John Doe" |
| `email` | `str` or `None` | Email address | "john@email.com" |
| `phone` | `str` or `None` | Phone number (various formats) | "+1-234-567-8900" |
| `skills` | `List[str]` | Technical and professional skills | ["Python", "AWS"] |
| `experience_years` | `float` or `None` | Total years of experience | 5.0 |
| `education` | `List[Dict]` | Education history | See above |
| `summary` | `str` or `None` | Professional summary | "Experienced..." |

---

## Error Handling

### Common Exceptions

```python
# File type not supported
try:
    result = parser.parse_resume(content, "txt")
except ValueError as e:
    print(f"Unsupported file type: {e}")

# File not found
try:
    result = parser.parse_resume_from_file("nonexistent.pdf")
except FileNotFoundError:
    print("File not found")

# General parsing error
try:
    result = parser.parse_resume(content, "pdf")
except Exception as e:
    print(f"Parsing failed: {e}")
```

### Data Validation

```python
result = parser.parse_resume(content, "pdf")

# Check for required fields
if not result.get("email"):
    print("Warning: Email not found")

if not result.get("name"):
    print("Warning: Name not found")

# Check for optional fields
if not result.get("skills"):
    print("Info: No skills extracted")

# Validate data completeness
required_fields = ["name", "email"]
missing = [f for f in required_fields if not result.get(f)]

if missing:
    print(f"Missing fields: {', '.join(missing)}")
```

---

## Examples

### Example 1: Simple Parse

```python
from resume_parser import ResumeParser

parser = ResumeParser()

with open("resume.pdf", "rb") as f:
    result = parser.parse_resume(f.read(), "pdf")

print(f"Name: {result['name']}")
print(f"Email: {result['email']}")
print(f"Skills: {', '.join(result['skills'])}")
```

### Example 2: With OpenAI

```python
import os
from resume_parser import ResumeParser

parser = ResumeParser(openai_api_key=os.getenv("OPENAI_API_KEY"))

result = parser.parse_resume_from_file("resume.pdf")

# More accurate extraction with OpenAI
print(result)
```

### Example 3: Batch Processing

```python
from resume_parser import ResumeParser
import glob

parser = ResumeParser()
results = []

for file_path in glob.glob("resumes/*.pdf"):
    try:
        result = parser.parse_resume_from_file(file_path)
        result["filename"] = file_path
        results.append(result)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

print(f"Processed {len(results)} resumes")
```

### Example 4: Streamlit Integration

```python
import streamlit as st
from resume_parser import ResumeParser

# Initialize in session state
if "parser" not in st.session_state:
    st.session_state.parser = ResumeParser()

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file:
    file_type = "pdf" if uploaded_file.type == "application/pdf" else "docx"
    
    with st.spinner("Parsing resume..."):
        result = st.session_state.parser.parse_resume(
            uploaded_file.read(),
            file_type
        )
    
    # Display results
    st.success("Resume parsed successfully!")
    st.json(result)
    
    # Show summary
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Name", result.get("name", "N/A"))
        st.metric("Experience", f"{result.get('experience_years', 0)} years")
    with col2:
        st.metric("Email", result.get("email", "N/A"))
        st.metric("Skills", len(result.get("skills", [])))
```

### Example 5: Custom Validation

```python
from resume_parser import ResumeParser

def validate_resume(result: dict) -> tuple[bool, list[str]]:
    """Validate parsed resume data"""
    errors = []
    
    if not result.get("name"):
        errors.append("Name is required")
    
    if not result.get("email"):
        errors.append("Email is required")
    
    if not result.get("skills") or len(result["skills"]) < 3:
        errors.append("At least 3 skills required")
    
    if not result.get("experience_years") or result["experience_years"] < 2:
        errors.append("Minimum 2 years experience required")
    
    return len(errors) == 0, errors

# Use validation
parser = ResumeParser()
result = parser.parse_resume_from_file("resume.pdf")

is_valid, errors = validate_resume(result)

if is_valid:
    print("✓ Resume meets all requirements")
else:
    print("✗ Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

### Example 6: Data Transformation

```python
from resume_parser import ResumeParser
import pandas as pd

def parse_resumes_to_dataframe(file_paths: list) -> pd.DataFrame:
    """Parse multiple resumes and return as DataFrame"""
    parser = ResumeParser()
    data = []
    
    for file_path in file_paths:
        try:
            result = parser.parse_resume_from_file(file_path)
            
            data.append({
                "name": result.get("name"),
                "email": result.get("email"),
                "phone": result.get("phone"),
                "experience": result.get("experience_years"),
                "skills_count": len(result.get("skills", [])),
                "skills": ", ".join(result.get("skills", [])),
                "education_count": len(result.get("education", [])),
                "has_summary": bool(result.get("summary"))
            })
        except Exception as e:
            print(f"Error: {e}")
    
    return pd.DataFrame(data)

# Use function
files = ["resume1.pdf", "resume2.pdf", "resume3.pdf"]
df = parse_resumes_to_dataframe(files)
print(df)
```

---

## Performance Considerations

### Memory Usage

```python
# For large files, process in chunks
import gc

parser = ResumeParser()

for file_path in large_file_list:
    result = parser.parse_resume_from_file(file_path)
    # Process result
    # ...
    gc.collect()  # Force garbage collection
```

### Batch Processing Optimization

```python
from concurrent.futures import ThreadPoolExecutor
from resume_parser import ResumeParser

def parse_single(file_path: str) -> dict:
    parser = ResumeParser()
    return parser.parse_resume_from_file(file_path)

# Parallel processing
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(parse_single, file_paths))
```

---

## Best Practices

1. **Always handle exceptions** when parsing resumes
2. **Validate extracted data** before using it
3. **Use OpenAI** for better accuracy when possible
4. **Cache parser instance** in long-running applications
5. **Implement retries** for API failures
6. **Log parsing errors** for debugging
7. **Set timeouts** for OpenAI calls in production

---

## Version Information

- **Module Version**: 1.0.0
- **Python Version**: 3.8+
- **Required Dependencies**: See `requirements.txt`

---

## Support

For issues, questions, or contributions:
- Check `RESUME_PARSER_README.md` for detailed documentation
- See `example_usage.py` for code examples
- Review `test_resume_parser.py` for test cases
