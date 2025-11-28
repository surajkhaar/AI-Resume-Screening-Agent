"""
Test the explainability function for resume matching
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from scoring import ResumeScorer, ScoreBreakdown, MatchExplanation, explain_match


class TestExplainMatch(unittest.TestCase):
    """Test cases for explain_match functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scorer = ResumeScorer()
        
        self.sample_resume = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "Machine Learning", "TensorFlow", "AWS", "Docker"],
            "experience_years": 6,
            "education": [
                {"degree": "Master of Science in Computer Science", "year": "2019"}
            ],
            "summary": "Experienced ML engineer with 6 years in production ML systems"
        }
        
        self.sample_job_description = """
        Senior Machine Learning Engineer
        
        Requirements:
        - 5+ years of experience in machine learning
        - Strong Python programming skills
        - Experience with TensorFlow or PyTorch
        - AWS cloud experience
        - Master's degree in Computer Science or related field
        
        Nice to have:
        - Docker and Kubernetes
        """
        
        self.sample_score_breakdown = ScoreBreakdown(
            skill_match_score=0.92,
            experience_score=1.15,
            education_score=1.0,
            semantic_similarity_score=0.85,
            final_score=0.87,
            matched_skills=["Python", "Machine Learning", "TensorFlow", "AWS", "Docker"],
            missing_skills=["Kubernetes"],
            experience_years=6,
            required_experience=5,
            has_required_degree=True
        )
    
    def test_match_explanation_structure(self):
        """Test MatchExplanation dataclass structure"""
        explanation = MatchExplanation(
            summary="Test summary",
            top_reasons=["Reason 1", "Reason 2", "Reason 3"],
            recommendation="Strong Match"
        )
        
        self.assertEqual(explanation.summary, "Test summary")
        self.assertEqual(len(explanation.top_reasons), 3)
        self.assertEqual(explanation.recommendation, "Strong Match")
    
    def test_match_explanation_to_dict(self):
        """Test conversion to dictionary"""
        explanation = MatchExplanation(
            summary="Test",
            top_reasons=["R1", "R2", "R3"],
            recommendation="Good Match"
        )
        
        result = explanation.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['summary'], "Test")
        self.assertEqual(len(result['top_reasons']), 3)
    
    @patch('scoring.OPENAI_AVAILABLE', False)
    def test_explain_match_without_openai(self):
        """Test that explain_match raises error when OpenAI not available"""
        with self.assertRaises(ImportError):
            self.scorer.explain_match(
                self.sample_resume,
                self.sample_job_description
            )
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('scoring.OPENAI_AVAILABLE', True)
    def test_explain_match_without_api_key(self):
        """Test that explain_match raises error when API key missing"""
        with self.assertRaises(ValueError):
            self.scorer.explain_match(
                self.sample_resume,
                self.sample_job_description
            )
    
    @patch('scoring.OPENAI_AVAILABLE', True)
    @patch('scoring.OpenAI')
    def test_explain_match_with_api_key(self, mock_openai_class):
        """Test explain_match with mocked OpenAI response"""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
Summary: John Doe is an excellent fit for the Senior Machine Learning Engineer role. With 6 years of experience and a Master's degree, he exceeds the minimum qualifications.

Top 3 Reasons:
1. Strong technical match with all core skills
2. Experience exceeds requirement by 1 year
3. Master's degree meets educational requirement

