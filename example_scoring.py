"""
Example usage of the scoring module

This file demonstrates various ways to use the scoring module to evaluate resumes
against job descriptions.
"""

from scoring import ResumeScorer, score_resume, score_resumes_batch
from embeddings import EmbeddingsManager


def example_1_basic_scoring():
    """Example 1: Basic resume scoring"""
    print("=" * 80)
    print("Example 1: Basic Resume Scoring")
    print("=" * 80)
    
    resume = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "skills": ["Python", "Machine Learning", "TensorFlow", "AWS", "Docker"],
        "experience_years": 5,
        "education": [
            {"degree": "Master of Science in Computer Science", "year": "2019"}
        ],
        "summary": "Experienced ML engineer with 5 years in production ML systems"
    }
    
    job_description = """
    Senior Machine Learning Engineer
    
    Requirements:
    - 3+ years of experience in machine learning
    - Strong Python programming skills
    - Experience with TensorFlow or PyTorch
    - AWS cloud experience
    - Master's degree in Computer Science or related field
    
    Nice to have:
    - Docker and Kubernetes
    - MLOps experience
    """
    
    # Score the resume
    breakdown = score_resume(resume, job_description)
    
    # Print results
    print(f"\nCandidate: {resume['name']}")
    print(f"Final Score: {breakdown.final_score:.2%}")
    print(f"\nScore Breakdown:")
    print(f"  Skill Match: {breakdown.skill_match_score:.2%}")
    print(f"  Experience: {breakdown.experience_score:.2%}")
    print(f"  Education: {breakdown.education_score:.2%}")
    print(f"  Semantic Similarity: {breakdown.semantic_similarity_score:.2%}")
    
    print(f"\nMatched Skills: {', '.join(breakdown.matched_skills)}")
    print(f"Missing Skills: {', '.join(breakdown.missing_skills)}")
    print(f"Experience: {breakdown.experience_years} years (Required: {breakdown.required_experience})")
    print(f"Has Required Degree: {breakdown.has_required_degree}")


def example_2_custom_weights():
    """Example 2: Custom scoring weights"""
    print("\n" + "=" * 80)
    print("Example 2: Custom Scoring Weights")
    print("=" * 80)
    
    resume = {
        "name": "Bob Smith",
        "skills": ["Python", "Django", "PostgreSQL"],
        "experience_years": 3,
        "education": [{"degree": "Bachelor of Science", "year": "2020"}]
    }
    
    job_description = """
    Backend Developer
    Requirements:
    - Python and Django expertise
    - 2+ years experience
    - SQL database knowledge
    """
    
    # Create scorer with custom weights (emphasize skills more)
    scorer = ResumeScorer(
        skill_weight=0.5,      # 50% weight on skills
        experience_weight=0.3,  # 30% on experience
        education_weight=0.1,   # 10% on education
        semantic_weight=0.1     # 10% on semantic similarity
    )
    
    breakdown = scorer.score_resume(resume, job_description)
    
    print(f"\nCandidate: {resume['name']}")
    print(f"Final Score (Custom Weights): {breakdown.final_score:.2%}")
    print(f"\nWeights Used:")
    print(f"  Skills: 50%")
    print(f"  Experience: 30%")
    print(f"  Education: 10%")
    print(f"  Semantic: 10%")


def example_3_batch_scoring():
    """Example 3: Score multiple resumes at once"""
    print("\n" + "=" * 80)
    print("Example 3: Batch Resume Scoring")
    print("=" * 80)
    
    resumes = [
        {
            "name": "Alice Johnson",
            "skills": ["Python", "Machine Learning", "TensorFlow", "AWS"],
            "experience_years": 5,
            "education": [{"degree": "Master"}]
        },
        {
            "name": "Bob Smith",
            "skills": ["Python", "Django", "Docker"],
            "experience_years": 3,
            "education": [{"degree": "Bachelor"}]
        },
        {
            "name": "Carol White",
            "skills": ["Java", "Spring Boot", "MySQL"],
            "experience_years": 4,
            "education": [{"degree": "Bachelor"}]
        },
        {
            "name": "David Lee",
            "skills": ["Python", "Machine Learning", "PyTorch", "GCP"],
            "experience_years": 6,
            "education": [{"degree": "PhD"}]
        }
    ]
    
    job_description = """
    Machine Learning Engineer
    Requirements:
    - Python and ML frameworks (TensorFlow/PyTorch)
    - 3+ years ML experience
    - Master's degree preferred
    - Cloud experience (AWS/GCP)
    """
    
    # Score all resumes
    results = score_resumes_batch(resumes, job_description)
    
    print(f"\nScored {len(results)} candidates:")
    print(f"\n{'Rank':<6}{'Name':<20}{'Score':<10}{'Skills':<10}{'Experience':<12}")
    print("-" * 80)
    
    for idx, (resume, breakdown) in enumerate(results, 1):
        print(f"{idx:<6}{resume['name']:<20}{breakdown.final_score:.2%}    "
              f"{breakdown.skill_match_score:.2%}    {breakdown.experience_score:.2%}")


