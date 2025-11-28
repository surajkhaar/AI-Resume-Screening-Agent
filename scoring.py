"""
Resume Scoring Module

Advanced scoring system that combines multiple signals:
- Skill match score
- Experience score
- Education score
- Semantic similarity score

Returns weighted final score with per-feature breakdown.
"""

import re
import os
from typing import Dict, List, Optional, Set, Tuple
import numpy as np
from dataclasses import dataclass, asdict
import logging

# Optional OpenAI import for explainability
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ScoreBreakdown:
    """Breakdown of individual scoring components."""
    skill_match_score: float
    experience_score: float
    education_score: float
    semantic_similarity_score: float
    final_score: float
    
    # Additional metadata
    matched_skills: List[str]
    missing_skills: List[str]
    experience_years: Optional[float]
    required_experience: Optional[float]
    has_required_degree: bool
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def __repr__(self) -> str:
        return (
            f"ScoreBreakdown(\n"
            f"  Final Score: {self.final_score:.2%}\n"
            f"  - Skills: {self.skill_match_score:.2%} ({len(self.matched_skills)} matched)\n"
            f"  - Experience: {self.experience_score:.2%}\n"
            f"  - Education: {self.education_score:.2%}\n"
            f"  - Semantic: {self.semantic_similarity_score:.2%}\n"
            f")"
        )


@dataclass
class MatchExplanation:
    """AI-generated explanation for candidate match."""
    summary: str  # Max 120 words explanation
    top_reasons: List[str]  # Top 3 reasons for match/mismatch
    recommendation: str  # "Strong Match", "Good Match", "Weak Match", etc.
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def __repr__(self) -> str:
        reasons_str = "\n".join([f"  {i+1}. {reason}" for i, reason in enumerate(self.top_reasons)])
        return (
            f"MatchExplanation(\n"
            f"  Recommendation: {self.recommendation}\n"
            f"  Summary: {self.summary}\n"
            f"  Top Reasons:\n{reasons_str}\n"
            f")"
        )


