"""
Example usage of the resume_parser module
"""

from resume_parser import ResumeParser, parse_resume
import json
import os


def example_parse_from_file():
    """Example: Parse resume from a file path"""
    print("Example 1: Parse from file path")
    print("-" * 50)
    
    parser = ResumeParser(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # Parse a PDF resume
    result = parser.parse_resume_from_file("sample_resume.pdf")
    
    print(json.dumps(result, indent=2))
    print("\n")


def example_parse_from_binary():
    """Example: Parse resume from binary content"""
    print("Example 2: Parse from binary content")
    print("-" * 50)
    
    # Read file as binary
    with open("sample_resume.pdf", "rb") as f:
        file_content = f.read()
    
    # Parse using the convenience function
    result = parse_resume(
        file_content=file_content,
        file_type="pdf",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    print(json.dumps(result, indent=2))
    print("\n")


def example_parse_uploaded_file():
    """Example: Parse resume from uploaded file (simulating Streamlit upload)"""
    print("Example 3: Parse uploaded file (Streamlit simulation)")
    print("-" * 50)
    
    # Simulating Streamlit uploaded file
    class UploadedFile:
        def __init__(self, path, file_type):
            self.name = path
            self.type = file_type
            with open(path, 'rb') as f:
                self.content = f.read()
        
        def read(self):
            return self.content
        
        def getvalue(self):
            return self.content
    
    # Simulate upload
    uploaded_file = UploadedFile("sample_resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    
    # Parse
    parser = ResumeParser()
    result = parser.parse_resume(
        file_content=uploaded_file.getvalue(),
        file_type="docx"
    )
    
    print(f"Parsed resume: {uploaded_file.name}")
    print(json.dumps(result, indent=2))
    print("\n")


def example_batch_processing():
    """Example: Process multiple resumes"""
    print("Example 4: Batch processing")
    print("-" * 50)
    
    resume_files = [
        ("resume1.pdf", "pdf"),
        ("resume2.docx", "docx"),
        ("resume3.pdf", "pdf")
    ]
    
    parser = ResumeParser(openai_api_key=os.getenv("OPENAI_API_KEY"))
    results = []
    
    for file_path, file_type in resume_files:
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                result = parser.parse_resume(file_content, file_type)
                result['filename'] = file_path
                results.append(result)
                
                print(f"✓ Processed: {file_path}")
                print(f"  Name: {result.get('name', 'N/A')}")
                print(f"  Email: {result.get('email', 'N/A')}")
                print(f"  Skills: {len(result.get('skills', []))} found")
                print()
        except Exception as e:
            print(f"✗ Error processing {file_path}: {str(e)}")
    
    # Save results to JSON
    with open('parsed_resumes.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Processed {len(results)} resumes. Results saved to 'parsed_resumes.json'")
    print("\n")


def example_custom_processing():
    """Example: Custom processing with error handling"""
    print("Example 5: Custom processing with error handling")
    print("-" * 50)
    
    parser = ResumeParser(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # Read resume
        with open("sample_resume.pdf", "rb") as f:
            file_content = f.read()
        
        # Parse
        result = parser.parse_resume(file_content, "pdf")
        
        # Custom validation
        required_fields = ['name', 'email']
        missing_fields = [field for field in required_fields if not result.get(field)]
        
        if missing_fields:
            print(f"⚠️  Warning: Missing required fields: {', '.join(missing_fields)}")
        else:
            print("✓ All required fields present")
        
        # Display results
        print(f"\nCandidate: {result.get('name', 'Unknown')}")
        print(f"Contact: {result.get('email', 'N/A')} | {result.get('phone', 'N/A')}")
        print(f"Experience: {result.get('experience_years', 'N/A')} years")
        print(f"Skills ({len(result.get('skills', []))}): {', '.join(result.get('skills', [])[:5])}")
        
        if result.get('education'):
            print(f"Education: {len(result.get('education', []))} entries")
            for edu in result.get('education', []):
                print(f"  - {edu.get('degree', 'N/A')}")
        
        if result.get('summary'):
            print(f"\nSummary: {result['summary'][:100]}...")
        
    except FileNotFoundError:
        print("Error: Resume file not found")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\n")


def example_json_output():
    """Example: Expected JSON output format"""
    print("Example 6: Expected JSON Output Format")
    print("-" * 50)
    
    sample_output = {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "+1-234-567-8900",
        "skills": [
            "Python",
            "Machine Learning",
            "Django",
            "AWS",
            "Docker",
            "React",
            "SQL"
        ],
        "experience_years": 5.0,
        "education": [
            {
                "degree": "Master of Science in Computer Science",
                "year": "2019",
                "details": "Master of Science in Computer Science, Stanford University, 2019"
            },
            {
                "degree": "Bachelor of Science in Software Engineering",
                "year": "2017",
                "details": "Bachelor of Science in Software Engineering, MIT, 2017"
            }
        ],
        "summary": "Experienced software engineer with 5+ years in full-stack development and machine learning. Proven track record of building scalable applications and leading technical teams."
    }
    
    print(json.dumps(sample_output, indent=2))
    print("\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Resume Parser - Usage Examples")
    print("=" * 50)
    print("\n")
    
    # Show expected output format
    example_json_output()
    
    # Uncomment the examples you want to run:
    # Note: You'll need actual resume files to run these examples
    
    # example_parse_from_file()
    # example_parse_from_binary()
    # example_parse_uploaded_file()
    # example_batch_processing()
    # example_custom_processing()
    
    print("\nNote: To run the examples, provide actual resume files")
    print("and uncomment the example functions you want to test.")