def example_4_with_embeddings():
    """Example 4: Scoring with embeddings for semantic similarity"""
    print("\n" + "=" * 80)
    print("Example 4: Scoring with Embeddings")
    print("=" * 80)
    
    try:
        # Initialize embeddings manager
        embeddings_manager = EmbeddingsManager(use_pinecone=False)
        
        # Create scorer with embeddings
        scorer = ResumeScorer(embeddings_manager=embeddings_manager)
        
        resume = {
            "name": "Emma Wilson",
            "skills": ["Neural Networks", "Deep Learning", "Computer Vision"],
            "experience_years": 4,
            "education": [{"degree": "Master in AI"}],
            "summary": "Specialized in computer vision and convolutional neural networks"
        }
        
        job_description = """
        Computer Vision Engineer
        
        We're looking for someone to build image recognition systems using
        state-of-the-art deep learning techniques. Experience with CNNs and
        transfer learning is essential.
        """
        
        breakdown = scorer.score_resume(resume, job_description)
        
        print(f"\nCandidate: {resume['name']}")
        print(f"Final Score: {breakdown.final_score:.2%}")
        print(f"Semantic Similarity (using embeddings): {breakdown.semantic_similarity_score:.2%}")
        print("\nNote: Semantic similarity uses sentence-transformers for better matching")
        
    except Exception as e:
        print(f"Could not initialize embeddings: {e}")
        print("Falling back to keyword-based similarity")


def example_5_detailed_analysis():
    """Example 5: Detailed score analysis"""
    print("\n" + "=" * 80)
    print("Example 5: Detailed Score Analysis")
    print("=" * 80)
    
    resume = {
        "name": "Frank Martinez",
        "skills": ["Python", "FastAPI", "Docker", "Kubernetes", "AWS", "MongoDB"],
        "experience_years": 7,
        "education": [
            {"degree": "Bachelor of Computer Science", "year": "2016"},
            {"degree": "Master of Software Engineering", "year": "2018"}
        ],
        "summary": "Full-stack engineer with DevOps expertise and cloud architecture experience"
    }
    
    job_description = """
    Senior Backend Engineer
    
    Requirements:
    - 5+ years backend development
    - Python expertise (FastAPI/Django)
    - Microservices architecture
    - Docker and Kubernetes
    - Cloud platforms (AWS/Azure/GCP)
    - Bachelor's degree minimum
    
    Bonus:
    - NoSQL databases
    - CI/CD experience
    """
    
    scorer = ResumeScorer()
    breakdown = scorer.score_resume(resume, job_description)
    
    print(f"\n{'=' * 60}")
    print(f"DETAILED SCORE ANALYSIS FOR: {resume['name']}")
    print(f"{'=' * 60}")
    
    print(f"\n🎯 FINAL SCORE: {breakdown.final_score:.1%}")
    
    print(f"\n📊 COMPONENT SCORES:")
    print(f"  └─ Skills Match:      {breakdown.skill_match_score:.1%} (weight: 35%)")
    print(f"  └─ Experience Level:  {breakdown.experience_score:.1%} (weight: 25%)")
    print(f"  └─ Education:         {breakdown.education_score:.1%} (weight: 15%)")
    print(f"  └─ Semantic Match:    {breakdown.semantic_similarity_score:.1%} (weight: 25%)")
    
    print(f"\n✅ MATCHED SKILLS ({len(breakdown.matched_skills)}):")
    for skill in breakdown.matched_skills:
        print(f"  • {skill}")
    
    if breakdown.missing_skills:
        print(f"\n❌ MISSING SKILLS ({len(breakdown.missing_skills)}):")
        for skill in breakdown.missing_skills:
            print(f"  • {skill}")
    
    print(f"\n💼 EXPERIENCE:")
    print(f"  Candidate: {breakdown.experience_years} years")
    print(f"  Required:  {breakdown.required_experience} years")
    if breakdown.experience_years >= breakdown.required_experience:
        print(f"  Status: ✅ Exceeds requirement (+{breakdown.experience_years - breakdown.required_experience} years)")
    else:
        print(f"  Status: ⚠️  Below requirement (-{breakdown.required_experience - breakdown.experience_years} years)")
    
    print(f"\n🎓 EDUCATION:")
    print(f"  Has Required Degree: {'✅ Yes' if breakdown.has_required_degree else '❌ No'}")
    print(f"  Degrees: {', '.join([edu['degree'] for edu in resume['education']])}")
    
    # Overall recommendation
    print(f"\n💡 RECOMMENDATION:")
    if breakdown.final_score >= 0.8:
        print("  🌟 STRONG MATCH - Highly recommended for interview")
    elif breakdown.final_score >= 0.6:
        print("  👍 GOOD MATCH - Recommended for consideration")
    elif breakdown.final_score >= 0.4:
        print("  🤔 MODERATE MATCH - Review carefully")
    else:
        print("  ❌ WEAK MATCH - May not be suitable")


