"""
Example Usage: Bias Detection Module
Demonstrates how to use the bias detection functionality
"""

from bias_detection import BiasDetector, generate_bias_report
import json


def example_1_clean_data():
    """Example 1: Clean data with no bias concerns"""
    print("\n" + "="*80)
    print("Example 1: Clean Data (No Bias Concerns)")
    print("="*80)
    
    resumes = [
        {
            "name": "Alice Chen",
            "email": "alice@email.com",
            "phone": "+1-555-0001",
            "skills": ["Python", "Machine Learning", "TensorFlow", "AWS"],
            "experience_years": 6,
            "education": [{"degree": "Master of Science in Computer Science", "year": "2018"}]
        },
        {
            "name": "Bob Martinez",
            "email": "bob@company.com",
            "phone": "+1-555-0002",
            "skills": ["Java", "Spring Boot", "Kubernetes", "Docker"],
            "experience_years": 5,
            "education": [{"degree": "Bachelor of Science in Software Engineering", "year": "2019"}]
        },
        {
            "name": "Carol Nakamura",
            "email": "carol@example.com",
            "phone": "+1-555-0003",
            "skills": ["Python", "Django", "PostgreSQL", "Redis"],
            "experience_years": 7,
            "education": [{"degree": "PhD in Computer Science", "year": "2016"}]
        }
    ]
    
    report = generate_bias_report(resumes)
    
    print(f"\n{report.summary}\n")
    
    if report.flags:
        print("Flags detected:")
        for flag in report.flags:
            print(f"  [{flag.severity.upper()}] {flag.message}")
    else:
        print("✅ No bias concerns detected!")


def example_2_missing_fields():
    """Example 2: Detect missing critical fields"""
    print("\n" + "="*80)
    print("Example 2: Missing Critical Fields")
    print("="*80)
    
    resumes = [
        {
            "name": "Alice Johnson",
            "email": "alice@email.com",
            "skills": ["Python", "Java"],
            "experience_years": 5
        },
        {
            "name": "Bob Smith",
            # Missing email
            "skills": ["JavaScript"],
            "experience_years": 4
        },
        {
            "name": "Carol Williams",
            "email": "carol@email.com",
            # Missing skills
            "experience_years": 6
        },
        {
            "name": "David Lee",
            # Missing email and skills
            "experience_years": 3
        }
    ]
    
    report = generate_bias_report(resumes)
    
    print(f"\n{report.summary}\n")
    print(f"Critical flags: {len(report.get_flags_by_severity('critical'))}")
    print(f"Warning flags: {len(report.get_flags_by_severity('warning'))}")
    print(f"Info flags: {len(report.get_flags_by_severity('info'))}\n")
    
    for flag in report.flags:
        print(f"\n[{flag.severity.upper()}] {flag.message}")
        print(f"Category: {flag.category}")
        print(f"Recommendation: {flag.recommendation}")
        if flag.affected_candidates:
            print(f"Affected: {', '.join(flag.affected_candidates[:5])}")
        print(f"Details: {flag.details}")


def example_3_experience_variance():
    """Example 3: Detect extreme experience variance"""
    print("\n" + "="*80)
    print("Example 3: Extreme Experience Variance")
    print("="*80)
    
    resumes = [
        {"name": "Entry Level", "skills": ["Python"], "experience_years": 0},
        {"name": "Junior", "skills": ["Python"], "experience_years": 2},
        {"name": "Mid Level", "skills": ["Python"], "experience_years": 5},
        {"name": "Senior", "skills": ["Python"], "experience_years": 10},
        {"name": "Principal", "skills": ["Python"], "experience_years": 20},
        {"name": "VP Engineering", "skills": ["Python"], "experience_years": 30},
    ]
    
    report = generate_bias_report(resumes)
    
    print(f"\n{report.summary}\n")
    
    variance_flags = [f for f in report.flags if f.category == "variance"]
    
    if variance_flags:
        for flag in variance_flags:
            print(f"⚠️  {flag.message}")
            print(f"\nDetails:")
            for key, value in flag.details.items():
                print(f"  {key}: {value}")
            print(f"\nRecommendation: {flag.recommendation}")
    else:
        print("No variance issues detected")


def example_4_education_patterns():
    """Example 4: Detect education distribution issues"""
    print("\n" + "="*80)
    print("Example 4: Education Distribution Patterns")
    print("="*80)
    
    # Scenario A: Missing education data
    print("\nScenario A: High rate of missing education")
    resumes_a = [
        {"name": f"Candidate {i}", "skills": ["Python"], "experience_years": 5}
        for i in range(10)
    ]
    
    report_a = generate_bias_report(resumes_a)
    education_flags = [f for f in report_a.flags if "education" in f.message.lower()]
    
    if education_flags:
        for flag in education_flags:
            print(f"  ⚠️  {flag.message}")
            print(f"  Rate: {flag.details.get('missing_rate', 0):.1%}")
    
    # Scenario B: Heavily skewed distribution
    print("\nScenario B: Heavily skewed distribution (all PhDs)")
    resumes_b = [
        {
            "name": f"PhD Candidate {i}",
            "skills": ["Python"],
            "experience_years": 10,
            "education": [{"degree": "PhD in Computer Science", "year": "2015"}]
        }
        for i in range(10)
    ]
    
    report_b = generate_bias_report(resumes_b)
    pattern_flags = [f for f in report_b.flags if f.category == "pattern" and "education" in f.message.lower()]
    
    if pattern_flags:
        for flag in pattern_flags:
            print(f"  ℹ️  {flag.message}")
            print(f"  Distribution: {flag.details.get('distribution', {})}")


