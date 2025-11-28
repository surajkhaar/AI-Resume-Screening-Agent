"""
Example: Testing the Enhanced Streamlit UI Features
Demonstrates scoring, explanations, CSV export, and Supabase integration
"""

import json
from scoring import ResumeScorer, explain_match
from embeddings import EmbeddingsManager
from supabase_client import SupabaseManager, check_supabase_connection
import pandas as pd
from datetime import datetime


def example_1_basic_analysis():
    """Example 1: Basic analysis with all features"""
    print("\n" + "="*80)
    print("Example 1: Basic Resume Analysis with Enhanced Features")
    print("="*80)
    
    # Sample resume data
    resume = {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@email.com",
        "phone": "+1-555-0123",
        "experience_years": 7,
        "skills": ["Python", "Machine Learning", "TensorFlow", "AWS", "Docker"],
        "education": [
            {"degree": "Master of Science in Computer Science", "year": "2017"}
        ],
        "summary": "Experienced ML engineer with 7 years in production systems"
    }
    
    # Job description
    job_description = """
    Senior Machine Learning Engineer
    
    Requirements:
    - 5+ years of experience in machine learning
    - Strong Python programming skills
    - Experience with TensorFlow or PyTorch
    - Cloud platform experience (AWS, GCP, or Azure)
    - Master's degree in Computer Science or related field preferred
    
    Responsibilities:
    - Design and implement ML models for production
    - Optimize model performance and scalability
    - Collaborate with cross-functional teams
    """
    
    # Initialize components
    print("\n1. Initializing components...")
    embeddings_manager = EmbeddingsManager()
    scorer = ResumeScorer(embeddings_manager=embeddings_manager)
    
    # Score the resume
    print("\n2. Calculating scores...")
    breakdown = scorer.score_resume(resume, job_description)
    
    print(f"\n📊 Score Breakdown:")
    print(f"   Overall Score: {breakdown.final_score:.1%}")
    print(f"   - Skills Match: {breakdown.skill_match_score:.1%} (weight: 35%)")
    print(f"   - Experience: {breakdown.experience_score:.1%} (weight: 25%)")
    print(f"   - Education: {breakdown.education_score:.1%} (weight: 15%)")
    print(f"   - Semantic: {breakdown.semantic_similarity_score:.1%} (weight: 25%)")
    
    # Generate AI explanation
    print("\n3. Generating AI explanation...")
    try:
        explanation = explain_match(
            resume_data=resume,
            job_description=job_description,
            score_breakdown=breakdown
        )
        
        print(f"\n🤖 AI Explanation:")
        print(f"\nSummary:\n{explanation.summary}")
        print(f"\nTop 3 Reasons:")
        for i, reason in enumerate(explanation.top_reasons, 1):
            print(f"  {i}. {reason}")
        print(f"\nRecommendation: {explanation.recommendation}")
    except Exception as e:
        print(f"\n⚠️  Could not generate explanation: {e}")
        explanation = None
    
    # Create CSV export data
    print("\n4. Creating CSV export...")
    export_data = [{
        "Rank": 1,
        "Name": resume.get("name"),
        "Email": resume.get("email"),
        "Phone": resume.get("phone"),
        "Final Score": f"{breakdown.final_score:.2%}",
        "Skills Match": f"{breakdown.skill_match_score:.2%}",
        "Experience Match": f"{breakdown.experience_score:.2%}",
        "Education Match": f"{breakdown.education_score:.2%}",
        "Semantic Match": f"{breakdown.semantic_similarity_score:.2%}",
        "Experience Years": breakdown.experience_years,
        "Matched Skills": ", ".join(breakdown.matched_skills),
        "Missing Skills": ", ".join(breakdown.missing_skills),
        "Recommendation": explanation.recommendation if explanation else "N/A"
    }]
    
    df = pd.DataFrame(export_data)
    csv_filename = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"   ✅ Exported to: {csv_filename}")
    
    # Try Supabase integration
    print("\n5. Testing Supabase integration...")
    if check_supabase_connection():
        try:
            manager = SupabaseManager()
            record = manager.store_analysis(
                job_description=job_description,
                resume_data=resume,
                score_breakdown=breakdown.to_dict(),
                explanation=explanation.to_dict() if explanation else None
            )
            print(f"   ✅ Stored in database with ID: {record.get('id')}")
        except Exception as e:
            print(f"   ⚠️  Database storage failed: {e}")
    else:
        print("   ℹ️  Supabase not configured (set SUPABASE_URL and SUPABASE_KEY)")