def example_6_export_results():
    """Example 6: Export scoring results"""
    print("\n" + "=" * 80)
    print("Example 6: Export Scoring Results")
    print("=" * 80)
    
    resume = {
        "name": "Grace Chen",
        "skills": ["JavaScript", "React", "Node.js", "TypeScript"],
        "experience_years": 4,
        "education": [{"degree": "Bachelor"}]
    }
    
    job_description = "Frontend developer with React and TypeScript needed"
    
    breakdown = score_resume(resume, job_description)
    
    # Convert to dictionary for export
    result_dict = breakdown.to_dict()
    
    print("\nExporting results as dictionary:")
    print("-" * 40)
    
    import json
    print(json.dumps(result_dict, indent=2))
    
    print("\nThis format can be:")
    print("  • Saved to JSON file")
    print("  • Stored in database")
    print("  • Sent via API")
    print("  • Used for reporting")


def example_7_compare_candidates():
    """Example 7: Compare multiple candidates side-by-side"""
    print("\n" + "=" * 80)
    print("Example 7: Side-by-Side Candidate Comparison")
    print("=" * 80)
    
    candidates = [
        {
            "name": "Candidate A",
            "skills": ["Python", "Django", "PostgreSQL", "Docker"],
            "experience_years": 5,
            "education": [{"degree": "Master"}]
        },
        {
            "name": "Candidate B",
            "skills": ["Python", "Flask", "MongoDB", "AWS"],
            "experience_years": 3,
            "education": [{"degree": "Bachelor"}]
        },
        {
            "name": "Candidate C",
            "skills": ["Python", "FastAPI", "PostgreSQL", "AWS", "Docker"],
            "experience_years": 6,
            "education": [{"degree": "Master"}]
        }
    ]
    
    job_description = """
    Python Backend Developer
    - Python expertise required
    - 4+ years experience
    - SQL database knowledge
    - Master's degree preferred
    - Docker and AWS experience
    """
    
    results = score_resumes_batch(candidates, job_description)
    
    print("\n" + "=" * 100)
    print(f"{'Metric':<25} {'Candidate A':<25} {'Candidate B':<25} {'Candidate C':<25}")
    print("=" * 100)
    
    # Extract scores for each candidate
    scores = [breakdown for _, breakdown in results]
    
    metrics = [
        ("Overall Score", "final_score"),
        ("Skills Match", "skill_match_score"),
        ("Experience", "experience_score"),
        ("Education", "education_score"),
        ("Semantic Match", "semantic_similarity_score")
    ]
    
    for metric_name, metric_attr in metrics:
        values = [getattr(s, metric_attr) for s in scores]
        print(f"{metric_name:<25} {values[0]:.1%}{'':18} {values[1]:.1%}{'':18} {values[2]:.1%}")
    
    print("=" * 100)
    
    best_idx = 0
    best_score = scores[0].final_score
    for idx, score in enumerate(scores[1:], 1):
        if score.final_score > best_score:
            best_score = score.final_score
            best_idx = idx
    
    print(f"\n🏆 WINNER: {candidates[best_idx]['name']} with {best_score:.1%} match")


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_basic_scoring,
        example_2_custom_weights,
        example_3_batch_scoring,
        example_4_with_embeddings,
        example_5_detailed_analysis,
        example_6_export_results,
        example_7_compare_candidates
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    run_all_examples()