def example_5_skill_diversity():
    """Example 5: Detect low skill diversity"""
    print("\n" + "="*80)
    print("Example 5: Low Skill Diversity")
    print("="*80)
    
    resumes = [
        {"name": "Alice", "skills": ["Python"], "experience_years": 5},
        {"name": "Bob", "skills": ["Java"], "experience_years": 4},
        {"name": "Carol", "skills": [], "experience_years": 6},
        {"name": "David", "skills": ["C++"], "experience_years": 3},
        {"name": "Eve", "skills": [], "experience_years": 7},
    ]
    
    report = generate_bias_report(resumes)
    
    skill_flags = [f for f in report.flags if "skill" in f.message.lower()]
    
    if skill_flags:
        print("\nSkill-related flags:")
        for flag in skill_flags:
            print(f"\n[{flag.severity.upper()}] {flag.message}")
            print(f"Avg skills per candidate: {flag.details.get('avg_skills_per_candidate', 0):.1f}")
            print(f"Total unique skills: {flag.details.get('total_unique_skills', 0)}")
            print(f"Recommendation: {flag.recommendation}")


def example_6_scoring_patterns():
    """Example 6: Detect suspicious scoring patterns"""
    print("\n" + "="*80)
    print("Example 6: Scoring Pattern Analysis")
    print("="*80)
    
    resumes = [
        {"name": f"Candidate {i}", "skills": ["Python", "Java"], "experience_years": 5}
        for i in range(10)
    ]
    
    # Scenario A: Score clustering
    print("\nScenario A: Narrow score distribution (clustering)")
    score_breakdowns_a = [{"final_score": 0.75 + i * 0.01} for i in range(10)]
    
    report_a = generate_bias_report(resumes, score_breakdowns_a)
    cluster_flags = [f for f in report_a.flags if "cluster" in f.message.lower()]
    
    if cluster_flags:
        for flag in cluster_flags:
            print(f"  ⚠️  {flag.message}")
            print(f"  Score range: {flag.details.get('score_range', 0):.3f}")
            print(f"  Min: {flag.details.get('min_score', 0):.3f}, Max: {flag.details.get('max_score', 0):.3f}")
    
    # Scenario B: Too many perfect scores
    print("\nScenario B: High rate of perfect scores")
    score_breakdowns_b = [
        {"final_score": 0.99 if i < 8 else 0.70}
        for i in range(10)
    ]
    
    report_b = generate_bias_report(resumes, score_breakdowns_b)
    perfect_flags = [f for f in report_b.flags if "perfect" in f.message.lower()]
    
    if perfect_flags:
        for flag in perfect_flags:
            print(f"  ℹ️  {flag.message}")
            print(f"  Perfect score rate: {flag.details.get('perfect_score_rate', 0):.1%}")


def example_7_duplicate_detection():
    """Example 7: Detect duplicate candidates"""
    print("\n" + "="*80)
    print("Example 7: Duplicate Candidate Detection")
    print("="*80)
    
    resumes = [
        {"name": "Alice Johnson", "email": "alice@email.com", "skills": ["Python"], "experience_years": 5},
        {"name": "Alice Johnson", "email": "alice.j@email.com", "skills": ["Java"], "experience_years": 5},
        {"name": "Bob Smith", "email": "bob@company.com", "skills": ["C++"], "experience_years": 4},
        {"name": "Bob Smith", "email": "bob.smith@company.com", "skills": ["Python"], "experience_years": 4},
        {"name": "Carol Williams", "email": "carol@example.com", "skills": ["JavaScript"], "experience_years": 6},
    ]
    
    report = generate_bias_report(resumes)
    
    duplicate_flags = [f for f in report.flags if f.category == "consistency" and "duplicate" in f.message.lower()]
    
    if duplicate_flags:
        print("\nDuplicate candidates detected:")
        for flag in duplicate_flags:
            print(f"\n⚠️  {flag.message}")
            print(f"Duplicates found: {flag.details.get('duplicates', {})}")
            print(f"Recommendation: {flag.recommendation}")


