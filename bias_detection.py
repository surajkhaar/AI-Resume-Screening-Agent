"""
Bias Detection and Reporting Module
Identifies potential biases in resume screening without inferring protected attributes
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set
import statistics
from collections import Counter


@dataclass
class BiasFlag:
    """Represents a potential bias warning"""
    severity: str  # "critical", "warning", "info"
    category: str  # e.g., "missing_data", "variance", "pattern"
    message: str
    affected_candidates: List[str]
    recommendation: str
    details: Dict[str, Any]


@dataclass
class BiasReport:
    """Complete bias detection report"""
    total_candidates: int
    flags: List[BiasFlag]
    summary: str
    
    def has_critical_flags(self) -> bool:
        """Check if report contains critical flags"""
        return any(flag.severity == "critical" for flag in self.flags)
    
    def has_warnings(self) -> bool:
        """Check if report contains warnings"""
        return any(flag.severity == "warning" for flag in self.flags)
    
    def get_flags_by_severity(self, severity: str) -> List[BiasFlag]:
        """Get all flags of a specific severity"""
        return [flag for flag in self.flags if flag.severity == severity]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export"""
        return {
            "total_candidates": self.total_candidates,
            "flags": [
                {
                    "severity": flag.severity,
                    "category": flag.category,
                    "message": flag.message,
                    "affected_candidates": flag.affected_candidates,
                    "recommendation": flag.recommendation,
                    "details": flag.details
                }
                for flag in self.flags
            ],
            "summary": self.summary,
            "has_critical_flags": self.has_critical_flags(),
            "has_warnings": self.has_warnings()
        }