class ResumeScorer:
    """
    Advanced resume scoring system with multiple weighted components.
    """
    
    def __init__(
        self,
        skill_weight: float = 0.35,
        experience_weight: float = 0.25,
        education_weight: float = 0.15,
        semantic_weight: float = 0.25,
        embeddings_manager=None
    ):
        """
        Initialize scorer with component weights.
        
        Args:
            skill_weight: Weight for skill matching (default: 0.35)
            experience_weight: Weight for experience (default: 0.25)
            education_weight: Weight for education (default: 0.15)
            semantic_weight: Weight for semantic similarity (default: 0.25)
            embeddings_manager: EmbeddingsManager instance for semantic scoring
        """
        # Validate weights sum to 1.0
        total_weight = skill_weight + experience_weight + education_weight + semantic_weight
        if not np.isclose(total_weight, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        self.skill_weight = skill_weight
        self.experience_weight = experience_weight
        self.education_weight = education_weight
        self.semantic_weight = semantic_weight
        self.embeddings_manager = embeddings_manager
    
    def score_resume(
        self,
        resume_data: Dict,
        job_description: str,
        required_skills: Optional[List[str]] = None,
        required_experience: Optional[float] = None,
        required_degree: Optional[str] = None
    ) -> ScoreBreakdown:
        """
        Calculate comprehensive resume score.
        
        Args:
            resume_data: Parsed resume dictionary
            job_description: Job description text
            required_skills: List of required skills (optional, will extract from JD)
            required_experience: Required years of experience (optional)
            required_degree: Required degree type (optional)
            
        Returns:
            ScoreBreakdown with final score and component scores
        """
        # Extract requirements from job description if not provided
        if required_skills is None:
            required_skills = self._extract_skills_from_text(job_description)
        
        if required_experience is None:
            required_experience = self._extract_required_experience(job_description)
        
        if required_degree is None:
            required_degree = self._extract_required_degree(job_description)
        
        # Calculate individual scores
        skill_score, matched_skills, missing_skills = self._calculate_skill_match_score(
            resume_data.get('skills', []),
            required_skills
        )
        
        experience_score = self._calculate_experience_score(
            resume_data.get('experience_years'),
            required_experience
        )
        
        education_score = self._calculate_education_score(
            resume_data.get('education', []),
            required_degree
        )
        
        semantic_score = self._calculate_semantic_similarity_score(
            resume_data,
            job_description
        )
        
        # Calculate weighted final score
        final_score = (
            self.skill_weight * skill_score +
            self.experience_weight * experience_score +
            self.education_weight * education_score +
            self.semantic_weight * semantic_score
        )
        
        # Create breakdown
        breakdown = ScoreBreakdown(
            skill_match_score=skill_score,
            experience_score=experience_score,
            education_score=education_score,
            semantic_similarity_score=semantic_score,
            final_score=final_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            experience_years=resume_data.get('experience_years'),
            required_experience=required_experience,
            has_required_degree=education_score > 0
        )
        
        return breakdown
    
    def _calculate_skill_match_score(
        self,
        resume_skills: List[str],
        required_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculate skill match score based on overlap.
        
        Args:
            resume_skills: Skills from resume
            required_skills: Required skills from job description
            
        Returns:
            Tuple of (score, matched_skills, missing_skills)
        """
        if not required_skills:
            return 1.0, [], []
        
        # Normalize skills for comparison (lowercase, strip)
        resume_skills_normalized = {skill.lower().strip() for skill in resume_skills}
        required_skills_normalized = {skill.lower().strip() for skill in required_skills}
        
        # Find matches
        matched = resume_skills_normalized & required_skills_normalized
        missing = required_skills_normalized - resume_skills_normalized
        
        # Calculate score
        if len(required_skills_normalized) == 0:
            score = 1.0
        else:
            score = len(matched) / len(required_skills_normalized)
        
        # Convert back to original case for display
        matched_skills = [s for s in resume_skills if s.lower().strip() in matched]
        missing_skills = list(missing)
        
        return score, matched_skills, missing_skills
    
    def _calculate_experience_score(
        self,
        resume_experience: Optional[float],
        required_experience: Optional[float]
    ) -> float:
        """
        Calculate experience score (normalized).
        
        Args:
            resume_experience: Years of experience from resume
            required_experience: Required years of experience
            
        Returns:
            Normalized score (0.0 to 1.0)
        """
        if required_experience is None or required_experience == 0:
            return 1.0  # No requirement, full score
        
        if resume_experience is None:
            return 0.0  # No experience data
        
        # Score based on how much experience exceeds requirement
        if resume_experience >= required_experience:
            # Full score if meets requirement
            # Bonus for exceeding (capped at 1.0)
            excess = min((resume_experience - required_experience) / required_experience, 0.2)
            return min(1.0, 1.0 + excess)
        else:
            # Partial score if below requirement
            # Linear scale: 0 experience = 0 score, required experience = 1.0 score
            return resume_experience / required_experience
    
    def _calculate_education_score(
        self,
        resume_education: List[Dict],
        required_degree: Optional[str]
    ) -> float:
        """
        Calculate education score (binary: has required degree or not).
        
        Args:
            resume_education: List of education entries from resume
            required_degree: Required degree type (e.g., "Bachelor", "Master", "PhD")
            
        Returns:
            Binary score (0.0 or 1.0)
        """
        if not required_degree:
            return 1.0  # No requirement, full score
        
        if not resume_education:
            return 0.0  # No education data
        
        # Degree hierarchy
        degree_hierarchy = {
            'phd': 4,
            'doctorate': 4,
            'ph.d': 4,
            'doctor': 4,
            'master': 3,
            'ms': 3,
            'm.s': 3,
            'ma': 3,
            'm.a': 3,
            'mba': 3,
            'bachelor': 2,
            'bs': 2,
            'b.s': 2,
            'ba': 2,
            'b.a': 2,
            'associate': 1,
            'diploma': 0.5,
            'certificate': 0.3
        }
        
        # Get required degree level
        required_level = 0
        required_normalized = required_degree.lower().strip()
        for degree_type, level in degree_hierarchy.items():
            if degree_type in required_normalized:
                required_level = max(required_level, level)
                break
        
        # Check if any resume degree meets requirement
        for edu in resume_education:
            degree_text = edu.get('degree', '').lower().strip()
            
            for degree_type, level in degree_hierarchy.items():
                if degree_type in degree_text:
                    if level >= required_level:
                        return 1.0  # Has required or higher degree
        
        return 0.0  # Does not meet degree requirement
    
    def _calculate_semantic_similarity_score(
        self,
        resume_data: Dict,
        job_description: str
    ) -> float:
        """
        Calculate semantic similarity using embeddings.
        
        Args:
            resume_data: Parsed resume dictionary
            job_description: Job description text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not self.embeddings_manager:
            # Fallback: simple keyword-based similarity
            return self._fallback_text_similarity(resume_data, job_description)
        
        try:
            # Use embeddings manager to calculate similarity
            score = self.embeddings_manager.compare_resume_to_job(
                resume_data,
                job_description
            )
            return score
        except Exception as e:
            # Fallback on error
            print(f"Semantic similarity calculation failed: {e}")
            return self._fallback_text_similarity(resume_data, job_description)
    
    def _fallback_text_similarity(
        self,
        resume_data: Dict,
        job_description: str
    ) -> float:
        """
        Fallback text similarity when embeddings not available.
        Simple keyword overlap calculation.
        
        Args:
            resume_data: Parsed resume dictionary
            job_description: Job description text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Create resume text
        resume_parts = []
        if resume_data.get('summary'):
            resume_parts.append(resume_data['summary'])
        if resume_data.get('skills'):
            resume_parts.append(' '.join(resume_data['skills']))
        
        resume_text = ' '.join(resume_parts).lower()
        jd_text = job_description.lower()
        
        # Extract words
        resume_words = set(re.findall(r'\b\w+\b', resume_text))
        jd_words = set(re.findall(r'\b\w+\b', jd_text))
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        resume_words -= stop_words
        jd_words -= stop_words
        
        # Calculate Jaccard similarity
        if not jd_words:
            return 0.5
        
        intersection = len(resume_words & jd_words)
        union = len(resume_words | jd_words)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract skills mentioned in job description.
        
        Args:
            text: Job description text
            
        Returns:
            List of identified skills
        """
        # Common technical skills database
        skill_database = [
            # Programming languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
            'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl',
            
            # Web frameworks
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
            'node.js', 'next.js', 'fastapi', 'asp.net', 'laravel',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'dynamodb', 'cassandra', 'oracle', 'sqlite',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
            'ansible', 'ci/cd', 'git', 'github', 'gitlab',
            
            # Data & ML
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'spark', 'hadoop', 'kafka',
            
            # Other
            'agile', 'scrum', 'jira', 'rest api', 'graphql', 'microservices',
            'testing', 'unit testing', 'tdd'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_database:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def _extract_required_experience(self, text: str) -> Optional[float]:
        """
        Extract required years of experience from job description.
        
        Args:
            text: Job description text
            
        Returns:
            Required years or None
        """
        # Patterns for extracting experience requirements
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'minimum\s+(?:of\s+)?(\d+)\+?\s*years?',
            r'at\s+least\s+(\d+)\+?\s*years?',
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                return float(matches[0])
        
        return None
    
    def _extract_required_degree(self, text: str) -> Optional[str]:
        """
        Extract required degree from job description.
        
        Args:
            text: Job description text
            
        Returns:
            Required degree type or None
        """
        text_lower = text.lower()
        
        # Check for degree requirements
        degree_keywords = {
            'phd': ['phd', 'ph.d', 'doctorate', 'doctoral'],
            'master': ['master', 'masters', 'ms', 'm.s', 'ma', 'm.a', 'mba'],
            'bachelor': ['bachelor', 'bachelors', 'bs', 'b.s', 'ba', 'b.a']
        }
        
        for degree_type, keywords in degree_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Check if it's marked as required
                    context_patterns = [
                        f'require[ds]?.*{keyword}',
                        f'{keyword}.*require[ds]?',
                        f'must have.*{keyword}',
                        f'{keyword}.*degree',
                    ]
                    
                    for pattern in context_patterns:
                        if re.search(pattern, text_lower):
                            return degree_type.capitalize()
        
        return None
    
    def explain_match(
        self,
        resume_data: Dict,
        job_description: str,
        score_breakdown: Optional[ScoreBreakdown] = None,
        api_key: Optional[str] = None
    ) -> MatchExplanation:
        """
        Generate AI-powered explanation for why a candidate matches or doesn't match.
        
        Uses OpenAI GPT with a deterministic prompt and few-shot examples to produce:
        - A concise summary (max 120 words)
        - Top 3 reasons for match/mismatch
        - Overall recommendation
        
        Args:
            resume_data: Parsed resume dictionary
            job_description: Job description text
            score_breakdown: Optional pre-computed score breakdown
            api_key: Optional OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            
        Returns:
            MatchExplanation with summary and top reasons
            
        Raises:
            ImportError: If OpenAI library not installed
            ValueError: If API key not provided
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI library not installed. Install with: pip install openai"
            )
        
        # Get or compute score breakdown
        if score_breakdown is None:
            score_breakdown = self.score_resume(resume_data, job_description)
        
        # Initialize OpenAI client
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        client = OpenAI(api_key=api_key)
        
        # Prepare candidate info
        candidate_name = resume_data.get("name", "Candidate")
        candidate_skills = resume_data.get("skills", [])
        candidate_experience = resume_data.get("experience_years", 0)
        candidate_education = resume_data.get("education", [])
        education_str = ", ".join([edu.get("degree", "") for edu in candidate_education]) if candidate_education else "Not specified"
        
        # Build prompt with few-shot examples
        prompt = f"""You are an expert recruiter analyzing candidate fit for a job position. Provide a concise explanation of why a candidate matches or doesn't match the job requirements.

INSTRUCTIONS:
- Write a summary in 120 words or less
- List exactly 3 key reasons (bullet points)
- Provide a clear recommendation
- Be specific and reference actual skills, experience, and qualifications

FEW-SHOT EXAMPLES:

Example 1:
Candidate: John Smith
Skills: Python, Django, PostgreSQL, AWS
Experience: 6 years
Education: Master's in Computer Science
Job: Senior Backend Engineer (5+ years, Python/Django, Master's preferred)
Final Score: 87%

Response:
Summary: John Smith is an excellent fit for the Senior Backend Engineer role. With 6 years of experience and a Master's degree, he exceeds the minimum qualifications. His technical skills align perfectly with the job requirements, particularly his expertise in Python and Django. While he has strong AWS experience, expanding his knowledge in container orchestration technologies would be beneficial.

Top 3 Reasons:
1. Strong technical match: Possesses all core required skills (Python, Django, PostgreSQL) with demonstrated AWS cloud experience
2. Experience level exceeds requirement: 6 years of experience surpasses the 5+ years requirement, indicating senior-level capability
3. Educational qualification met: Master's in Computer Science aligns with preferred degree requirement

Recommendation: Strong Match - Highly recommended for interview

---

Example 2:
Candidate: Sarah Lee
Skills: JavaScript, React, Node.js
Experience: 3 years
Education: Bachelor's in Information Systems
Job: Machine Learning Engineer (5+ years, Python, TensorFlow, Master's required)
Final Score: 34%

Response:
Summary: Sarah Lee does not align well with the Machine Learning Engineer position requirements. Her background is primarily in web development with JavaScript technologies, lacking the specialized machine learning skills and Python expertise needed for this role. Additionally, her 3 years of experience falls short of the 5+ years requirement, and her Bachelor's degree doesn't meet the Master's degree requirement for this position.

Top 3 Reasons:
1. Skills mismatch: Specializes in JavaScript/React/Node.js rather than required Python and machine learning frameworks (TensorFlow/PyTorch)
2. Insufficient experience: 3 years of experience is below the 5+ years requirement, suggesting lack of senior-level ML expertise
3. Education gap: Bachelor's degree doesn't meet the required Master's degree in Computer Science or related field

Recommendation: Weak Match - Not suitable for this position

---

Example 3:
Candidate: Michael Chen
Skills: Python, Machine Learning, scikit-learn, Docker
Experience: 4 years
Education: Master's in Data Science
Job: Machine Learning Engineer (5+ years, Python, TensorFlow, Master's preferred)
Final Score: 68%

Response:
Summary: Michael Chen shows good potential for the Machine Learning Engineer role with solid foundational qualifications. His Master's in Data Science and Python/ML skills demonstrate relevant expertise. However, he falls slightly short with 4 years of experience versus the 5+ required, and lacks specific experience with TensorFlow mentioned in the job requirements. His Docker skills indicate DevOps awareness which is valuable for ML deployment.

Top 3 Reasons:
1. Good ML foundation: Strong Python and machine learning background, though experience is with scikit-learn rather than required TensorFlow
2. Education requirement met: Master's in Data Science aligns well with the preferred Master's degree requirement
3. Slightly under experience threshold: 4 years versus 5+ required, but close enough to demonstrate relevant capabilities

Recommendation: Good Match - Worth considering with focus on TensorFlow experience gap

---

NOW ANALYZE THIS CANDIDATE:

Candidate: {candidate_name}
Skills: {", ".join(candidate_skills) if candidate_skills else "Not specified"}
Experience: {candidate_experience} years
Education: {education_str}
Job Description: {job_description[:500]}...
Final Score: {score_breakdown.final_score:.0%}
Matched Skills: {", ".join(score_breakdown.matched_skills) if score_breakdown.matched_skills else "None"}
Missing Skills: {", ".join(score_breakdown.missing_skills) if score_breakdown.missing_skills else "None"}

Provide your analysis in the exact same format:
Summary: [120 words or less]

Top 3 Reasons:
1. [Reason 1]
2. [Reason 2]
3. [Reason 3]

Recommendation: [Strong Match/Good Match/Moderate Match/Weak Match]"""

        try:
            # Call OpenAI with deterministic settings
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert recruiter providing concise, actionable candidate assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temperature for consistency
                max_tokens=500,
                top_p=0.9
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Extract sections
            summary_match = re.search(r'Summary:\s*(.+?)(?=\n\nTop 3 Reasons:|Top 3 Reasons:)', content, re.DOTALL)
            reasons_match = re.search(r'Top 3 Reasons:\s*\n(.+?)(?=\n\nRecommendation:|Recommendation:)', content, re.DOTALL)
            recommendation_match = re.search(r'Recommendation:\s*(.+?)$', content, re.DOTALL)
            
            # Parse summary
            summary = summary_match.group(1).strip() if summary_match else "Unable to generate summary."
            
            # Parse reasons (extract lines starting with numbers)
            top_reasons = []
            if reasons_match:
                reasons_text = reasons_match.group(1).strip()
                for line in reasons_text.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        # Remove numbering and clean
                        reason = re.sub(r'^\d+\.\s*', '', line)
                        reason = re.sub(r'^-\s*', '', reason)
                        if reason:
                            top_reasons.append(reason)
            
            # Limit to exactly 3 reasons
            if len(top_reasons) < 3:
                top_reasons.extend(["Additional analysis needed"] * (3 - len(top_reasons)))
            top_reasons = top_reasons[:3]
            
            # Parse recommendation
            recommendation = recommendation_match.group(1).strip() if recommendation_match else "Unable to determine"
            
            return MatchExplanation(
                summary=summary,
                top_reasons=top_reasons,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            # Return fallback explanation based on score
            if score_breakdown.final_score >= 0.8:
                rec = "Strong Match"
                summary = f"{candidate_name} shows strong alignment with the position requirements."
            elif score_breakdown.final_score >= 0.6:
                rec = "Good Match"
                summary = f"{candidate_name} demonstrates good fit for the position with some areas for improvement."
            elif score_breakdown.final_score >= 0.4:
                rec = "Moderate Match"
                summary = f"{candidate_name} has moderate alignment with some gaps in key requirements."
            else:
                rec = "Weak Match"
                summary = f"{candidate_name} does not align well with the core position requirements."
            
            return MatchExplanation(
                summary=summary,
                top_reasons=[
                    f"Skills match: {len(score_breakdown.matched_skills)} matched, {len(score_breakdown.missing_skills)} missing",
                    f"Experience: {score_breakdown.experience_years} years (required: {score_breakdown.required_experience})",
                    f"Education: {'Meets' if score_breakdown.has_required_degree else 'Does not meet'} requirements"
                ],
                recommendation=rec
            )
    
    def batch_score_resumes(
        self,
        resumes: List[Dict],
        job_description: str,
        required_skills: Optional[List[str]] = None,
        required_experience: Optional[float] = None,
        required_degree: Optional[str] = None
    ) -> List[Tuple[Dict, ScoreBreakdown]]:
        """
        Score multiple resumes against a job description.
        
        Args:
            resumes: List of parsed resume dictionaries
            job_description: Job description text
            required_skills: Required skills (optional)
            required_experience: Required experience (optional)
            required_degree: Required degree (optional)
            
        Returns:
            List of (resume, score_breakdown) tuples, sorted by final score
        """
        scored_resumes = []
        
        for resume in resumes:
            breakdown = self.score_resume(
                resume,
                job_description,
                required_skills,
                required_experience,
                required_degree
            )
            scored_resumes.append((resume, breakdown))
        
        # Sort by final score (descending)
        scored_resumes.sort(key=lambda x: x[1].final_score, reverse=True)
        
        return scored_resumes


# Convenience functions
def score_resume(
    resume_data: Dict,
    job_description: str,
    embeddings_manager=None,
    **kwargs
) -> ScoreBreakdown:
    """
    Convenience function to score a single resume.
    
    Args:
        resume_data: Parsed resume dictionary
        job_description: Job description text
        embeddings_manager: Optional embeddings manager
        **kwargs: Additional scoring parameters
        
    Returns:
        ScoreBreakdown with results
    """
    scorer = ResumeScorer(embeddings_manager=embeddings_manager)
    return scorer.score_resume(resume_data, job_description, **kwargs)


def score_resumes_batch(
    resumes: List[Dict],
    job_description: str,
    embeddings_manager=None,
    **kwargs
) -> List[Tuple[Dict, ScoreBreakdown]]:
    """
    Convenience function to score multiple resumes.
    
    Args:
        resumes: List of parsed resume dictionaries
        job_description: Job description text
        embeddings_manager: Optional embeddings manager
        **kwargs: Additional scoring parameters
        
    Returns:
        List of (resume, score_breakdown) tuples
    """
    scorer = ResumeScorer(embeddings_manager=embeddings_manager)
    return scorer.batch_score_resumes(resumes, job_description, **kwargs)


def explain_match(
    resume_data: Dict,
    job_description: str,
    score_breakdown: Optional[ScoreBreakdown] = None,
    embeddings_manager=None,
    api_key: Optional[str] = None
) -> MatchExplanation:
    """
    Convenience function to generate AI explanation for a candidate match.
    
    Args:
        resume_data: Parsed resume dictionary
        job_description: Job description text
        score_breakdown: Optional pre-computed score breakdown
        embeddings_manager: Optional embeddings manager
        api_key: Optional OpenAI API key
        
    Returns:
        MatchExplanation with summary and top reasons
    """
    scorer = ResumeScorer(embeddings_manager=embeddings_manager)
    return scorer.explain_match(resume_data, job_description, score_breakdown, api_key)