def example_8_comprehensive_report():
    """Example 8: Generate comprehensive report with multiple issues"""
    print("\n" + "="*80)
    print("Example 8: Comprehensive Report (Multiple Issues)")
    print("="*80)
    
    resumes = [
        {"name": "Alice", "skills": ["Python"], "experience_years": 1},
        {"name": "Bob", "experience_years": 5},  # Missing skills
        {"name": "Carol", "skills": ["Java"], "experience_years": 20},  # High experience
        {"name": "Alice", "skills": ["C++"], "experience_years": 3},  # Duplicate name
        {"name": "Eve", "skills": [], "experience_years": 0},  # Empty skills, no experience
    ]
    
    score_breakdowns = [
        {"final_score": 0.76},
        {"final_score": 0.75},
        {"final_score": 0.77},
        {"final_score": 0.75},
        {"final_score": 0.76},
    ]
    
    report = generate_bias_report(resumes, score_breakdowns)
    
    print(f"\n{report.summary}\n")
    print(f"Total flags: {len(report.flags)}")
    print(f"  Critical: {len(report.get_flags_by_severity('critical'))}")
    print(f"  Warning: {len(report.get_flags_by_severity('warning'))}")
    print(f"  Info: {len(report.get_flags_by_severity('info'))}\n")
    
    # Group by category
    from collections import defaultdict
    by_category = defaultdict(list)
    for flag in report.flags:
        by_category[flag.category].append(flag)
    
    print("Flags by category:")
    for category, flags in by_category.items():
        print(f"\n  {category.upper()}: {len(flags)} flag(s)")
        for flag in flags:
            print(f"    - [{flag.severity}] {flag.message}")


def example_9_export_report():
    """Example 9: Export report to JSON"""
    print("\n" + "="*80)
    print("Example 9: Export Report to JSON")
    print("="*80)
    
    resumes = [
        {"name": "Alice", "skills": ["Python"], "experience_years": 5},
        {"name": "Bob", "experience_years": 4},  # Missing skills
        {"name": "Carol", "skills": ["Java"], "experience_years": 6},
    ]
    
    report = generate_bias_report(resumes)
    report_dict = report.to_dict()
    
    # Save to JSON
    json_output = json.dumps(report_dict, indent=2)
    
    print("\nReport exported to JSON:")
    print(json_output)
    
    # Save to file (commented out)
    # with open('bias_report.json', 'w') as f:
    #     json.dump(report_dict, f, indent=2)
    # print("\n✅ Report saved to bias_report.json")


def example_10_custom_thresholds():
    """Example 10: Use custom detection thresholds"""
    print("\n" + "="*80)
    print("Example 10: Custom Detection Thresholds")
    print("="*80)
    
    resumes = [
        {"name": "Alice", "skills": ["Python"], "experience_years": 5},
        {"name": "Bob", "experience_years": 4},  # Missing skills
    ]
    
    # Default thresholds
    print("\nWith default thresholds:")
    detector_default = BiasDetector()
    report_default = detector_default.generate_report(resumes)
    print(f"  Flags detected: {len(report_default.flags)}")
    
    # Strict thresholds (more sensitive)
    print("\nWith strict thresholds (more sensitive):")
    detector_strict = BiasDetector(
        missing_field_threshold=0.2,  # Flag if >20% missing
        variance_threshold=0.5,       # Flag if CV > 0.5
        score_spread_threshold=0.7    # Flag if spread < 0.7
    )
    report_strict = detector_strict.generate_report(resumes)
    print(f"  Flags detected: {len(report_strict.flags)}")
    
    # Lenient thresholds (less sensitive)
    print("\nWith lenient thresholds (less sensitive):")
    detector_lenient = BiasDetector(
        missing_field_threshold=0.6,  # Flag only if >60% missing
        variance_threshold=1.0,       # Flag if CV > 1.0
        score_spread_threshold=0.3    # Flag if spread < 0.3
    )
    report_lenient = detector_lenient.generate_report(resumes)
    print(f"  Flags detected: {len(report_lenient.flags)}")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("BIAS DETECTION MODULE - EXAMPLES")
    print("="*80)
    print("\nThis module helps identify potential bias and data quality issues")
    print("without inferring protected attributes (race, gender, age, etc.)\n")
    
    examples = [
        ("Clean Data", example_1_clean_data),
        ("Missing Fields", example_2_missing_fields),
        ("Experience Variance", example_3_experience_variance),
        ("Education Patterns", example_4_education_patterns),
        ("Skill Diversity", example_5_skill_diversity),
        ("Scoring Patterns", example_6_scoring_patterns),
        ("Duplicate Detection", example_7_duplicate_detection),
        ("Comprehensive Report", example_8_comprehensive_report),
        ("Export to JSON", example_9_export_report),
        ("Custom Thresholds", example_10_custom_thresholds),
    ]
    
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
    
    print("\n" + "="*80)
    print("✅ All examples completed!")
    print("="*80)
    print("\nKey Takeaways:")
    print("  1. Bias detection identifies data quality issues and patterns")
    print("  2. It does NOT infer protected attributes")
    print("  3. Review all flags in the context of your hiring process")
    print("  4. Use recommendations to improve data collection and parsing")
    print("  5. Adjust thresholds based on your specific needs")


if __name__ == "__main__":
    main()
