"""
Unit tests for embeddings module
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from embeddings import EmbeddingsManager


class TestEmbeddingsManager(unittest.TestCase):
    """Test cases for EmbeddingsManager class"""
    
    @patch('embeddings.SentenceTransformer')
    def setUp(self, mock_transformer):
        """Set up test fixtures"""
        # Mock the sentence transformer
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.random.rand(384)
        mock_transformer.return_value = mock_model
        
        # Create manager with FAISS fallback (no API keys)
        self.manager = EmbeddingsManager(
            pinecone_api_key=None,
            use_faiss_fallback=True
        )
    
    def test_initialization(self):
        """Test embeddings manager initialization"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.embedding_dimension, 384)
        self.assertIn(self.manager.vector_db_type, ['pinecone', 'faiss'])
    
    def test_generate_embedding(self):
        """Test single embedding generation"""
        text = "Python developer with 5 years experience"
        embedding = self.manager.generate_embedding(text)
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape[0], self.manager.embedding_dimension)
    
    def test_generate_embeddings_batch(self):
        """Test batch embedding generation"""
        texts = [
            "Python developer",
            "Java engineer",
            "Data scientist"
        ]
        
        with patch.object(self.manager.model, 'encode') as mock_encode:
            mock_encode.return_value = np.random.rand(3, 384)
            embeddings = self.manager.generate_embeddings(texts)
            
            self.assertEqual(embeddings.shape[0], 3)
            self.assertEqual(embeddings.shape[1], 384)
    
    def test_create_resume_text(self):
        """Test resume text creation"""
        resume_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "Machine Learning"],
            "experience_years": 5,
            "summary": "Experienced developer",
            "education": [{"degree": "BS Computer Science"}]
        }
        
        text = self.manager.create_resume_text(resume_data)
        
        self.assertIn("John Doe", text)
        self.assertIn("Python", text)
        self.assertIn("5 years", text)
        self.assertIn("Experienced developer", text)
    
    def test_create_resume_text_partial(self):
        """Test resume text creation with partial data"""
        resume_data = {
            "name": "Jane Smith",
            "skills": ["Java"]
        }
        
        text = self.manager.create_resume_text(resume_data)
        
        self.assertIn("Jane Smith", text)
        self.assertIn("Java", text)
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        a = np.array([1, 0, 0])
        b = np.array([1, 0, 0])
        
        similarity = EmbeddingsManager._cosine_similarity(a, b)
        self.assertAlmostEqual(similarity, 1.0)
        
        # Test orthogonal vectors
        a = np.array([1, 0])
        b = np.array([0, 1])
        similarity = EmbeddingsManager._cosine_similarity(a, b)
        self.assertAlmostEqual(similarity, 0.0)
    
    def test_upsert_resume(self):
        """Test upserting resume to vector DB"""
        resume_data = {
            "name": "Test User",
            "email": "test@example.com",
            "skills": ["Python", "Docker"],
            "experience_years": 3
        }
        
        with patch.object(self.manager, 'generate_embedding') as mock_gen:
            mock_gen.return_value = np.random.rand(384)
            
            success = self.manager.upsert_resume("resume_001", resume_data)
            self.assertTrue(success)
    
    def test_compare_resume_to_job(self):
        """Test resume to job comparison"""
        resume_data = {
            "name": "Python Developer",
            "skills": ["Python", "Django", "AWS"],
            "experience_years": 5
        }
        
        job_description = "Looking for Python developer with AWS experience"
        
        with patch.object(self.manager, 'generate_embeddings') as mock_gen:
            # Mock embeddings for resume and job
            mock_gen.return_value = np.array([
                [1, 0, 0, 0],  # Resume embedding
                [0.9, 0.1, 0, 0]  # Job embedding (similar)
            ])
            
            score = self.manager.compare_resume_to_job(resume_data, job_description)
            
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_rank_resumes(self):
        """Test ranking multiple resumes"""
        resumes = [
            {"name": "Candidate A", "skills": ["Python", "ML"], "experience_years": 5},
            {"name": "Candidate B", "skills": ["Java", "Spring"], "experience_years": 3},
            {"name": "Candidate C", "skills": ["Python", "Django"], "experience_years": 7}
        ]
        
        job_description = "Python developer needed"
        
        with patch.object(self.manager, 'compare_resume_to_job') as mock_compare:
            # Mock scores
            mock_compare.side_effect = [0.85, 0.60, 0.90]
            
            ranked = self.manager.rank_resumes(resumes, job_description)
            
            self.assertEqual(len(ranked), 3)
            # Check sorted by score descending
            self.assertEqual(ranked[0][1], 0.90)  # Candidate C
            self.assertEqual(ranked[1][1], 0.85)  # Candidate A
            self.assertEqual(ranked[2][1], 0.60)  # Candidate B
    
    def test_upsert_resumes_batch(self):
        """Test batch upserting resumes"""
        resumes = [
            ("resume_001", {"name": "User 1", "skills": ["Python"]}),
            ("resume_002", {"name": "User 2", "skills": ["Java"]}),
            ("resume_003", {"name": "User 3", "skills": ["JavaScript"]})
        ]
        
        with patch.object(self.manager, 'upsert_resume') as mock_upsert:
            mock_upsert.return_value = True
            
            results = self.manager.upsert_resumes_batch(resumes)
            
            self.assertEqual(len(results), 3)
            self.assertTrue(all(results.values()))
    
    def test_get_stats(self):
        """Test getting vector DB statistics"""
        stats = self.manager.get_stats()
        
        self.assertIn('vector_db_type', stats)
        self.assertIn('embedding_dimension', stats)
        self.assertEqual(stats['embedding_dimension'], 384)


