"""
Example usage of the explainability feature

This demonstrates how to use the explain_match function to generate
AI-powered explanations for candidate matches.
"""

import os
from scoring import ResumeScorer, explain_match, score_resume


def example_1_basic_explanation():
    """Example 1: Basic explanation for a strong match"""
    print("=" * 80)
    print("Example 1: Strong Match Explanation")
    print("=" * 80)
    
    resume = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "skills": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "AWS", "Docker"],
        "experience_years": 6,
        "education": [
            {"degree": "Master of Science in Computer Science", "year": "2019"}
        ],
        "summary": "Senior ML engineer with 6 years building production ML systems"
    }
    
    job_description = """
    Senior Machine Learning Engineer
    
    Requirements:
    - 5+ years of experience in machine learning
    - Strong Python programming skills
    - Experience with TensorFlow or PyTorch
    - AWS cloud platform knowledge
    - Master's degree in Computer Science or related field
    - Docker and Kubernetes experience preferred
    
    Responsibilities:
    - Design and implement ML models
    - Deploy models to production environments
    - Mentor junior engineers
    """
    
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Set it to see AI-generated explanations.")
        print("   For now, showing fallback explanation...")
    
    try:
        # Generate explanation
        explanation = explain_match(resume, job_description)
        
        print(f"\n✨ AI EXPLANATION FOR: {resume['name']}")
        print("=" * 80)
        
        print(f"\n📝 SUMMARY:")
        print(f"{explanation.summary}")
        
        print(f"\n🎯 TOP 3 REASONS:")
        for i, reason in enumerate(explanation.top_reasons, 1):
            print(f"{i}. {reason}")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"{explanation.recommendation}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_2_weak_match_explanation():
    """Example 2: Explanation for a weak match"""
    print("\n" + "=" * 80)
    print("Example 2: Weak Match Explanation")
    print("=" * 80)
    
    resume = {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "skills": ["JavaScript", "React", "Node.js", "HTML", "CSS"],
        "experience_years": 3,
        "education": [
            {"degree": "Bachelor of Arts in Design", "year": "2020"}
        ],
        "summary": "Frontend developer with passion for UI/UX"
    }
    
    job_description = """
    Senior Machine Learning Engineer
    
    Requirements:
    - 5+ years of experience in machine learning
    - Strong Python programming skills
    - Experience with TensorFlow or PyTorch
    - Master's degree in Computer Science required
    """
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Showing fallback explanation...")
    
    try:
        explanation = explain_match(resume, job_description)
        
        print(f"\n✨ AI EXPLANATION FOR: {resume['name']}")
        print("=" * 80)
        
        print(f"\n📝 SUMMARY:")
        print(f"{explanation.summary}")
        
        print(f"\n🎯 TOP 3 REASONS:")
        for i, reason in enumerate(explanation.top_reasons, 1):
            print(f"{i}. {reason}")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"{explanation.recommendation}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_3_with_pre_computed_score():
    """Example 3: Using pre-computed score breakdown"""
    print("\n" + "=" * 80)
    print("Example 3: Explanation with Pre-Computed Score")
    print("=" * 80)
    
    resume = {
        "name": "Carol White",
        "email": "carol@example.com",
        "skills": ["Python", "Machine Learning", "scikit-learn", "Pandas", "Docker"],
        "experience_years": 4,
        "education": [
            {"degree": "Master of Data Science", "year": "2021"}
        ],
        "summary": "Data scientist with ML model deployment experience"
    }
    
    job_description = """
    Machine Learning Engineer
    
    Requirements:
    - 5+ years in machine learning
    - Python, TensorFlow/PyTorch
    - Master's degree preferred
    - Cloud experience (AWS/GCP)
    """
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set.")
    
    try:
        # First, compute the score
        print("\n📊 Computing score breakdown first...")
        breakdown = score_resume(resume, job_description)
        
        print(f"Final Score: {breakdown.final_score:.1%}")
        print(f"Matched Skills: {', '.join(breakdown.matched_skills)}")
        print(f"Missing Skills: {', '.join(breakdown.missing_skills)}")
        
        # Then generate explanation using the score
        print("\n📝 Generating AI explanation...")
        scorer = ResumeScorer()
        explanation = scorer.explain_match(
            resume,
            job_description,
            score_breakdown=breakdown  # Pass pre-computed score
        )
        
        print(f"\n✨ AI EXPLANATION FOR: {resume['name']}")
        print("=" * 80)
        
        print(f"\n📝 SUMMARY:")
        print(f"{explanation.summary}")
        
        print(f"\n🎯 TOP 3 REASONS:")
        for i, reason in enumerate(explanation.top_reasons, 1):
            print(f"{i}. {reason}")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"{explanation.recommendation}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_4_batch_with_explanations():
    """Example 4: Generate explanations for multiple candidates"""
    print("\n" + "=" * 80)
    print("Example 4: Batch Explanations for Multiple Candidates")
    print("=" * 80)
    
    candidates = [
        {
            "name": "David Lee",
            "skills": ["Python", "TensorFlow", "Keras", "AWS", "Docker"],
            "experience_years": 7,
            "education": [{"degree": "PhD in Machine Learning", "year": "2018"}]
        },
        {
            "name": "Emma Wilson",
            "skills": ["Python", "scikit-learn", "SQL", "Tableau"],
            "experience_years": 3,
            "education": [{"degree": "Master of Statistics", "year": "2021"}]
        },
        {
            "name": "Frank Martinez",
            "skills": ["Python", "PyTorch", "Computer Vision", "Docker", "Kubernetes"],
            "experience_years": 5,
            "education": [{"degree": "Master of Computer Science", "year": "2020"}]
        }
    ]
    
    job_description = """
    Senior ML Engineer - Computer Vision
    
    Requirements:
    - 5+ years ML/AI experience
    - Deep learning (TensorFlow/PyTorch)
    - Computer vision expertise
    - Master's degree required
    - Cloud deployment (AWS/GCP)
    """
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Set it to see AI explanations.")
        return
    
    try:
        scorer = ResumeScorer()
        
        print(f"\n📊 Analyzing {len(candidates)} candidates...\n")
        
        for i, resume in enumerate(candidates, 1):
            print(f"\n{'='*80}")
            print(f"CANDIDATE #{i}: {resume['name']}")
            print('='*80)
            
            # Score first
            breakdown = scorer.score_resume(resume, job_description)
            print(f"\n⭐ Final Score: {breakdown.final_score:.1%}")
            
            # Generate explanation
            explanation = scorer.explain_match(resume, job_description, breakdown)
            
            print(f"\n📝 Summary:")
            print(f"{explanation.summary}")
            
            print(f"\n🎯 Top 3 Reasons:")
            for j, reason in enumerate(explanation.top_reasons, 1):
                print(f"{j}. {reason}")
            
            print(f"\n💡 Recommendation: {explanation.recommendation}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_5_comparison_with_and_without_ai():
    """Example 5: Compare standard scores with AI explanations"""
    print("\n" + "=" * 80)
    print("Example 5: Score Breakdown vs AI Explanation")
    print("=" * 80)
    
    resume = {
        "name": "Grace Chen",
        "skills": ["Python", "Deep Learning", "PyTorch", "MLflow", "Docker"],
        "experience_years": 5,
        "education": [
            {"degree": "Master of AI and Robotics", "year": "2020"}
        ],
        "summary": "ML engineer specializing in deep learning for NLP applications"
    }
    
    job_description = """
    Machine Learning Engineer - NLP Focus
    
    Requirements:
    - 5+ years in ML/AI
    - Deep learning frameworks (PyTorch/TensorFlow)
    - NLP experience required
    - Master's degree in CS or related field
    - MLOps tools (MLflow, Kubeflow)
    """
    
    try:
        scorer = ResumeScorer()
        
        # Standard score breakdown
        print("\n📊 STANDARD SCORE BREAKDOWN")
        print("-" * 80)
        breakdown = scorer.score_resume(resume, job_description)
        
        print(f"Final Score: {breakdown.final_score:.1%}")
        print(f"\nComponent Scores:")
        print(f"  • Skills Match: {breakdown.skill_match_score:.1%}")
        print(f"  • Experience: {breakdown.experience_score:.1%}")
        print(f"  • Education: {breakdown.education_score:.1%}")
        print(f"  • Semantic: {breakdown.semantic_similarity_score:.1%}")
        
        print(f"\nMatched Skills: {', '.join(breakdown.matched_skills)}")
        print(f"Missing Skills: {', '.join(breakdown.missing_skills)}")
        
        # AI explanation
        if os.getenv("OPENAI_API_KEY"):
            print("\n" + "=" * 80)
            print("✨ AI-POWERED EXPLANATION")
            print("-" * 80)
            
            explanation = scorer.explain_match(resume, job_description, breakdown)
            
            print(f"\nSummary:")
            print(f"{explanation.summary}")
            
            print(f"\nTop 3 Reasons:")
            for i, reason in enumerate(explanation.top_reasons, 1):
                print(f"{i}. {reason}")
            
            print(f"\nRecommendation: {explanation.recommendation}")
            
            print("\n" + "=" * 80)
            print("💡 KEY DIFFERENCE:")
            print("Standard scores give you numbers.")
            print("AI explanation gives you actionable insights and context!")
        else:
            print("\n⚠️  Set OPENAI_API_KEY to see AI explanation comparison")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_6_custom_api_key():
    """Example 6: Using custom API key"""
    print("\n" + "=" * 80)
    print("Example 6: Using Custom API Key")
    print("=" * 80)
    
    resume = {
        "name": "Henry Zhang",
        "skills": ["Python", "TensorFlow", "Computer Vision", "AWS"],
        "experience_years": 6,
        "education": [{"degree": "Master of CS", "year": "2019"}]
    }
    
    job_description = "Senior CV Engineer, 5+ years, Python, TensorFlow, Master's required"
    
    print("\n📝 You can pass API key directly:")
    print("   explanation = explain_match(resume, jd, api_key='your-key')")
    print("\nOr use environment variable:")
    print("   export OPENAI_API_KEY='your-key'")
    print("   explanation = explain_match(resume, jd)")
    
    # Example with custom key (won't actually call API without valid key)
    print("\n⚠️  Example code structure:")
    print("""
    try:
        explanation = explain_match(
            resume,
            job_description,
            api_key="sk-your-actual-api-key-here"
        )
        print(explanation.summary)
        print(explanation.top_reasons)
        print(explanation.recommendation)
    except Exception as e:
        print(f"Error: {e}")
    """)


def example_7_export_explanation():
    """Example 7: Export explanation to JSON"""
    print("\n" + "=" * 80)
    print("Example 7: Export Explanation to JSON")
    print("=" * 80)
    
    resume = {
        "name": "Iris Patel",
        "skills": ["Python", "Spark", "Hadoop", "SQL", "AWS"],
        "experience_years": 5,
        "education": [{"degree": "Master of Data Engineering", "year": "2020"}]
    }
    
    job_description = "Big Data Engineer, 5+ years, Spark, Hadoop, Cloud experience"
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set.")
        return
    
    try:
        import json
        
        # Generate explanation
        explanation = explain_match(resume, job_description)
        
        # Convert to dictionary
        explanation_dict = explanation.to_dict()
        
        print("\n📄 Explanation as JSON:")
        print(json.dumps(explanation_dict, indent=2))
        
        print("\n💾 This can be:")
        print("  • Saved to a file")
        print("  • Sent via API")
        print("  • Stored in database")
        print("  • Included in reports")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def run_all_examples():
    """Run all examples"""
    print("\n" + "🎯" * 40)
    print("EXPLAINABILITY FEATURE EXAMPLES")
    print("🎯" * 40)
    
    print("\n💡 TIP: Set OPENAI_API_KEY environment variable to see real AI explanations")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    
    examples = [
        example_1_basic_explanation,
        example_2_weak_match_explanation,
        example_3_with_pre_computed_score,
        example_4_batch_with_explanations,
        example_5_comparison_with_and_without_ai,
        example_6_custom_api_key,
        example_7_export_explanation
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("✅ All examples completed!")
    print("=" * 80)
    
    print("\n📚 Key Takeaways:")
    print("  1. explain_match() generates human-readable explanations")
    print("  2. Uses GPT-4 with few-shot examples for consistency")
    print("  3. Returns summary (≤120 words) + top 3 reasons")
    print("  4. Provides actionable recommendations")
    print("  5. Falls back gracefully if OpenAI unavailable")
    print("  6. Can use pre-computed scores for efficiency")
    print("  7. Easy to export as JSON for integration")


if __name__ == "__main__":
    run_all_examples()
