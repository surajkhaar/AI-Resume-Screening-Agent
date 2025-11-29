"""
Embeddings Module

Generates embeddings using sentence-transformers and stores them in vector databases.
Supports Pinecone (cloud) and FAISS (local) as fallback.
"""

import os
import json
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """Manage embeddings generation and vector storage with Pinecone/FAISS."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        pinecone_api_key: Optional[str] = None,
        pinecone_environment: Optional[str] = None,
        pinecone_index_name: str = "resume-index",
        use_faiss_fallback: bool = True
    ):
        """
        Initialize embeddings manager.
        
        Args:
            model_name: Sentence transformer model name
            pinecone_api_key: Pinecone API key (optional)
            pinecone_environment: Pinecone environment (optional)
            pinecone_index_name: Name for Pinecone index
            use_faiss_fallback: Use FAISS if Pinecone not available
        """
        # Load sentence transformer model
        logger.info(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dimension}")
        
        # Initialize vector database
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = pinecone_environment or os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = pinecone_index_name
        self.use_faiss_fallback = use_faiss_fallback
        
        # Try to initialize Pinecone, fallback to FAISS, then to in-memory if needed
        self.vector_db_type = None
        self.index = None
        self.faiss_metadata = {}  # Store metadata for FAISS vectors
        self.memory_vectors = {}  # In-memory vector storage as final fallback
        
        self._initialize_vector_db()
    
    def _initialize_vector_db(self):
        """Initialize vector database (Pinecone, FAISS, or in-memory fallback)."""
        # Try Pinecone first
        pinecone_index = os.getenv("PINECONE_INDEX")
        if self.pinecone_api_key and self.pinecone_environment:
            try:
                if pinecone_index:
                    self.pinecone_index_name = pinecone_index
                self._initialize_pinecone()
                self.vector_db_type = "pinecone"
                logger.info("Using Pinecone for vector storage")
                return
            except Exception as e:
                logger.warning(f"Pinecone initialization failed, falling back to local index. Error: {e}")
        
        # Fallback to FAISS
        if self.use_faiss_fallback:
            try:
                self._initialize_faiss()
                self.vector_db_type = "faiss"
                logger.info("Using FAISS for vector storage (local)")
                return
            except Exception as e:
                logger.warning(f"FAISS initialization failed, using in-memory storage. Error: {e}")
        
        # Final fallback: in-memory numpy-based storage
        logger.info("Pinecone initialization failed, falling back to local index.")
        self.vector_db_type = "memory"
        self.memory_vectors = {}
        logger.info("Using in-memory vector storage (numpy-based)")
    
    def _initialize_pinecone(self):
        """Initialize Pinecone index."""
        try:
            from pinecone import Pinecone, ServerlessSpec
            
            # Initialize Pinecone client
            pc = Pinecone(api_key=self.pinecone_api_key)
            
            # Check if index exists
            existing_indexes = pc.list_indexes().names()
            
            if self.pinecone_index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.pinecone_index_name}")
                pc.create_index(
                    name=self.pinecone_index_name,
                    dimension=self.embedding_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info("Pinecone index created")
            else:
                logger.info(f"Using existing Pinecone index: {self.pinecone_index_name}")
            
            # Connect to index
            self.index = pc.Index(self.pinecone_index_name)
            logger.info("Connected to Pinecone index")
            
        except ImportError:
            raise ImportError("pinecone-client not installed. Install with: pip install pinecone-client")
        except Exception as e:
            raise Exception(f"Pinecone initialization failed: {str(e)}")
    
    def _initialize_faiss(self):
        """Initialize FAISS index."""
        try:
            import faiss
            
            # Create FAISS index (L2 distance, can be changed to inner product for cosine)
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
            
            # Wrap with IDMap to support custom IDs
            self.index = faiss.IndexIDMap(self.index)
            
            logger.info(f"FAISS index created with dimension {self.embedding_dimension}")
            
        except ImportError:
            raise ImportError("faiss-cpu not installed. Install with: pip install faiss-cpu")
        except Exception as e:
            raise Exception(f"FAISS initialization failed: {str(e)}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            Array of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def create_resume_text(self, resume_data: Dict) -> str:
        """
        Create searchable text from resume data.
        
        Args:
            resume_data: Parsed resume dictionary
            
        Returns:
            Concatenated text for embedding
        """
        parts = []
        
        # Add name
        if resume_data.get('name'):
            parts.append(f"Name: {resume_data['name']}")
        
        # Add summary
        if resume_data.get('summary'):
            parts.append(f"Summary: {resume_data['summary']}")
        
        # Add skills
        if resume_data.get('skills'):
            skills_text = ", ".join(resume_data['skills'])
            parts.append(f"Skills: {skills_text}")
        
        # Add experience
        if resume_data.get('experience_years'):
            parts.append(f"Experience: {resume_data['experience_years']} years")
        
        # Add education
        if resume_data.get('education'):
            for edu in resume_data['education']:
                parts.append(f"Education: {edu.get('degree', '')}")
        
        return " | ".join(parts)
    
    def upsert_resume(
        self,
        resume_id: str,
        resume_data: Dict,
        custom_text: Optional[str] = None
    ) -> bool:
        """
        Add or update resume in vector database.
        
        Args:
            resume_id: Unique identifier for the resume
            resume_data: Parsed resume dictionary
            custom_text: Optional custom text (otherwise generated from resume_data)
            
        Returns:
            True if successful
        """
        try:
            # Generate text for embedding
            text = custom_text if custom_text else self.create_resume_text(resume_data)
            
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Prepare metadata
            metadata = {
                "id": resume_id,
                "name": resume_data.get('name', 'Unknown'),
                "email": resume_data.get('email', ''),
                "phone": resume_data.get('phone', ''),
                "skills": json.dumps(resume_data.get('skills', [])),
                "experience_years": resume_data.get('experience_years', 0) or 0,
                "education_count": len(resume_data.get('education', [])),
                "text": text[:500]  # Store truncated text
            }
            
            # Upsert based on vector DB type
            if self.vector_db_type == "pinecone":
                self._upsert_pinecone(resume_id, embedding, metadata)
            elif self.vector_db_type == "faiss":
                self._upsert_faiss(resume_id, embedding, metadata)
            elif self.vector_db_type == "memory":
                self._upsert_memory(resume_id, embedding, metadata)
            else:
                raise RuntimeError("No vector database initialized")
            
            logger.info(f"Successfully upserted resume: {resume_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting resume {resume_id}: {e}")
            return False
    
    def _upsert_pinecone(self, resume_id: str, embedding: np.ndarray, metadata: Dict):
        """Upsert vector to Pinecone."""
        self.index.upsert(
            vectors=[
                {
                    "id": resume_id,
                    "values": embedding.tolist(),
                    "metadata": metadata
                }
            ]
        )
    
    def _upsert_faiss(self, resume_id: str, embedding: np.ndarray, metadata: Dict):
        """Upsert vector to FAISS."""
        # Generate numeric ID from string ID
        numeric_id = hash(resume_id) % (10 ** 10)
        
        # Add to index
        self.index.add_with_ids(
            embedding.reshape(1, -1).astype('float32'),
            np.array([numeric_id])
        )
        
        # Store metadata separately
        self.faiss_metadata[numeric_id] = metadata
    
    def _upsert_memory(self, resume_id: str, embedding: np.ndarray, metadata: Dict):
        """Upsert vector to in-memory storage."""
        self.memory_vectors[resume_id] = {
            'embedding': embedding,
            'metadata': metadata
        }
    
    def upsert_resumes_batch(
        self,
        resumes: List[Tuple[str, Dict]]
    ) -> Dict[str, bool]:
        """
        Batch upsert multiple resumes.
        
        Args:
            resumes: List of (resume_id, resume_data) tuples
            
        Returns:
            Dictionary mapping resume_id to success status
        """
        results = {}
        
        for resume_id, resume_data in resumes:
            success = self.upsert_resume(resume_id, resume_data)
            results[resume_id] = success
        
        return results
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar resumes.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of search results with scores and metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Search based on vector DB type
            if self.vector_db_type == "pinecone":
                return self._search_pinecone(query_embedding, top_k, filter_dict)
            elif self.vector_db_type == "faiss":
                return self._search_faiss(query_embedding, top_k)
            elif self.vector_db_type == "memory":
                return self._search_memory(query_embedding, top_k)
            else:
                raise RuntimeError("No vector database initialized")
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def _search_pinecone(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        filter_dict: Optional[Dict]
    ) -> List[Dict]:
        """Search in Pinecone."""
        results = self.index.query(
            vector=query_embedding.tolist(),
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        search_results = []
        for match in results['matches']:
            result = {
                'id': match['id'],
                'score': match['score'],
                'metadata': match.get('metadata', {})
            }
            search_results.append(result)
        
        return search_results
    
    def _search_faiss(
        self,
        query_embedding: np.ndarray,
        top_k: int
    ) -> List[Dict]:
        """Search in FAISS."""
        # Search in FAISS
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            top_k
        )
        
        search_results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # No more results
                break
            
            # Convert distance to similarity score (inverse)
            score = 1.0 / (1.0 + distance)
            
            result = {
                'id': str(idx),
                'score': float(score),
                'metadata': self.faiss_metadata.get(idx, {})
            }
            search_results.append(result)
        
        return search_results
    
    def _search_memory(
        self,
        query_embedding: np.ndarray,
        top_k: int
    ) -> List[Dict]:
        """Search in in-memory storage using cosine similarity."""
        if not self.memory_vectors:
            return []
        
        # Calculate cosine similarity for all vectors
        similarities = []
        for resume_id, data in self.memory_vectors.items():
            similarity = self._cosine_similarity(query_embedding, data['embedding'])
            similarities.append({
                'id': resume_id,
                'score': float(similarity),
                'metadata': data['metadata']
            })
        
        # Sort by score descending and return top_k
        similarities.sort(key=lambda x: x['score'], reverse=True)
        return similarities[:top_k]
    
    def compare_resume_to_job(
        self,
        resume_data: Dict,
        job_description: str
    ) -> float:
        """
        Compare resume to job description using cosine similarity.
        
        Args:
            resume_data: Parsed resume dictionary
            job_description: Job description text
            
        Returns:
            Similarity score (0-1)
        """
        # Generate texts
        resume_text = self.create_resume_text(resume_data)
        
        # Generate embeddings
        embeddings = self.generate_embeddings([resume_text, job_description])
        resume_emb = embeddings[0]
        job_emb = embeddings[1]
        
        # Calculate cosine similarity
        similarity = self._cosine_similarity(resume_emb, job_emb)
        
        return float(similarity)
    
    def rank_resumes(
        self,
        resumes: List[Dict],
        job_description: str
    ) -> List[Tuple[Dict, float]]:
        """
        Rank multiple resumes against a job description.
        
        Args:
            resumes: List of parsed resume dictionaries
            job_description: Job description text
            
        Returns:
            List of (resume, score) tuples sorted by score descending
        """
        scored_resumes = []
        
        for resume in resumes:
            score = self.compare_resume_to_job(resume, job_description)
            scored_resumes.append((resume, score))
        
        # Sort by score descending
        scored_resumes.sort(key=lambda x: x[1], reverse=True)
        
        return scored_resumes
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def get_stats(self) -> Dict:
        """Get vector database statistics."""
        stats = {
            "vector_db_type": self.vector_db_type,
            "embedding_dimension": self.embedding_dimension,
            "model_name": self.model.get_sentence_embedding_dimension()
        }
        
        if self.vector_db_type == "pinecone":
            index_stats = self.index.describe_index_stats()
            stats["total_vectors"] = index_stats.get('total_vector_count', 0)
        elif self.vector_db_type == "faiss":
            stats["total_vectors"] = self.index.ntotal
        elif self.vector_db_type == "memory":
            stats["total_vectors"] = len(self.memory_vectors)
        
        return stats
    
    def delete_resume(self, resume_id: str) -> bool:
        """
        Delete resume from vector database.
        
        Args:
            resume_id: Resume identifier
            
        Returns:
            True if successful
        """
        try:
            if self.vector_db_type == "pinecone":
                self.index.delete(ids=[resume_id])
            elif self.vector_db_type == "faiss":
                # FAISS doesn't support individual deletion easily
                # Would need to rebuild index
                logger.warning("FAISS doesn't support individual deletion")
                return False
            
            logger.info(f"Deleted resume: {resume_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting resume {resume_id}: {e}")
            return False
    
    def save_faiss_index(self, filepath: str = "faiss_index.bin"):
        """Save FAISS index and metadata to disk."""
        if self.vector_db_type != "faiss":
            logger.warning("Not using FAISS, cannot save")
            return
        
        try:
            import faiss
            
            # Save index
            faiss.write_index(self.index, filepath)
            
            # Save metadata
            metadata_path = filepath.replace('.bin', '_metadata.json')
            with open(metadata_path, 'w') as f:
                # Convert numpy int keys to strings for JSON
                json_metadata = {str(k): v for k, v in self.faiss_metadata.items()}
                json.dump(json_metadata, f)
            
            logger.info(f"FAISS index saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def load_faiss_index(self, filepath: str = "faiss_index.bin"):
        """Load FAISS index and metadata from disk."""
        if self.vector_db_type != "faiss":
            logger.warning("Not using FAISS, cannot load")
            return
        
        try:
            import faiss
            
            # Load index
            self.index = faiss.read_index(filepath)
            
            # Load metadata
            metadata_path = filepath.replace('.bin', '_metadata.json')
            with open(metadata_path, 'r') as f:
                json_metadata = json.load(f)
                # Convert string keys back to integers
                self.faiss_metadata = {int(k): v for k, v in json_metadata.items()}
            
            logger.info(f"FAISS index loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
    
    # Public method aliases for consistent API
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text (alias for generate_embedding).
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        return self.generate_embedding(text)
    
    def upsert(self, resume_id: str, resume_data: Dict, custom_text: Optional[str] = None) -> bool:
        """
        Add or update resume (alias for upsert_resume).
        
        Args:
            resume_id: Unique identifier for the resume
            resume_data: Parsed resume dictionary
            custom_text: Optional custom text
            
        Returns:
            True if successful
        """
        return self.upsert_resume(resume_id, resume_data, custom_text)
    
    def query(self, query_text: str, top_k: int = 10, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar resumes (alias for search).
        
        Args:
            query_text: Search query text
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of search results with scores and metadata
        """
        return self.search(query_text, top_k, filter_dict)
    
    def clear(self) -> bool:
        """
        Clear all vectors from the database.
        
        Returns:
            True if successful
        """
        try:
            if self.vector_db_type == "pinecone":
                # Delete all vectors in Pinecone
                self.index.delete(delete_all=True)
                logger.info("Cleared all vectors from Pinecone")
            elif self.vector_db_type == "faiss":
                # Recreate FAISS index
                self._initialize_faiss()
                self.faiss_metadata = {}
                logger.info("Cleared all vectors from FAISS")
            elif self.vector_db_type == "memory":
                # Clear in-memory storage
                self.memory_vectors = {}
                logger.info("Cleared all vectors from memory")
            return True
        except Exception as e:
            logger.error(f"Error clearing vectors: {e}")
            return False


# Convenience functions
def create_embeddings_manager(
    pinecone_api_key: Optional[str] = None,
    use_faiss_fallback: bool = True
) -> EmbeddingsManager:
    """
    Create embeddings manager with automatic configuration.
    
    Args:
        pinecone_api_key: Optional Pinecone API key
        use_faiss_fallback: Use FAISS if Pinecone not available
        
    Returns:
        Configured EmbeddingsManager instance
    """
    return EmbeddingsManager(
        pinecone_api_key=pinecone_api_key,
        use_faiss_fallback=use_faiss_fallback
    )