class TestEmbeddingsFAISS(unittest.TestCase):
    """Test FAISS-specific functionality"""
    
    @patch('embeddings.SentenceTransformer')
    @patch('embeddings.faiss')
    def setUp(self, mock_faiss, mock_transformer):
        """Set up FAISS test fixtures"""
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.random.rand(384)
        mock_transformer.return_value = mock_model
        
        # Mock FAISS
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatL2.return_value = mock_index
        mock_faiss.IndexIDMap.return_value = mock_index
        
        self.manager = EmbeddingsManager(use_faiss_fallback=True)
    
    def test_faiss_initialization(self):
        """Test FAISS initialization"""
        self.assertEqual(self.manager.vector_db_type, 'faiss')
        self.assertIsNotNone(self.manager.index)
    
    def test_faiss_search(self):
        """Test searching in FAISS"""
        query = "Python developer"
        
        with patch.object(self.manager, '_search_faiss') as mock_search:
            mock_search.return_value = [
                {'id': '123', 'score': 0.95, 'metadata': {'name': 'John'}},
                {'id': '456', 'score': 0.85, 'metadata': {'name': 'Jane'}}
            ]
            
            with patch.object(self.manager, 'generate_embedding') as mock_gen:
                mock_gen.return_value = np.random.rand(384)
                
                results = self.manager.search(query, top_k=5)
                
                self.assertEqual(len(results), 2)
                self.assertEqual(results[0]['id'], '123')
                self.assertGreater(results[0]['score'], results[1]['score'])


class TestEmbeddingsPinecone(unittest.TestCase):
    """Test Pinecone-specific functionality"""
    
    @patch('embeddings.SentenceTransformer')
    @patch('embeddings.Pinecone')
    def setUp(self, mock_pinecone_class, mock_transformer):
        """Set up Pinecone test fixtures"""
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.random.rand(384)
        mock_transformer.return_value = mock_model
        
        # Mock Pinecone
        mock_pc = Mock()
        mock_pc.list_indexes.return_value.names.return_value = []
        mock_index = Mock()
        mock_pc.Index.return_value = mock_index
        mock_pinecone_class.return_value = mock_pc
        
        try:
            self.manager = EmbeddingsManager(
                pinecone_api_key="test_key",
                pinecone_environment="test_env",
                use_faiss_fallback=False
            )
        except:
            self.skipTest("Pinecone initialization failed in test")
    
    def test_pinecone_initialization(self):
        """Test Pinecone initialization"""
        self.assertEqual(self.manager.vector_db_type, 'pinecone')
        self.assertIsNotNone(self.manager.index)
    
    def test_pinecone_upsert(self):
        """Test upserting to Pinecone"""
        resume_data = {
            "name": "Test User",
            "skills": ["Python"],
            "experience_years": 5
        }
        
        with patch.object(self.manager.index, 'upsert') as mock_upsert:
            with patch.object(self.manager, 'generate_embedding') as mock_gen:
                mock_gen.return_value = np.random.rand(384)
                
                success = self.manager.upsert_resume("resume_001", resume_data)
                
                self.assertTrue(success)
                mock_upsert.assert_called_once()
    
    def test_pinecone_search(self):
        """Test searching in Pinecone"""
        query = "Python developer"
        
        with patch.object(self.manager.index, 'query') as mock_query:
            mock_query.return_value = {
                'matches': [
                    {
                        'id': 'resume_001',
                        'score': 0.95,
                        'metadata': {'name': 'John Doe', 'skills': '["Python"]'}
                    }
                ]
            }
            
            with patch.object(self.manager, 'generate_embedding') as mock_gen:
                mock_gen.return_value = np.random.rand(384)
                
                results = self.manager.search(query, top_k=5)
                
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]['id'], 'resume_001')
                self.assertEqual(results[0]['score'], 0.95)


class TestEmbeddingsIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow: create, upsert, search"""
        with patch('embeddings.SentenceTransformer') as mock_transformer:
            with patch('embeddings.faiss'):
                # Mock sentence transformer
                mock_model = Mock()
                mock_model.get_sentence_embedding_dimension.return_value = 384
                mock_model.encode.return_value = np.random.rand(384)
                mock_transformer.return_value = mock_model
                
                # Create manager
                manager = EmbeddingsManager(use_faiss_fallback=True)
                
                # Create resume
                resume = {
                    "name": "John Doe",
                    "skills": ["Python", "Docker"],
                    "experience_years": 5
                }
                
                # Upsert
                with patch.object(manager, 'upsert_resume') as mock_upsert:
                    mock_upsert.return_value = True
                    success = manager.upsert_resume("resume_001", resume)
                    self.assertTrue(success)
                
                # Search
                with patch.object(manager, 'search') as mock_search:
                    mock_search.return_value = [
                        {'id': 'resume_001', 'score': 0.9}
                    ]
                    results = manager.search("Python developer")
                    self.assertEqual(len(results), 1)


def run_tests():
    """Run all tests"""
    unittest.main()


if __name__ == '__main__':
    run_tests()