Recommendation: Strong Match - Highly recommended for interview
"""
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Call explain_match
        explanation = self.scorer.explain_match(
            self.sample_resume,
            self.sample_job_description,
            self.sample_score_breakdown,
            api_key="test_key"
        )
        
        # Verify result
        self.assertIsInstance(explanation, MatchExplanation)
        self.assertIn("excellent fit", explanation.summary.lower())
        self.assertEqual(len(explanation.top_reasons), 3)
        self.assertIn("Strong Match", explanation.recommendation)
        
        # Verify OpenAI was called correctly
        mock_openai_class.assert_called_once_with(api_key="test_key")
        mock_client.chat.completions.create.assert_called_once()
        
        # Check call parameters
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], 'gpt-4')
        self.assertEqual(call_args.kwargs['temperature'], 0.3)
    
    @patch('scoring.OPENAI_AVAILABLE', True)
    @patch('scoring.OpenAI')
    def test_explain_match_fallback_on_error(self, mock_openai_class):
        """Test fallback explanation when OpenAI call fails"""
        # Mock OpenAI to raise exception
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Call explain_match
        explanation = self.scorer.explain_match(
            self.sample_resume,
            self.sample_job_description,
            self.sample_score_breakdown,
            api_key="test_key"
        )
        
        # Should return fallback explanation
        self.assertIsInstance(explanation, MatchExplanation)
        self.assertIsNotNone(explanation.summary)
        self.assertEqual(len(explanation.top_reasons), 3)
        self.assertIn("Match", explanation.recommendation)
    
    @patch('scoring.OPENAI_AVAILABLE', True)
    @patch('scoring.OpenAI')
    def test_explain_match_computes_score_if_not_provided(self, mock_openai_class):
        """Test that explain_match computes score if not provided"""
        # Mock OpenAI
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
Summary: Test summary.

Top 3 Reasons:
1. Reason 1
2. Reason 2
3. Reason 3

Recommendation: Good Match
"""
        mock_client.chat.completions.create.return_value = mock_response
        
        # Call without score_breakdown
        explanation = self.scorer.explain_match(
            self.sample_resume,
            self.sample_job_description,
            score_breakdown=None,  # Should compute internally
            api_key="test_key"
        )
        
        self.assertIsInstance(explanation, MatchExplanation)
    
    @patch('scoring.OPENAI_AVAILABLE', True)
    @patch('scoring.OpenAI')
    def test_explain_match_prompt_includes_candidate_info(self, mock_openai_class):
        """Test that prompt includes candidate information"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Summary: Test\n\nTop 3 Reasons:\n1. R1\n2. R2\n3. R3\n\nRecommendation: Good"
        mock_client.chat.completions.create.return_value = mock_response
        
        self.scorer.explain_match(
            self.sample_resume,
            self.sample_job_description,
            self.sample_score_breakdown,
            api_key="test_key"
        )
        
        # Get the prompt that was sent
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args.kwargs['messages'][1]['content']
        
        # Verify candidate info is in prompt
        self.assertIn("John Doe", prompt)
        self.assertIn("Python", prompt)
        self.assertIn("6 years", prompt)
        self.assertIn("87%", prompt)  # Final score
    
    @patch('scoring.OPENAI_AVAILABLE', True)
    @patch('scoring.OpenAI')
    def test_explain_match_uses_few_shot_examples(self, mock_openai_class):
        """Test that prompt includes few-shot examples"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Summary: Test\n\nTop 3 Reasons:\n1. R1\n2. R2\n3. R3\n\nRecommendation: Good"
        mock_client.chat.completions.create.return_value = mock_response
        
        self.scorer.explain_match(
            self.sample_resume,
            self.sample_job_description,
            self.sample_score_breakdown,
            api_key="test_key"
        )
        
        # Get the prompt
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args.kwargs['messages'][1]['content']
        
        # Verify few-shot examples are present
        self.assertIn("FEW-SHOT EXAMPLES", prompt)
        self.assertIn("Example 1:", prompt)
        self.assertIn("Example 2:", prompt)
        self.assertIn("Example 3:", prompt)
    
    @patch('scoring.OPENAI_AVAILABLE', True)
    @patch('scoring.OpenAI')
    def test_convenience_function(self, mock_openai_class):
        """Test convenience function for explain_match"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Summary: Test\n\nTop 3 Reasons:\n1. R1\n2. R2\n3. R3\n\nRecommendation: Good"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Use convenience function
        explanation = explain_match(
            self.sample_resume,
            self.sample_job_description,
            api_key="test_key"
        )
        
        self.assertIsInstance(explanation, MatchExplanation)
    
    def test_fallback_explanation_strong_match(self):
        """Test fallback explanation for strong match"""
        strong_breakdown = ScoreBreakdown(
            skill_match_score=0.95,
            experience_score=1.2,
            education_score=1.0,
            semantic_similarity_score=0.9,
            final_score=0.85,
            matched_skills=["Python", "ML", "AWS"],
            missing_skills=[],
            experience_years=6,
            required_experience=5,
            has_required_degree=True
        )
        
        # Force fallback by mocking OpenAI error
        with patch('scoring.OPENAI_AVAILABLE', True), \
             patch('scoring.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("Error")
            
            explanation = self.scorer.explain_match(
                self.sample_resume,
                self.sample_job_description,
                strong_breakdown,
                api_key="test_key"
            )
            
            self.assertIn("Strong Match", explanation.recommendation)
            self.assertIn("strong alignment", explanation.summary.lower())


def run_tests():
    """Run all tests"""
    unittest.main()


if __name__ == '__main__':
    run_tests()