def example_2_batch_analysis():
    """Example 2: Batch analysis with multiple candidates"""
    print("\n" + "="*80)
    print("Example 2: Batch Analysis with Multiple Candidates")
    print("="*80)
    
    # Multiple resumes
    resumes = [
        {
            "name": "Alice Chen",
            "email": "alice@email.com",
            "experience_years": 8,
            "skills": ["Python", "PyTorch", "Kubernetes", "GCP"],
            "education": [{"degree": "PhD in Computer Science", "year": "2016"}]
        },
        {
            "name": "Bob Smith",
            "email": "bob@email.com",
            "experience_years": 4,
            "skills": ["Java", "Spring Boot", "MySQL"],
            "education": [{"degree": "Bachelor in Software Engineering", "year": "2019"}]
        },
        {
            "name": "Carol Williams",
            "email": "carol@email.com",
            "experience_years": 6,
            "skills": ["Python", "TensorFlow", "AWS", "MLOps"],
            "education": [{"degree": "Master of Science in AI", "year": "2018"}]
        }
    ]
    
    job_description = """
    Machine Learning Engineer
    Requirements: 5+ years, Python, TensorFlow/PyTorch, Cloud experience
    Master's degree preferred
    """
    
    # Initialize
    print("\nInitializing scorer...")
    embeddings_manager = EmbeddingsManager()
    scorer = ResumeScorer(embeddings_manager=embeddings_manager)
    
    # Batch score
    print("\nScoring all candidates...")
    scored_results = scorer.batch_score_resumes(resumes, job_description)
    
    # Display results
    print(f"\n🏆 Ranked Results:")
    print("-" * 80)
    
    results_with_explanations = []
    for rank, (resume, breakdown) in enumerate(scored_results, 1):
        name = resume.get("name", "Unknown")
        score = breakdown.final_score
        
        # Visual score bar
        bar_length = 50
        filled = int(score * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        if score >= 0.8:
            emoji = "🌟"
        elif score >= 0.6:
            emoji = "👍"
        elif score >= 0.4:
            emoji = "🤔"
        else:
            emoji = "❌"
        
        print(f"\n#{rank} {emoji} {name}")
        print(f"    Score: [{bar}] {score:.1%}")
        print(f"    Skills: {breakdown.skill_match_score:.1%} | "
              f"Exp: {breakdown.experience_score:.1%} | "
              f"Edu: {breakdown.education_score:.1%} | "
              f"Semantic: {breakdown.semantic_similarity_score:.1%}")
        print(f"    Matched Skills: {', '.join(breakdown.matched_skills[:3])}")
        
        # Generate explanation
        try:
            explanation = explain_match(resume, job_description, breakdown)
            print(f"    Recommendation: {explanation.recommendation}")
            results_with_explanations.append((resume, breakdown, explanation))
        except Exception as e:
            print(f"    ⚠️  No explanation available")
            results_with_explanations.append((resume, breakdown, None))
    
    # Export to CSV
    print("\n\nExporting to CSV...")
    export_data = []
    for resume, breakdown, explanation in results_with_explanations:
        export_data.append({
            "Name": resume.get("name"),
            "Score": f"{breakdown.final_score:.2%}",
            "Skills": f"{breakdown.skill_match_score:.2%}",
            "Experience": f"{breakdown.experience_score:.2%}",
            "Recommendation": explanation.recommendation if explanation else "N/A"
        })
    
    df = pd.DataFrame(export_data)
    filename = f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Exported {len(export_data)} candidates to: {filename}")
    
    # Statistics
    print("\n📊 Summary Statistics:")
    avg_score = sum(b.final_score for _, b, _ in results_with_explanations) / len(results_with_explanations)
    strong = sum(1 for _, b, _ in results_with_explanations if b.final_score >= 0.8)
    print(f"   Total Candidates: {len(results_with_explanations)}")
    print(f"   Average Score: {avg_score:.1%}")
    print(f"   Strong Matches (≥80%): {strong}")


def example_3_supabase_queries():
    """Example 3: Querying Supabase database"""
    print("\n" + "="*80)
    print("Example 3: Supabase Database Queries")
    print("="*80)
    
    if not check_supabase_connection():
        print("\n⚠️  Supabase not configured. Set environment variables:")
        print("   export SUPABASE_URL='https://your-project.supabase.co'")
        print("   export SUPABASE_KEY='your-anon-key'")
        return
    
    try:
        manager = SupabaseManager()
        
        # Get recent analyses
        print("\n1. Recent Analyses (last 5):")
        recent = manager.get_recent_analyses(limit=5)
        if recent:
            for record in recent:
                print(f"   - {record['candidate_name']}: {record['final_score']:.1%} "
                      f"({record['timestamp']})")
        else:
            print("   No analyses found")
        
        # Get statistics
        print("\n2. Database Statistics:")
        stats = manager.get_statistics()
        print(f"   Total Analyses: {stats.get('total_analyses', 0)}")
        print(f"   Average Score: {stats.get('average_score', 0):.1%}")
        print(f"   Strong Matches: {stats.get('strong_matches', 0)}")
        print(f"   Good Matches: {stats.get('good_matches', 0)}")
        print(f"   Moderate Matches: {stats.get('moderate_matches', 0)}")
        print(f"   Weak Matches: {stats.get('weak_matches', 0)}")
        
        # Get top performers
        print("\n3. Top Performers (score ≥ 0.8):")
        top = manager.get_analyses_by_score_range(min_score=0.8)
        if top:
            for record in top[:5]:
                print(f"   🌟 {record['candidate_name']}: {record['final_score']:.1%}")
                if record.get('explanation_recommendation'):
                    print(f"      {record['explanation_recommendation']}")
        else:
            print("   No strong matches found")
        
    except Exception as e:
        print(f"\n❌ Error querying database: {e}")


def example_4_visualization_data():
    """Example 4: Prepare data for visualization"""
    print("\n" + "="*80)
    print("Example 4: Visualization Data Preparation")
    print("="*80)
    
    # Sample scored results
    sample_data = [
        {"name": "Candidate A", "score": 0.87, "skills": 0.95, "exp": 0.80, "edu": 0.85, "sem": 0.88},
        {"name": "Candidate B", "score": 0.72, "skills": 0.70, "exp": 0.75, "edu": 0.70, "sem": 0.73},
        {"name": "Candidate C", "score": 0.45, "skills": 0.50, "exp": 0.40, "edu": 0.45, "sem": 0.43},
    ]
    
    print("\nScore Bar Visualization (HTML/CSS):")
    print("-" * 80)
    
    for data in sample_data:
        score_pct = data["score"] * 100
        
        # Determine color class
        if score_pct >= 80:
            color_class = "excellent"
            color = "\033[92m"  # Green
        elif score_pct >= 60:
            color_class = "good"
            color = "\033[94m"  # Blue
        elif score_pct >= 40:
            color_class = "moderate"
            color = "\033[93m"  # Yellow
        else:
            color_class = "weak"
            color = "\033[91m"  # Red
        reset = "\033[0m"
        
        print(f"\n{data['name']}:")
        print(f'{color}{"█" * int(score_pct/2)}{reset}{"░" * int((100-score_pct)/2)} {score_pct:.1f}%')
        print(f"  Skills:   {data['skills']:.1%}")
        print(f"  Exp:      {data['exp']:.1%}")
        print(f"  Edu:      {data['edu']:.1%}")
        print(f"  Semantic: {data['sem']:.1%}")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("ENHANCED STREAMLIT UI FEATURES - TEST EXAMPLES")
    print("="*80)
    print("\nThis script demonstrates all enhanced features:")
    print("  1. Visual score bars and progress indicators")
    print("  2. AI-powered explanations")
    print("  3. CSV export functionality")
    print("  4. Supabase database integration")
    print("  5. Enhanced ranking display")
    
    # Run examples
    try:
        example_1_basic_analysis()
    except Exception as e:
        print(f"\n❌ Example 1 failed: {e}")
    
    try:
        example_2_batch_analysis()
    except Exception as e:
        print(f"\n❌ Example 2 failed: {e}")
    
    try:
        example_3_supabase_queries()
    except Exception as e:
        print(f"\n❌ Example 3 failed: {e}")
    
    try:
        example_4_visualization_data()
    except Exception as e:
        print(f"\n❌ Example 4 failed: {e}")
    
    print("\n" + "="*80)
    print("✅ Test Examples Complete!")
    print("="*80)
    print("\nTo see these features in the UI, run:")
    print("  streamlit run app.py")


if __name__ == "__main__":
    main()
