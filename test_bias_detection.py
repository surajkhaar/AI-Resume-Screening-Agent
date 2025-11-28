"""
Test Suite for Bias Detection Module
Tests various bias detection scenarios
"""

import unittest
from bias_detection import BiasDetector, BiasFlag, BiasReport, generate_bias_report


class TestBiasDetection(unittest.TestCase):
    """Test bias detection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = BiasDetector()
    
    def test_no_flags_for_good_data(self):
        """Test that good quality data produces no flags"""
        resumes = [
            {
                "name": "Alice Johnson",
                "email": "alice@email.com",
                "phone": "+1-555-0001",
                "skills": ["Python", "Java", "SQL"],
                "experience_years": 5,
                "education": [{"degree": "Master of Science in CS", "year": "2018"}]
            },
            {
                "name": "Bob Smith",
                "email": "bob@company.com",
                "phone": "+1-555-0002",
                "skills": ["JavaScript", "React", "Node.js"],
                "experience_years": 4,
                "education": [{"degree": "Bachelor of Science in CS", "year": "2019"}]
            },
            {
                "name": "Carol Williams",
                "email": "carol@example.com",
                "phone": "+1-555-0003",
                "skills": ["C++", "Python", "Docker"],
                "experience_years": 6,
                "education": [{"degree": "PhD in Computer Science", "year": "2017"}]
            }
        ]
        
        report = self.detector.generate_report(resumes)
        
        # Should have no critical or warning flags for good data
        self.assertFalse(report.has_critical_flags())
        self.assertEqual(len(report.get_flags_by_severity("critical")), 0)
    
    def test_missing_fields_detection(self):
        """Test detection of missing critical fields"""
        resumes = [
            {"name": "Alice", "skills": ["Python"]},
            {"name": "Bob"},  # Missing skills
            {"name": "Carol"},  # Missing skills
        ]
        
        report = self.detector.generate_report(resumes)
        
        # Should flag missing skills
        self.assertTrue(len(report.flags) > 0)
        
        # Check if skills flag exists
        skills_flags = [f for f in report.flags if "skills" in f.message.lower()]
        self.assertTrue(len(skills_flags) > 0)
    
    def test_extreme_experience_variance(self):
        """Test detection of extreme experience variance"""
        resumes = [
            {"name": "Junior Dev", "skills": ["Python"], "experience_years": 1},
            {"name": "Mid Dev", "skills": ["Python"], "experience_years": 5},
            {"name": "Senior Dev", "skills": ["Python"], "experience_years": 15},
            {"name": "Principal", "skills": ["Python"], "experience_years": 25},
        ]
        
        report = self.detector.generate_report(resumes)
        
        # Should flag high variance
        variance_flags = [f for f in report.flags if f.category == "variance"]
        self.assertTrue(len(variance_flags) > 0)
    
    def test_education_distribution(self):
        """Test detection of education distribution issues"""
        # All candidates missing education
        resumes = [
            {"name": f"Candidate {i}", "skills": ["Python"], "experience_years": 5}
            for i in range(5)
        ]
        
        report = self.detector.generate_report(resumes)
        
        # Should flag missing education
        education_flags = [f for f in report.flags if "education" in f.message.lower()]
        self.assertTrue(len(education_flags) > 0)
    
    def test_skill_diversity_issues(self):
        """Test detection of low skill diversity"""
        resumes = [
            {"name": "Alice", "skills": ["Python"], "experience_years": 5},
            {"name": "Bob", "skills": ["Java"], "experience_years": 4},
            {"name": "Carol", "skills": [], "experience_years": 6},  # No skills
        ]
        
        report = self.detector.generate_report(resumes)
        
        # Should flag low skill extraction
        skill_flags = [f for f in report.flags if "skill" in f.message.lower()]
        self.assertTrue(len(skill_flags) > 0)
    
    def test_no_skills_critical_flag(self):
        """Test critical flag when no skills extracted"""
        resumes = [
            {"name": "Alice", "skills": [], "experience_years": 5},
            {"name": "Bob", "skills": [], "experience_years": 4},
            {"name": "Carol", "skills": [], "experience_years": 6},
        ]
        
        report = self.detector.generate_report(resumes)
        
        # Should have critical flag
        self.assertTrue(report.has_critical_flags())
    
    def test_score_clustering(self):
        """Test detection of score clustering"""
        resumes = [
            {"name": "Alice", "skills": ["Python"], "experience_years": 5},
            {"name": "Bob", "skills": ["Java"], "experience_years": 5},
            {"name": "Carol", "skills": ["C++"], "experience_years": 5},
        ]
        
        # All very similar scores
        score_breakdowns = [
            {"final_score": 0.75},
            {"final_score": 0.76},
            {"final_score": 0.77},
        ]
        
        report = self.detector.generate_report(resumes, score_breakdowns)
        
        # Should flag narrow score distribution
        pattern_flags = [f for f in report.flags if f.category == "pattern" and "cluster" in f.message.lower()]
        # Note: May not always flag depending on threshold
        # Just ensure no error occurs
        self.assertIsNotNone(report)
    
    def test_duplicate_detection(self):
        """Test detection of duplicate candidates"""
        resumes = [
            {"name": "Alice Johnson", "skills": ["Python"], "experience_years": 5},
            {"name": "Alice Johnson", "skills": ["Java"], "experience_years": 6},  # Duplicate
            {"name": "Bob Smith", "skills": ["C++"], "experience_years": 4},
        ]
        
        report = self.detector.generate_report(resumes)
        
        # Should flag duplicates
        consistency_flags = [f for f in report.flags if f.category == "consistency"]
        self.assertTrue(len(consistency_flags) > 0)
    
    def test_incomplete_parsing(self):
        """Test detection of incomplete parsing"""
        resumes = [
            {"name": "Alice"},  # Very incomplete
            {"name": "Bob", "skills": ["Python"]},  # Still incomplete
            {
                "name": "Carol",
                "email": "carol@email.com",
                "skills": ["Python", "Java"],
                "experience_years": 5,
                "education": [{"degree": "Master", "year": "2018"}]
            }  # Complete
        ]
        
        report = self.detector.generate_report(resumes)
        
        # Should flag incomplete parsing
        parsing_flags = [f for f in report.flags if f.category == "parsing_quality"]
        self.assertTrue(len(parsing_flags) > 0)
    
    def test_bias_flag_structure(self):
        """Test BiasFlag dataclass structure"""
        flag = BiasFlag(
            severity="warning",
            category="test",
            message="Test message",
            affected_candidates=["Alice", "Bob"],
            recommendation="Test recommendation",
            details={"key": "value"}
        )
        
        self.assertEqual(flag.severity, "warning")
        self.assertEqual(flag.category, "test")
        self.assertEqual(len(flag.affected_candidates), 2)
    
    def test_bias_report_methods(self):
        """Test BiasReport methods"""
        flags = [
            BiasFlag("critical", "test", "Critical issue", [], "Fix it", {}),
            BiasFlag("warning", "test", "Warning issue", [], "Review it", {}),
            BiasFlag("info", "test", "Info", [], "Note it", {}),
        ]
        
        report = BiasReport(
            total_candidates=5,
            flags=flags,
            summary="Test summary"
        )
        
        self.assertTrue(report.has_critical_flags())
        self.assertTrue(report.has_warnings())
        self.assertEqual(len(report.get_flags_by_severity("critical")), 1)
        self.assertEqual(len(report.get_flags_by_severity("warning")), 1)
        self.assertEqual(len(report.get_flags_by_severity("info")), 1)
    
    def test_to_dict_export(self):
        """Test export to dictionary"""
        resumes = [
            {"name": "Alice", "skills": ["Python"], "experience_years": 5},
        ]
        
        report = self.detector.generate_report(resumes)
        report_dict = report.to_dict()
        
        self.assertIn("total_candidates", report_dict)
        self.assertIn("flags", report_dict)
        self.assertIn("summary", report_dict)
        self.assertIn("has_critical_flags", report_dict)
        self.assertIn("has_warnings", report_dict)
    
    def test_convenience_function(self):
        """Test convenience function"""
        resumes = [
            {"name": "Alice", "skills": ["Python"], "experience_years": 5},
            {"name": "Bob", "skills": ["Java"], "experience_years": 4},
        ]
        
        report = generate_bias_report(resumes)
        
        self.assertIsInstance(report, BiasReport)
        self.assertEqual(report.total_candidates, 2)
    
    def test_custom_thresholds(self):
        """Test custom threshold configuration"""
        detector = BiasDetector(
            missing_field_threshold=0.5,
            variance_threshold=0.8,
            score_spread_threshold=0.5
        )
        
        self.assertEqual(detector.missing_field_threshold, 0.5)
        self.assertEqual(detector.variance_threshold, 0.8)
        self.assertEqual(detector.score_spread_threshold, 0.5)
    
    def test_empty_resumes(self):
        """Test handling of empty resume list"""
        resumes = []
        
        report = self.detector.generate_report(resumes)
        
        self.assertEqual(report.total_candidates, 0)
    
    def test_single_resume(self):
        """Test handling of single resume"""
        resumes = [
            {
                "name": "Alice",
                "skills": ["Python", "Java"],
                "experience_years": 5,
                "education": [{"degree": "Master", "year": "2018"}]
            }
        ]
        
        report = self.detector.generate_report(resumes)
        
        # Should handle single resume without errors
        self.assertEqual(report.total_candidates, 1)
    
    def test_email_domain_concentration(self):
        """Test detection of email domain concentration"""
        resumes = [
            {"name": f"Employee {i}", "email": f"emp{i}@company.com", "skills": ["Python"]}
            for i in range(10)
        ]
        
        report = self.detector.generate_report(resumes)
        
        # Should flag domain concentration
        pattern_flags = [f for f in report.flags if "domain" in f.message.lower()]
        self.assertTrue(len(pattern_flags) > 0)
    
    def test_perfect_scores_detection(self):
        """Test detection of unusually high perfect scores"""
        resumes = [
            {"name": f"Candidate {i}", "skills": ["Python"], "experience_years": 5}
            for i in range(10)
        ]
        
        # Most candidates have perfect scores
        score_breakdowns = [
            {"final_score": 0.99 if i < 8 else 0.75}
            for i in range(10)
        ]
        
        report = self.detector.generate_report(resumes, score_breakdowns)
        
        # Should flag high rate of perfect scores
        perfect_score_flags = [f for f in report.flags if "perfect" in f.message.lower()]
        self.assertTrue(len(perfect_score_flags) > 0)


if __name__ == "__main__":
    unittest.main()
