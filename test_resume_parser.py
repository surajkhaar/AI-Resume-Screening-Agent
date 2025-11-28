"""
Unit tests for resume_parser module
"""

import unittest
import json
from resume_parser import ResumeParser
from unittest.mock import Mock, patch, MagicMock


class TestResumeParser(unittest.TestCase):
    """Test cases for ResumeParser class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = ResumeParser(openai_api_key="test_key")
        
        self.sample_text = """
        John Doe
        john.doe@email.com | +1-234-567-8900
        
        PROFESSIONAL SUMMARY
        Experienced software engineer with 5+ years in full-stack development.
        
        SKILLS
        Python, JavaScript, React, Django, AWS, Docker, Machine Learning
        
        EXPERIENCE
        Senior Software Engineer - Tech Corp
        2020 - Present
        - Led development of ML-powered applications
        - Managed team of 5 developers
        
        Software Engineer - StartUp Inc
        2018 - 2020
        - Built scalable web applications
        
        EDUCATION
        Master of Science in Computer Science
        Stanford University, 2018
        
        Bachelor of Science in Software Engineering
        MIT, 2016
        """
    
    def test_extract_email(self):
        """Test email extraction"""
        email = self.parser._extract_email(self.sample_text)
        self.assertEqual(email, "john.doe@email.com")
    
    def test_extract_phone(self):
        """Test phone number extraction"""
        phone = self.parser._extract_phone(self.sample_text)
        self.assertIsNotNone(phone)
        self.assertIn("234", phone)
    
    def test_extract_name(self):
        """Test name extraction"""
        name = self.parser._extract_name(self.sample_text)
        self.assertEqual(name, "John Doe")
    
    def test_extract_skills(self):
        """Test skills extraction"""
        skills = self.parser._extract_skills(self.sample_text)
        self.assertIsInstance(skills, list)
        self.assertTrue(len(skills) > 0)
        self.assertIn("Python", skills)
    
    def test_extract_experience_years(self):
        """Test experience years extraction"""
        years = self.parser._extract_experience_years(self.sample_text)
        self.assertIsNotNone(years)
        self.assertGreater(years, 0)
    
    def test_extract_education(self):
        """Test education extraction"""
        education = self.parser._extract_education(self.sample_text)
        self.assertIsInstance(education, list)
        self.assertTrue(len(education) > 0)
        self.assertTrue(any('Master' in edu.get('degree', '') for edu in education))
    
    def test_extract_summary(self):
        """Test summary extraction"""
        summary = self.parser._extract_summary(self.sample_text)
        self.assertIsNotNone(summary)
        self.assertIn("software engineer", summary.lower())
    
    def test_extract_section(self):
        """Test section extraction"""
        skills_section = self.parser._extract_section(self.sample_text, ['skills'])
        self.assertIsNotNone(skills_section)
        self.assertIn("Python", skills_section)
    
    def test_is_data_incomplete(self):
        """Test data completeness check"""
        # Complete data
        complete_data = {
            "name": "John Doe",
            "email": "john@email.com",
            "skills": ["Python"],
            "education": [{"degree": "BS"}]
        }
        self.assertFalse(self.parser._is_data_incomplete(complete_data))
        
        # Incomplete data
        incomplete_data = {
            "name": None,
            "email": None,
            "skills": [],
            "education": []
        }
        self.assertTrue(self.parser._is_data_incomplete(incomplete_data))
    
    @patch('pdfplumber.open')
    def test_extract_from_pdf(self, mock_pdfplumber):
        """Test PDF text extraction"""
        # Mock PDF page
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample text from PDF"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        
        mock_pdfplumber.return_value = mock_pdf
        
        # Test extraction
        text = self.parser._extract_from_pdf(b"fake pdf content")
        self.assertIn("Sample text", text)
    
    @patch('docx.Document')
    def test_extract_from_docx(self, mock_document):
        """Test DOCX text extraction"""
        # Mock document paragraphs
        mock_paragraph = Mock()
        mock_paragraph.text = "Sample text from DOCX"
        
        mock_doc = Mock()
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []
        
        mock_document.return_value = mock_doc
        
        # Test extraction
        text = self.parser._extract_from_docx(b"fake docx content")
        self.assertIn("Sample text", text)
    
    def test_extract_structured_data(self):
        """Test complete structured data extraction"""
        data = self.parser._extract_structured_data(self.sample_text)
        
        # Verify all expected fields are present
        expected_fields = ['name', 'email', 'phone', 'skills', 'experience_years', 'education', 'summary']
        for field in expected_fields:
            self.assertIn(field, data)
        
        # Verify data types
        self.assertIsInstance(data['skills'], list)
        self.assertIsInstance(data['education'], list)
    
    @patch('openai.OpenAI')
    def test_extract_with_openai(self, mock_openai):
        """Test OpenAI extraction fallback"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "name": "John Doe",
            "email": "john@email.com",
            "phone": "123-456-7890",
            "skills": ["Python", "JavaScript"],
            "experience_years": 5,
            "education": [{"degree": "BS CS", "year": "2016"}],
            "summary": "Software engineer"
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        self.parser.client = mock_client
        
        existing_data = {
            "name": None,
            "email": None,
            "phone": None,
            "skills": [],
            "experience_years": None,
            "education": [],
            "summary": None
        }
        
        result = self.parser._extract_with_openai(self.sample_text, existing_data)
        
        # Verify OpenAI data was used
        self.assertEqual(result['name'], "John Doe")
        self.assertEqual(result['email'], "john@email.com")
        self.assertTrue(len(result['skills']) > 0)


class TestResumeParserIntegration(unittest.TestCase):
    """Integration tests for resume parsing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = ResumeParser()
    
    def test_parse_resume_without_openai(self):
        """Test resume parsing without OpenAI key"""
        sample_resume = """
        Jane Smith
        jane.smith@example.com
        555-123-4567
        
        SUMMARY
        Data scientist with 3 years of experience.
        
        SKILLS
        Python, Machine Learning, TensorFlow, SQL
        
        EDUCATION
        MS in Data Science, 2020
        """
        
        # This should work without OpenAI
        result = self.parser._extract_structured_data(sample_resume)
        
        self.assertIsNotNone(result['email'])
        self.assertIsNotNone(result['phone'])
        self.assertTrue(len(result['skills']) > 0)


def run_tests():
    """Run all tests"""
    unittest.main()


if __name__ == '__main__':
    run_tests()