class BiasDetector:
    """Detects potential biases in resume screening process"""
    
    def __init__(
        self,
        missing_field_threshold: float = 0.3,
        variance_threshold: float = 0.7,
        score_spread_threshold: float = 0.6
    ):
        """
        Initialize bias detector with configurable thresholds
        
        Args:
            missing_field_threshold: Fraction of candidates with missing fields to flag (0.3 = 30%)
            variance_threshold: Coefficient of variation threshold for extreme variance
            score_spread_threshold: Minimum score spread to avoid clustering
        """
        self.missing_field_threshold = missing_field_threshold
        self.variance_threshold = variance_threshold
        self.score_spread_threshold = score_spread_threshold
    
    def generate_report(
        self,
        resumes: List[Dict[str, Any]],
        score_breakdowns: Optional[List[Dict[str, Any]]] = None
    ) -> BiasReport:
        """
        Generate comprehensive bias report
        
        Args:
            resumes: List of parsed resume data
            score_breakdowns: Optional list of score breakdowns
            
        Returns:
            BiasReport with all detected flags
        """
        flags = []
        
        # Check for missing fields
        flags.extend(self._check_missing_fields(resumes))
        
        # Check for extreme variance in experience
        flags.extend(self._check_experience_variance(resumes))
        
        # Check for education distribution patterns
        flags.extend(self._check_education_patterns(resumes))
        
        # Check for skill diversity
        flags.extend(self._check_skill_diversity(resumes))
        
        # Check scoring patterns if available
        if score_breakdowns:
            flags.extend(self._check_scoring_patterns(resumes, score_breakdowns))
        
        # Check for incomplete parsing
        flags.extend(self._check_parsing_quality(resumes))
        
        # Check for data consistency
        flags.extend(self._check_data_consistency(resumes))
        
        # Generate summary
        summary = self._generate_summary(len(resumes), flags)
        
        return BiasReport(
            total_candidates=len(resumes),
            flags=flags,
            summary=summary
        )
    
    def _check_missing_fields(self, resumes: List[Dict[str, Any]]) -> List[BiasFlag]:
        """Check for missing critical fields"""
        flags = []
        
        critical_fields = ["name", "email", "skills", "experience_years"]
        
        for field in critical_fields:
            missing_candidates = []
            
            for resume in resumes:
                value = resume.get(field)
                
                # Check if field is missing or empty
                if value is None:
                    missing_candidates.append(resume.get("name", "Unknown"))
                elif isinstance(value, (list, str)) and not value:
                    missing_candidates.append(resume.get("name", "Unknown"))
                elif isinstance(value, (int, float)) and value == 0 and field == "experience_years":
                    # Note: 0 years experience is valid for entry-level
                    pass
            
            if missing_candidates:
                missing_rate = len(missing_candidates) / len(resumes)
                
                if missing_rate >= self.missing_field_threshold:
                    severity = "critical" if missing_rate >= 0.5 else "warning"
                    
                    flags.append(BiasFlag(
                        severity=severity,
                        category="missing_data",
                        message=f"High rate of missing '{field}' field ({missing_rate:.1%} of candidates)",
                        affected_candidates=missing_candidates,
                        recommendation=f"Review resume parsing for '{field}' extraction. Missing data may lead to unfair evaluation.",
                        details={
                            "field": field,
                            "missing_count": len(missing_candidates),
                            "missing_rate": missing_rate
                        }
                    ))
        
        return flags
    
    def _check_experience_variance(self, resumes: List[Dict[str, Any]]) -> List[BiasFlag]:
        """Check for extreme variance in experience distribution"""
        flags = []
        
        experience_years = [r.get("experience_years", 0) for r in resumes if r.get("experience_years") is not None]
        
        if len(experience_years) < 2:
            return flags
        
        # Calculate statistics
        mean_exp = statistics.mean(experience_years)
        
        if mean_exp == 0:
            return flags
        
        stdev_exp = statistics.stdev(experience_years) if len(experience_years) > 1 else 0
        cv = stdev_exp / mean_exp if mean_exp > 0 else 0  # Coefficient of variation
        
        # Check for extreme variance
        if cv > self.variance_threshold:
            # Identify candidates at extremes
            min_exp = min(experience_years)
            max_exp = max(experience_years)
            
            low_exp_candidates = [
                r.get("name", "Unknown") for r in resumes 
                if r.get("experience_years", 0) == min_exp
            ]
            
            high_exp_candidates = [
                r.get("name", "Unknown") for r in resumes 
                if r.get("experience_years", 0) == max_exp
            ]
            
            flags.append(BiasFlag(
                severity="warning",
                category="variance",
                message=f"Extreme variance in experience distribution (CV={cv:.2f})",
                affected_candidates=[],
                recommendation="Review if job requirements are clearly defined. Large experience spread may indicate unclear requirements or over-broad candidate pool.",
                details={
                    "mean_experience": round(mean_exp, 1),
                    "std_dev": round(stdev_exp, 1),
                    "coefficient_of_variation": round(cv, 2),
                    "min_experience": min_exp,
                    "max_experience": max_exp,
                    "range": max_exp - min_exp
                }
            ))
        
        return flags
    
    def _check_education_patterns(self, resumes: List[Dict[str, Any]]) -> List[BiasFlag]:
        """Check for suspicious education distribution patterns"""
        flags = []
        
        # Extract education levels
        education_levels = []
        no_education_candidates = []
        
        for resume in resumes:
            education = resume.get("education", [])
            
            if not education:
                no_education_candidates.append(resume.get("name", "Unknown"))
                education_levels.append("none")
            else:
                # Get highest degree
                degrees = [e.get("degree", "").lower() for e in education]
                
                if any("phd" in d or "doctorate" in d for d in degrees):
                    education_levels.append("phd")
                elif any("master" in d or "mba" in d or "ms" in d or "ma" in d for d in degrees):
                    education_levels.append("master")
                elif any("bachelor" in d or "bs" in d or "ba" in d for d in degrees):
                    education_levels.append("bachelor")
                elif any("associate" in d for d in degrees):
                    education_levels.append("associate")
                else:
                    education_levels.append("other")
        
        # Check for missing education data
        if len(no_education_candidates) / len(resumes) >= self.missing_field_threshold:
            flags.append(BiasFlag(
                severity="warning",
                category="missing_data",
                message=f"High rate of missing education data ({len(no_education_candidates)}/{len(resumes)} candidates)",
                affected_candidates=no_education_candidates,
                recommendation="Verify if education requirements are clearly stated. Missing education data may disadvantage qualified candidates.",
                details={
                    "missing_count": len(no_education_candidates),
                    "missing_rate": len(no_education_candidates) / len(resumes)
                }
            ))
        
        # Check for extreme homogeneity or heterogeneity
        education_counts = Counter(education_levels)
        most_common = education_counts.most_common(1)[0]
        
        # Flag if one education level dominates (>80%)
        if most_common[1] / len(education_levels) > 0.8 and len(resumes) >= 5:
            flags.append(BiasFlag(
                severity="info",
                category="pattern",
                message=f"Education distribution heavily skewed toward {most_common[0]} level ({most_common[1]}/{len(resumes)} candidates)",
                affected_candidates=[],
                recommendation="Review if job requirements may be excluding qualified candidates with different education backgrounds.",
                details={
                    "dominant_level": most_common[0],
                    "dominant_count": most_common[1],
                    "dominant_percentage": most_common[1] / len(resumes),
                    "distribution": dict(education_counts)
                }
            ))
        
        return flags
    
    def _check_skill_diversity(self, resumes: List[Dict[str, Any]]) -> List[BiasFlag]:
        """Check for lack of skill diversity"""
        flags = []
        
        all_skills = set()
        candidate_skill_counts = []
        
        for resume in resumes:
            skills = resume.get("skills", [])
            all_skills.update(skills)
            candidate_skill_counts.append(len(skills))
        
        if not all_skills:
            flags.append(BiasFlag(
                severity="critical",
                category="missing_data",
                message="No skills extracted from any candidate",
                affected_candidates=[r.get("name", "Unknown") for r in resumes],
                recommendation="Critical: Review resume parsing. Skills are essential for evaluation.",
                details={
                    "total_unique_skills": 0,
                    "candidates_affected": len(resumes)
                }
            ))
            return flags
        
        # Check for low skill diversity across candidates
        avg_skills_per_candidate = statistics.mean(candidate_skill_counts) if candidate_skill_counts else 0
        
        if avg_skills_per_candidate < 3 and len(resumes) >= 3:
            low_skill_candidates = [
                r.get("name", "Unknown") for r in resumes 
                if len(r.get("skills", [])) < 3
            ]
            
            flags.append(BiasFlag(
                severity="warning",
                category="missing_data",
                message=f"Low skill extraction rate (avg {avg_skills_per_candidate:.1f} skills per candidate)",
                affected_candidates=low_skill_candidates,
                recommendation="Review resume parsing quality. Low skill counts may indicate parsing issues or overly strict extraction.",
                details={
                    "avg_skills_per_candidate": round(avg_skills_per_candidate, 1),
                    "total_unique_skills": len(all_skills),
                    "candidates_with_few_skills": len(low_skill_candidates)
                }
            ))
        
        return flags
    
    def _check_scoring_patterns(
        self,
        resumes: List[Dict[str, Any]],
        score_breakdowns: List[Dict[str, Any]]
    ) -> List[BiasFlag]:
        """Check for suspicious scoring patterns"""
        flags = []
        
        if len(score_breakdowns) < 3:
            return flags
        
        # Extract final scores
        final_scores = [s.get("final_score", 0) for s in score_breakdowns]
        
        if not final_scores:
            return flags
        
        # Check for score clustering (all scores very similar)
        score_range = max(final_scores) - min(final_scores)
        
        if score_range < self.score_spread_threshold and len(resumes) >= 5:
            flags.append(BiasFlag(
                severity="warning",
                category="pattern",
                message=f"Scores clustered in narrow range (spread: {score_range:.1%})",
                affected_candidates=[],
                recommendation="Review scoring methodology. Narrow score distribution may indicate system is not differentiating candidates effectively.",
                details={
                    "score_range": round(score_range, 3),
                    "min_score": round(min(final_scores), 3),
                    "max_score": round(max(final_scores), 3),
                    "mean_score": round(statistics.mean(final_scores), 3)
                }
            ))
        
        # Check for perfect scores (may indicate gaming or issues)
        perfect_scores = [
            (i, r.get("name", "Unknown")) 
            for i, (r, s) in enumerate(zip(resumes, score_breakdowns))
            if s.get("final_score", 0) >= 0.99
        ]
        
        if len(perfect_scores) > len(resumes) * 0.3:  # More than 30% perfect scores
            flags.append(BiasFlag(
                severity="info",
                category="pattern",
                message=f"Unusually high rate of near-perfect scores ({len(perfect_scores)}/{len(resumes)})",
                affected_candidates=[name for _, name in perfect_scores],
                recommendation="Verify scoring is differentiating candidates. Very high scores may indicate overly lenient criteria.",
                details={
                    "perfect_score_count": len(perfect_scores),
                    "perfect_score_rate": len(perfect_scores) / len(resumes)
                }
            ))
        
        return flags
    
    def _check_parsing_quality(self, resumes: List[Dict[str, Any]]) -> List[BiasFlag]:
        """Check for signs of poor parsing quality"""
        flags = []
        
        incomplete_candidates = []
        
        for resume in resumes:
            # Count how many key fields are present
            key_fields = ["name", "email", "phone", "skills", "experience_years", "education"]
            present_fields = sum(1 for field in key_fields if resume.get(field))
            
            # Flag if less than half of key fields are present
            if present_fields < len(key_fields) / 2:
                incomplete_candidates.append(resume.get("name", "Unknown"))
        
        if incomplete_candidates:
            flags.append(BiasFlag(
                severity="warning",
                category="parsing_quality",
                message=f"{len(incomplete_candidates)} candidates have incomplete data (< 50% key fields)",
                affected_candidates=incomplete_candidates,
                recommendation="Review resume formats and parsing logic. Incomplete parsing may unfairly disadvantage candidates.",
                details={
                    "incomplete_count": len(incomplete_candidates),
                    "incomplete_rate": len(incomplete_candidates) / len(resumes)
                }
            ))
        
        return flags
    
    def _check_data_consistency(self, resumes: List[Dict[str, Any]]) -> List[BiasFlag]:
        """Check for data consistency issues"""
        flags = []
        
        # Check for duplicate candidates
        names = [r.get("name", "").lower().strip() for r in resumes if r.get("name")]
        name_counts = Counter(names)
        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        
        if duplicates:
            flags.append(BiasFlag(
                severity="warning",
                category="consistency",
                message=f"Potential duplicate candidates detected ({len(duplicates)} names appear multiple times)",
                affected_candidates=list(duplicates.keys()),
                recommendation="Review for duplicate submissions. Multiple entries for same candidate may skew statistics.",
                details={
                    "duplicates": duplicates
                }
            ))
        
        # Check for suspicious email patterns (all same domain, etc.)
        emails = [r.get("email", "").lower() for r in resumes if r.get("email")]
        
        if emails:
            domains = [email.split("@")[1] if "@" in email else "" for email in emails]
            domain_counts = Counter(domains)
            most_common_domain = domain_counts.most_common(1)[0] if domain_counts else ("", 0)
            
            # Flag if one domain is >70% (unless it's common like gmail)
            common_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}
            if (most_common_domain[0] not in common_domains and 
                most_common_domain[1] / len(emails) > 0.7 and 
                len(resumes) >= 5):
                
                flags.append(BiasFlag(
                    severity="info",
                    category="pattern",
                    message=f"Email addresses concentrated in one domain ({most_common_domain[0]}: {most_common_domain[1]}/{len(emails)})",
                    affected_candidates=[],
                    recommendation="This may be normal for internal referrals, but verify candidate pool diversity.",
                    details={
                        "dominant_domain": most_common_domain[0],
                        "domain_count": most_common_domain[1],
                        "domain_rate": most_common_domain[1] / len(emails)
                    }
                ))
        
        return flags
    
    def _generate_summary(self, total_candidates: int, flags: List[BiasFlag]) -> str:
        """Generate summary of bias report"""
        if not flags:
            return f"✅ No bias concerns detected across {total_candidates} candidates."
        
        critical_count = sum(1 for f in flags if f.severity == "critical")
        warning_count = sum(1 for f in flags if f.severity == "warning")
        info_count = sum(1 for f in flags if f.severity == "info")
        
        parts = [f"Analyzed {total_candidates} candidates."]
        
        if critical_count > 0:
            parts.append(f"🚨 {critical_count} critical issue(s) found.")
        
        if warning_count > 0:
            parts.append(f"⚠️  {warning_count} warning(s) identified.")
        
        if info_count > 0:
            parts.append(f"ℹ️  {info_count} informational notice(s).")
        
        parts.append("Review flags below for details and recommendations.")
        
        return " ".join(parts)


# Convenience function
def generate_bias_report(
    resumes: List[Dict[str, Any]],
    score_breakdowns: Optional[List[Dict[str, Any]]] = None
) -> BiasReport:
    """
    Generate a bias detection report
    
    Args:
        resumes: List of parsed resume dictionaries
        score_breakdowns: Optional list of score breakdown dictionaries
        
    Returns:
        BiasReport with detected issues
        
    Example:
        >>> resumes = [{"name": "Alice", "skills": ["Python"]}, ...]
        >>> report = generate_bias_report(resumes)
        >>> print(report.summary)
        >>> for flag in report.flags:
        ...     print(f"{flag.severity}: {flag.message}")
    """
    detector = BiasDetector()
    return detector.generate_report(resumes, score_breakdowns)
