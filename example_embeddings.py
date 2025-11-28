"""
Example usage of the embeddings module
"""

from embeddings import EmbeddingsManager, create_embeddings_manager
from resume_parser import ResumeParser
import json


def example_basic_usage():
    """Example 1: Basic embeddings generation"""
    print("=" * 70)
    print("Example 1: Basic Embeddings Generation")
    print("=" * 70)
    
    # Create embeddings manager (will use FAISS fallback if no Pinecone key)
    manager = EmbeddingsManager()
    
    # Generate single embedding
    text = "Python developer with 5 years experience in Django and AWS"
    embedding = manager.generate_embedding(text)
    
    print(f"Text: {text}")
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding dimension: {manager.embedding_dimension}")
    print(f"Vector DB type: {manager.vector_db_type}")
    print()


def example_upsert_resume():
    """Example 2: Upsert resume to vector database"""
    print("=" * 70)
    print("Example 2: Upsert Resume to Vector Database")
    print("=" * 70)
    
    manager = EmbeddingsManager()
    
    # Sample resume data
    resume_data = {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "+1-234-567-8900",
        "skills": ["Python", "Machine Learning", "Docker", "AWS"],
        "experience_years": 5,
        "education": [
            {"degree": "MS Computer Science", "year": "2019"}
        ],
        "summary": "Experienced software engineer specializing in ML applications"
    }
    
    # Upsert to vector database
    success = manager.upsert_resume("resume_001", resume_data)
    
    if success:
        print(f"✓ Successfully upserted resume: {resume_data['name']}")
        print(f"  Email: {resume_data['email']}")
        print(f"  Skills: {', '.join(resume_data['skills'])}")
    else:
        print("✗ Failed to upsert resume")
    
    print()


def example_batch_upsert():
    """Example 3: Batch upsert multiple resumes"""
    print("=" * 70)
    print("Example 3: Batch Upsert Multiple Resumes")
    print("=" * 70)
    
    manager = EmbeddingsManager()
    
    resumes = [
        ("resume_001", {
            "name": "Alice Smith",
            "skills": ["Python", "TensorFlow", "Deep Learning"],
            "experience_years": 7
        }),
        ("resume_002", {
            "name": "Bob Johnson",
            "skills": ["Java", "Spring Boot", "Microservices"],
            "experience_years": 5
        }),
        ("resume_003", {
            "name": "Carol Williams",
            "skills": ["JavaScript", "React", "Node.js"],
            "experience_years": 4
        })
    ]
    
    results = manager.upsert_resumes_batch(resumes)
    
    print(f"Processed {len(results)} resumes:")
    for resume_id, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {resume_id}")
    
    print()


def example_search_resumes():
    """Example 4: Search for similar resumes"""
    print("=" * 70)
    print("Example 4: Search for Similar Resumes")
    print("=" * 70)
    
    manager = EmbeddingsManager()
    
    # First, add some resumes
    resumes = [
        ("resume_001", {
            "name": "Python Expert",
            "skills": ["Python", "Django", "FastAPI", "PostgreSQL"],
            "experience_years": 6
        }),
        ("resume_002", {
            "name": "ML Engineer",
            "skills": ["Python", "TensorFlow", "PyTorch", "AWS"],
            "experience_years": 4
        }),
        ("resume_003", {
            "name": "Full Stack Developer",
            "skills": ["JavaScript", "React", "Node.js", "MongoDB"],
            "experience_years": 5
        })
    ]
    
    manager.upsert_resumes_batch(resumes)
    
    # Search for Python developers
    query = "Looking for Python developer with machine learning experience"
    results = manager.search(query, top_k=3)
    
    print(f"Query: {query}\n")
    print("Search Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. ID: {result['id']}")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Name: {result['metadata'].get('name', 'N/A')}")
        print(f"   Skills: {result['metadata'].get('skills', 'N/A')}")
        print()


def example_compare_resume_to_job():
    """Example 5: Compare resume to job description"""
    print("=" * 70)
    print("Example 5: Compare Resume to Job Description")
    print("=" * 70)
    
    manager = EmbeddingsManager()
    
    resume_data = {
        "name": "Jane Developer",
        "skills": ["Python", "Django", "React", "AWS", "Docker"],
        "experience_years": 5,
        "summary": "Full-stack developer with expertise in Python and React"
    }
    
    job_description = """
    We are looking for a Full Stack Developer with:
    - 3+ years experience with Python and Django
    - Experience with React and modern JavaScript
    - AWS and containerization knowledge
    - Strong problem-solving skills
    """
    
    score = manager.compare_resume_to_job(resume_data, job_description)
    
    print(f"Candidate: {resume_data['name']}")
    print(f"Skills: {', '.join(resume_data['skills'])}")
    print(f"\nMatch Score: {score:.2%}")
    
    if score > 0.8:
        print("✓ Excellent match!")
    elif score > 0.6:
        print("✓ Good match")
    elif score > 0.4:
        print("⚠ Partial match")
    else:
        print("✗ Poor match")
    
    print()


