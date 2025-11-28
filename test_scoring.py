"""
Unit tests for scoring module
"""

import unittest
from unittest.mock import Mock, patch
from scoring import ResumeScorer, ScoreBreakdown, score_resume, score_resumes_batch


class TestResumeScorer(unittest.TestCase):
    """Test cases for ResumeScorer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scorer = ResumeScorer()
        
        self.sample_resume = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "Machine Learning", "AWS", "Docker"],
            "experience_years": 5,
            "education": [
                {"degree": "Master of Science in Computer Science", "year": "2019"}
            ],
            "summary": "Experienced ML engineer with Python and AWS expertise"
        }
        
        self.sample_job_description = """
        Senior Machine Learning Engineer
        
        Requirements:
        - 3+ years of experience in machine learning
        - Strong Python programming skills
        - Experience with AWS and cloud platforms
        - Master's degree in Computer Science or related field
        - Knowledge of Docker and Kubernetes
        
        Responsibilities:
        - Design and implement ML models
        - Deploy models to production
        - Work with cross-functional teams
        """
    
    def test_initialization(self):
        """Test scorer initialization"""
        scorer = ResumeScorer()
        self.assertEqual(scorer.skill_weight, 0.35)
        self.assertEqual(scorer.experience_weight, 0.25)
        self.assertEqual(scorer.education_weight, 0.15)
        self.assertEqual(scorer.semantic_weight, 0.25)
    
    def test_custom_weights(self):
        """Test custom weight initialization"""
        scorer = ResumeScorer(
            skill_weight=0.4,
            experience_weight=0.3,
            education_weight=0.2,
            semantic_weight=0.1
        )
        self.assertEqual(scorer.skill_weight, 0.4)
    
    def test_invalid_weights(self):
        """Test that invalid weights raise error"""
        with self.assertRaises(ValueError):
            ResumeScorer(
                skill_weight=0.5,
                experience_weight=0.5,
                education_weight=0.5,
                semantic_weight=0.5
            )
    
    def test_skill_match_score_perfect_match(self):
        """Test skill matching with perfect match"""
        resume_skills = ["Python", "AWS", "Docker"]
        required_skills = ["Python", "AWS", "Docker"]
        
        score, matched, missing = self.scorer._calculate_skill_match_score(
            resume_skills, required_skills
        )
        
        self.assertEqual(score, 1.0)
        self.assertEqual(len(matched), 3)
        self.assertEqual(len(missing), 0)
    
    def test_skill_match_score_partial_match(self):
        """Test skill matching with partial match"""
        resume_skills = ["Python", "AWS"]
        required_skills = ["Python", "AWS", "Docker", "Kubernetes"]
        
        score, matched, missing = self.scorer._calculate_skill_match_score(
            resume_skills, required_skills
        )
        
        self.assertEqual(score, 0.5)  # 2 out of 4
        self.assertEqual(len(matched), 2)
        self.assertEqual(len(missing), 2)
    
    def test_skill_match_score_no_match(self):
        """Test skill matching with no match"""
        resume_skills = ["Java", "Spring"]
        required_skills = ["Python", "Django"]
        
        score, matched, missing = self.scorer._calculate_skill_match_score(
            resume_skills, required_skills
        )
        
        self.assertEqual(score, 0.0)
        self.assertEqual(len(matched), 0)
        self.assertEqual(len(missing), 2)
    
    def test_skill_match_case_insensitive(self):
        """Test that skill matching is case insensitive"""
        resume_skills = ["python", "aws"]
        required_skills = ["Python", "AWS"]
        
        score, matched, missing = self.scorer._calculate_skill_match_score(
            resume_skills, required_skills
        )
        
        self.assertEqual(score, 1.0)
    
    def test_experience_score_meets_requirement(self):
        """Test experience score when meeting requirement"""
        score = self.scorer._calculate_experience_score(5, 3)
        self.assertGreater(score, 1.0)  # Bonus for exceeding
    
    def test_experience_score_below_requirement(self):
        """Test experience score below requirement"""
        score = self.scorer._calculate_experience_score(2, 5)
        self.assertEqual(score, 0.4)  # 2/5 = 0.4
    
    def test_experience_score_no_requirement(self):
        """Test experience score with no requirement"""
        score = self.scorer._calculate_experience_score(5, None)
        self.assertEqual(score, 1.0)
    
    def test_experience_score_no_data(self):
        """Test experience score with no data"""
        score = self.scorer._calculate_experience_score(None, 3)
        self.assertEqual(score, 0.0)
    
    def test_education_score_has_required_degree(self):
        """Test education score with required degree"""
        education = [
            {"degree": "Master of Science in Computer Science", "year": "2019"}
        ]
        score = self.scorer._calculate_education_score(education, "Master")
        self.assertEqual(score, 1.0)
    
    def test_education_score_higher_degree(self):
        """Test education score with higher degree than required"""
        education = [
            {"degree": "PhD in Computer Science", "year": "2019"}
        ]
        score = self.scorer._calculate_education_score(education, "Master")
        self.assertEqual(score, 1.0)
    
    def test_education_score_lower_degree(self):
        """Test education score with lower degree than required"""
        education = [
            {"degree": "Bachelor of Science", "year": "2019"}
        ]
        score = self.scorer._calculate_education_score(education, "Master")
        self.assertEqual(score, 0.0)
    
    def test_education_score_no_requirement(self):
        """Test education score with no requirement"""
        education = [{"degree": "Bachelor", "year": "2019"}]
        score = self.scorer._calculate_education_score(education, None)
        self.assertEqual(score, 1.0)
    
    def test_extract_skills_from_job_description(self):
        """Test skill extraction from job description"""
        jd = "Looking for Python developer with AWS and Docker experience"
        skills = self.scorer._extract_skills_from_text(jd)
        
        self.assertIn("Python", skills)
        self.assertIn("Aws", skills)
        self.assertIn("Docker", skills)
    
    def test_extract_required_experience(self):
        """Test extracting required experience"""
        jd = "Looking for candidate with 5+ years of experience"
        years = self.scorer._extract_required_experience(jd)
        self.assertEqual(years, 5.0)
    
    def test_extract_required_degree(self):
        """Test extracting required degree"""
        jd = "Master's degree in Computer Science required"
        degree = self.scorer._extract_required_degree(jd)
        self.assertEqual(degree, "Master")
    
    def test_score_breakdown_structure(self):
        """Test ScoreBreakdown structure"""
        breakdown = ScoreBreakdown(
            skill_match_score=0.8,
            experience_score=0.9,
            education_score=1.0,
            semantic_similarity_score=0.85,
            final_score=0.87,
            matched_skills=["Python", "AWS"],
            missing_skills=["Docker"],
            experience_years=5,
            required_experience=3,
            has_required_degree=True
        )
        
        self.assertEqual(breakdown.skill_match_score, 0.8)
        self.assertEqual(breakdown.final_score, 0.87)
        self.assertTrue(breakdown.has_required_degree)
    
    def test_score_breakdown_to_dict(self):
        """Test converting ScoreBreakdown to dictionary"""
        breakdown = ScoreBreakdown(
            skill_match_score=0.8,
            experience_score=0.9,
            education_score=1.0,
            semantic_similarity_score=0.85,
            final_score=0.87,
            matched_skills=["Python"],
            missing_skills=["Docker"],
            experience_years=5,
            required_experience=3,
            has_required_degree=True
        )
        
        result = breakdown.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['final_score'], 0.87)
    
    def test_full_scoring_workflow(self):
        """Test complete scoring workflow"""
        breakdown = self.scorer.score_resume(
            self.sample_resume,
            self.sample_job_description
        )
        
        self.assertIsInstance(breakdown, ScoreBreakdown)
        self.assertGreaterEqual(breakdown.final_score, 0.0)
        self.assertLessEqual(breakdown.final_score, 1.0)
        self.assertGreaterEqual(breakdown.skill_match_score, 0.0)
        self.assertGreaterEqual(breakdown.experience_score, 0.0)
        self.assertGreaterEqual(breakdown.education_score, 0.0)
        self.assertGreaterEqual(breakdown.semantic_similarity_score, 0.0)
    
    def test_batch_scoring(self):
        """Test batch resume scoring"""
        resumes = [
            self.sample_resume,
            {
                "name": "Jane Smith",
                "skills": ["Java", "Spring"],
                "experience_years": 2,
                "education": [{"degree": "Bachelor", "year": "2021"}]
            }
        ]
        
        results = self.scorer.batch_score_resumes(
            resumes,
            self.sample_job_description
        )
        
        self.assertEqual(len(results), 2)
        # Results should be sorted by score
        self.assertGreaterEqual(
            results[0][1].final_score,
            results[1][1].final_score
        )
    
    def test_semantic_similarity_with_embeddings(self):
        """Test semantic similarity with embeddings manager"""
        mock_embeddings_manager = Mock()
        mock_embeddings_manager.compare_resume_to_job.return_value = 0.85
        
        scorer = ResumeScorer(embeddings_manager=mock_embeddings_manager)
        score = scorer._calculate_semantic_similarity_score(
            self.sample_resume,
            self.sample_job_description
        )
        
        self.assertEqual(score, 0.85)
        mock_embeddings_manager.compare_resume_to_job.assert_called_once()
    
    def test_semantic_similarity_fallback(self):
        """Test semantic similarity fallback without embeddings"""
        score = self.scorer._calculate_semantic_similarity_score(
            self.sample_resume,
            self.sample_job_description
        )
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_fallback_text_similarity(self):
        """Test fallback text similarity calculation"""
        score = self.scorer._fallback_text_similarity(
            self.sample_resume,
            self.sample_job_description
        )
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def test_score_resume_function(self):
        """Test convenience score_resume function"""
        resume = {
            "name": "Test User",
            "skills": ["Python", "AWS"],
            "experience_years": 5,
            "education": [{"degree": "Master"}]
        }
        
        jd = "Looking for Python developer with 3+ years experience"
        
        breakdown = score_resume(resume, jd)
        
        self.assertIsInstance(breakdown, ScoreBreakdown)
        self.assertGreaterEqual(breakdown.final_score, 0.0)
    
    def test_score_resumes_batch_function(self):
        """Test convenience score_resumes_batch function"""
        resumes = [
            {"name": "User 1", "skills": ["Python"], "experience_years": 5},
            {"name": "User 2", "skills": ["Java"], "experience_years": 3}
        ]
        
        jd = "Python developer needed"
        
        results = score_resumes_batch(resumes, jd)
        
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0][1], ScoreBreakdown)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.scorer = ResumeScorer()
    
    def test_empty_resume(self):
        """Test scoring empty resume"""
        resume = {}
        jd = "Python developer needed"
        
        breakdown = self.scorer.score_resume(resume, jd)
        
        self.assertIsInstance(breakdown, ScoreBreakdown)
        # Should have low score but not crash
        self.assertLess(breakdown.final_score, 0.5)
    
    def test_empty_job_description(self):
        """Test scoring with empty job description"""
        resume = {
            "name": "Test",
            "skills": ["Python"],
            "experience_years": 5
        }
        jd = ""
        
        breakdown = self.scorer.score_resume(resume, jd)
        
        self.assertIsInstance(breakdown, ScoreBreakdown)
    
    def test_missing_fields(self):
        """Test resume with missing fields"""
        resume = {
            "name": "Test User"
            # Missing skills, experience, education
        }
        jd = "Python developer with 5 years experience needed"
        
        breakdown = self.scorer.score_resume(resume, jd)
        
        self.assertIsInstance(breakdown, ScoreBreakdown)
        self.assertEqual(len(breakdown.matched_skills), 0)
    
    def test_zero_required_experience(self):
        """Test with zero required experience"""
        resume = {"experience_years": 0}
        score = self.scorer._calculate_experience_score(0, 0)
        self.assertEqual(score, 1.0)


def run_tests():
    """Run all tests"""
    unittest.main()


if __name__ == '__main__':
    run_tests()
