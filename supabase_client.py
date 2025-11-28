"""
Supabase Client for Resume Analyzer
Handles database operations for storing resume analysis results
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import json


class SupabaseManager:
    """Manager for Supabase database operations"""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase client
        
        Args:
            url: Supabase project URL (defaults to SUPABASE_URL env var)
            key: Supabase API key (defaults to SUPABASE_KEY env var)
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError(
                "Supabase credentials not found. "
                "Set SUPABASE_URL and SUPABASE_KEY environment variables"
            )
        
        self.client: Client = create_client(self.url, self.key)
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """
        Check if the resume_analyses table exists
        
        Note: You need to create this table in Supabase with the following schema:
        
        CREATE TABLE resume_analyses (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            job_description TEXT NOT NULL,
            candidate_name TEXT NOT NULL,
            candidate_email TEXT,
            candidate_phone TEXT,
            final_score FLOAT NOT NULL,
            skill_match_score FLOAT,
            experience_score FLOAT,
            education_score FLOAT,
            semantic_score FLOAT,
            experience_years INTEGER,
            required_experience INTEGER,
            has_required_degree BOOLEAN,
            matched_skills TEXT[],
            missing_skills TEXT[],
            resume_data JSONB,
            score_breakdown JSONB,
            explanation_summary TEXT,
            explanation_reasons TEXT[],
            explanation_recommendation TEXT,
            filename TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX idx_timestamp ON resume_analyses(timestamp DESC);
        CREATE INDEX idx_candidate_name ON resume_analyses(candidate_name);
        CREATE INDEX idx_final_score ON resume_analyses(final_score DESC);
        """
        # This is just a placeholder - actual table creation should be done via Supabase UI or SQL editor
        pass
    
    def store_analysis(
        self,
        job_description: str,
        resume_data: Dict[str, Any],
        score_breakdown: Dict[str, Any],
        explanation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a resume analysis result in Supabase
        
        Args:
            job_description: The job description text
            resume_data: Parsed resume data
            score_breakdown: Scoring breakdown
            explanation: Optional LLM explanation
            
        Returns:
            Inserted record from database
        """
        # Prepare the data for insertion
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "job_description": job_description,
            "candidate_name": resume_data.get("name", "Unknown"),
            "candidate_email": resume_data.get("email"),
            "candidate_phone": resume_data.get("phone"),
            "final_score": score_breakdown.get("final_score", 0),
            "skill_match_score": score_breakdown.get("skill_match_score"),
            "experience_score": score_breakdown.get("experience_score"),
            "education_score": score_breakdown.get("education_score"),
            "semantic_score": score_breakdown.get("semantic_similarity_score"),
            "experience_years": score_breakdown.get("experience_years", 0),
            "required_experience": score_breakdown.get("required_experience"),
            "has_required_degree": score_breakdown.get("has_required_degree", False),
            "matched_skills": score_breakdown.get("matched_skills", []),
            "missing_skills": score_breakdown.get("missing_skills", []),
            "resume_data": resume_data,
            "score_breakdown": score_breakdown,
            "filename": resume_data.get("filename", "unknown.pdf")
        }
        
        # Add explanation data if available
        if explanation:
            data["explanation_summary"] = explanation.get("summary")
            data["explanation_reasons"] = explanation.get("top_reasons", [])
            data["explanation_recommendation"] = explanation.get("recommendation")
        
        # Insert into database
        try:
            response = self.client.table("resume_analyses").insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"Error storing analysis: {str(e)}")
            raise
    
    def store_batch_analyses(
        self,
        job_description: str,
        analyses: List[tuple]
    ) -> List[Dict[str, Any]]:
        """
        Store multiple resume analyses in batch
        
        Args:
            job_description: The job description text
            analyses: List of tuples (resume_data, score_breakdown, explanation)
            
        Returns:
            List of inserted records
        """
        records = []
        
        for analysis in analyses:
            if len(analysis) == 2:
                resume_data, score_breakdown = analysis
                explanation = None
            else:
                resume_data, score_breakdown, explanation = analysis
            
            try:
                record = self.store_analysis(
                    job_description,
                    resume_data,
                    score_breakdown,
                    explanation
                )
                records.append(record)
            except Exception as e:
                print(f"Error storing analysis for {resume_data.get('name')}: {str(e)}")
                continue
        
        return records
    
    def get_recent_analyses(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get recent resume analyses
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of analysis records
        """
        try:
            response = (
                self.client.table("resume_analyses")
                .select("*")
                .order("timestamp", desc=True)
                .limit(limit)
                .offset(offset)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching analyses: {str(e)}")
            return []
    
    def get_analyses_by_candidate(
        self,
        candidate_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get all analyses for a specific candidate
        
        Args:
            candidate_name: Name of the candidate
            
        Returns:
            List of analysis records for this candidate
        """
        try:
            response = (
                self.client.table("resume_analyses")
                .select("*")
                .eq("candidate_name", candidate_name)
                .order("timestamp", desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching candidate analyses: {str(e)}")
            return []
    
    def get_analyses_by_score_range(
        self,
        min_score: float,
        max_score: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Get analyses within a score range
        
        Args:
            min_score: Minimum final score
            max_score: Maximum final score
            
        Returns:
            List of analysis records in score range
        """
        try:
            response = (
                self.client.table("resume_analyses")
                .select("*")
                .gte("final_score", min_score)
                .lte("final_score", max_score)
                .order("final_score", desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching analyses by score: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored analyses
        
        Returns:
            Dictionary with statistics
        """
        try:
            # Get all records (you might want to add pagination for large datasets)
            response = self.client.table("resume_analyses").select("*").execute()
            data = response.data
            
            if not data:
                return {
                    "total_analyses": 0,
                    "average_score": 0,
                    "strong_matches": 0,
                    "weak_matches": 0
                }
            
            total = len(data)
            avg_score = sum(r["final_score"] for r in data) / total
            strong = sum(1 for r in data if r["final_score"] >= 0.8)
            weak = sum(1 for r in data if r["final_score"] < 0.4)
            
            return {
                "total_analyses": total,
                "average_score": avg_score,
                "strong_matches": strong,
                "weak_matches": weak,
                "good_matches": sum(1 for r in data if 0.6 <= r["final_score"] < 0.8),
                "moderate_matches": sum(1 for r in data if 0.4 <= r["final_score"] < 0.6)
            }
        except Exception as e:
            print(f"Error fetching statistics: {str(e)}")
            return {}
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete a specific analysis
        
        Args:
            analysis_id: UUID of the analysis to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.table("resume_analyses").delete().eq("id", analysis_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting analysis: {str(e)}")
            return False
    
    def clear_old_analyses(self, days: int = 30) -> int:
        """
        Delete analyses older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of records deleted
        """
        try:
            from datetime import timedelta
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            response = (
                self.client.table("resume_analyses")
                .delete()
                .lt("timestamp", cutoff_date)
                .execute()
            )
            return len(response.data) if response.data else 0
        except Exception as e:
            print(f"Error clearing old analyses: {str(e)}")
            return 0


# Convenience functions
def get_supabase_manager(url: Optional[str] = None, key: Optional[str] = None) -> SupabaseManager:
    """
    Get a SupabaseManager instance
    
    Args:
        url: Optional Supabase URL
        key: Optional Supabase key
        
    Returns:
        SupabaseManager instance
    """
    return SupabaseManager(url, key)


def check_supabase_connection() -> bool:
    """
    Check if Supabase connection is available
    
    Returns:
        True if connection is available, False otherwise
    """
    try:
        manager = get_supabase_manager()
        manager.get_recent_analyses(limit=1)
        return True
    except Exception:
        return False