def example_rank_resumes():
    """Example 6: Rank multiple resumes against job description"""
    print("=" * 70)
    print("Example 6: Rank Multiple Resumes")
    print("=" * 70)
    
    manager = EmbeddingsManager()
    
    resumes = [
        {
            "name": "Alice ML Engineer",
            "skills": ["Python", "TensorFlow", "PyTorch", "Deep Learning", "AWS"],
            "experience_years": 6,
            "summary": "Machine learning engineer with PhD in CS"
        },
        {
            "name": "Bob Backend Dev",
            "skills": ["Java", "Spring", "Kubernetes", "Microservices"],
            "experience_years": 5,
            "summary": "Backend developer specializing in scalable systems"
        },
        {
            "name": "Carol Data Scientist",
            "skills": ["Python", "Scikit-learn", "Pandas", "Machine Learning"],
            "experience_years": 4,
            "summary": "Data scientist with strong Python and ML background"
        }
    ]
    
    job_description = """
    Machine Learning Engineer position:
    - Strong Python and ML frameworks (TensorFlow/PyTorch)
    - 3+ years ML experience
    - AWS cloud experience
    - PhD or MS in Computer Science preferred
    """
    
    ranked_resumes = manager.rank_resumes(resumes, job_description)
    
    print("Job Description:", job_description[:100] + "...\n")
    print("Ranked Candidates:")
    print("-" * 70)
    
    for rank, (resume, score) in enumerate(ranked_resumes, 1):
        print(f"\n{rank}. {resume['name']} - Match: {score:.2%}")
        print(f"   Skills: {', '.join(resume['skills'][:3])}...")
        print(f"   Experience: {resume['experience_years']} years")
    
    print()


def example_with_parser():
    """Example 7: Complete workflow with resume parser"""
    print("=" * 70)
    print("Example 7: Complete Workflow with Resume Parser")
    print("=" * 70)
    
    # Initialize both parser and embeddings manager
    parser = ResumeParser()
    embeddings_manager = EmbeddingsManager()
    
    # Simulate parsing a resume
    sample_resume_text = """
    John Doe
    john.doe@email.com | 555-1234
    
    SUMMARY
    Senior software engineer with 8 years experience
    
    SKILLS
    Python, Django, React, AWS, Docker, Kubernetes
    
    EXPERIENCE
    Senior Software Engineer - Tech Corp (2018-Present)
    """
    
    # In real usage, you'd parse from PDF/DOCX
    resume_data = {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "555-1234",
        "skills": ["Python", "Django", "React", "AWS", "Docker", "Kubernetes"],
        "experience_years": 8,
        "summary": "Senior software engineer with 8 years experience"
    }
    
    # Upsert to vector database
    success = embeddings_manager.upsert_resume("resume_john_doe", resume_data)
    
    print(f"Parsed Resume: {resume_data['name']}")
    print(f"Upsert Status: {'✓ Success' if success else '✗ Failed'}")
    print()
    
    # Now search for this candidate
    job_desc = "Looking for Python developer with AWS and Docker experience"
    score = embeddings_manager.compare_resume_to_job(resume_data, job_desc)
    
    print(f"Job Match Score: {score:.2%}")
    print()


def example_statistics():
    """Example 8: Get vector database statistics"""
    print("=" * 70)
    print("Example 8: Vector Database Statistics")
    print("=" * 70)
    
    manager = EmbeddingsManager()
    
    # Add some resumes
    for i in range(5):
        resume = {
            "name": f"Candidate {i+1}",
            "skills": ["Python", "JavaScript"],
            "experience_years": i + 2
        }
        manager.upsert_resume(f"resume_{i:03d}", resume)
    
    # Get statistics
    stats = manager.get_stats()
    
    print("Vector Database Statistics:")
    print(f"  Type: {stats['vector_db_type']}")
    print(f"  Embedding Dimension: {stats['embedding_dimension']}")
    print(f"  Total Vectors: {stats.get('total_vectors', 'N/A')}")
    print()


def example_faiss_persistence():
    """Example 9: Save and load FAISS index"""
    print("=" * 70)
    print("Example 9: FAISS Index Persistence")
    print("=" * 70)
    
    # Create manager with FAISS
    manager = EmbeddingsManager(use_faiss_fallback=True)
    
    # Add some data
    resume = {
        "name": "Test User",
        "skills": ["Python", "Java"],
        "experience_years": 5
    }
    manager.upsert_resume("resume_test", resume)
    
    # Save index
    if manager.vector_db_type == "faiss":
        manager.save_faiss_index("my_resume_index.bin")
        print("✓ FAISS index saved to 'my_resume_index.bin'")
        
        # Later, load the index
        # manager.load_faiss_index("my_resume_index.bin")
        # print("✓ FAISS index loaded")
    else:
        print("Not using FAISS, cannot demonstrate persistence")
    
    print()


def example_pinecone_setup():
    """Example 10: Using Pinecone (requires API key)"""
    print("=" * 70)
    print("Example 10: Pinecone Setup")
    print("=" * 70)
    
    print("""
To use Pinecone:

1. Get API key from https://www.pinecone.io/
2. Set environment variables:
   export PINECONE_API_KEY="your-api-key"
   export PINECONE_ENVIRONMENT="your-environment"

3. Create manager:
   manager = EmbeddingsManager(
       pinecone_api_key="your-key",
       pinecone_environment="your-env"
   )

4. Use normally:
   manager.upsert_resume("resume_001", resume_data)
   results = manager.search("Python developer", top_k=5)

Pinecone advantages:
- Cloud-hosted (no local storage needed)
- Scales to billions of vectors
- Built-in metadata filtering
- High availability
    """)
    print()


if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print("EMBEDDINGS MODULE - USAGE EXAMPLES")
    print("=" * 70)
    print()
    
    # Run examples (comment out ones you don't want to run)
    example_basic_usage()
    # example_upsert_resume()
    # example_batch_upsert()
    # example_search_resumes()
    # example_compare_resume_to_job()
    # example_rank_resumes()
    # example_with_parser()
    # example_statistics()
    # example_faiss_persistence()
    example_pinecone_setup()
    
    print("=" * 70)
    print("For more examples, uncomment the function calls above")
    print("=" * 70)
