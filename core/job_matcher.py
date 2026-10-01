import json
from typing import Dict, List, Tuple
import difflib

class JobMatcher:
    def __init__(self):
        self.profile_data = self._load_profile()
    
    def _load_profile(self) -> Dict:
        """Load profile data from file"""
        try:
            with open('data/profile_data.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def match_jobs(self, jobs: List[Dict]) -> List[Tuple[Dict, float]]:
        """Match jobs with profile and return sorted by relevance"""
        if not self.profile_data:
            return [(job, 50.0) for job in jobs]  # Default score if no profile
        
        matched_jobs = []
        
        for job in jobs:
            score = self._calculate_match_score(job)
            if score > 30:  # Threshold for relevance
                matched_jobs.append((job, score))
        
        # Sort by score descending
        matched_jobs.sort(key=lambda x: x[1], reverse=True)
        return matched_jobs
    
    def _calculate_match_score(self, job: Dict) -> float:
        """Calculate match score between job and profile"""
        score = 0
        
        # 1. Title match (40%)
        title_score = self._match_title(job.get('title', ''))
        score += title_score * 0.4
        
        # 2. Skills match (40%)
        skills_score = self._match_skills(job.get('keywords', []))
        score += skills_score * 0.4
        
        # 3. Experience match (20%)
        exp_score = self._match_experience(job)
        score += exp_score * 0.2
        
        return score * 100  # Convert to percentage
    
    def _match_title(self, job_title: str) -> float:
        """Match job title with profile field"""
        if not self.profile_data:
            return 0.5
        
        profile_field = self.profile_data.get('field', '').lower()
        job_title_lower = job_title.lower()
        
        # Check if field appears in job title
        if profile_field in job_title_lower:
            return 1.0
        
        # Check for related terms
        related_terms = {
            'iot': ['internet of things', 'sensor', 'smart'],
            'robotics': ['robot', 'ros', 'automation'],
            'embedded systems': ['embedded', 'firmware', 'microcontroller'],
            'automation': ['plc', 'scada', 'control']
        }
        
        for term in related_terms.get(profile_field, []):
            if term in job_title_lower:
                return 0.8
        
        # Use fuzzy matching
        similarity = difflib.SequenceMatcher(
            None, profile_field, job_title_lower
        ).ratio()
        
        return similarity
    
    def _match_skills(self, job_keywords: List[str]) -> float:
        """Match job keywords with profile skills"""
        if not self.profile_data or not job_keywords:
            return 0.5
        
        profile_skills = self.profile_data.get('skills', [])
        
        if not profile_skills:
            return 0.5
        
        # Count matching skills
        matches = 0
        for skill in profile_skills:
            for keyword in job_keywords:
                if skill.lower() in keyword.lower() or keyword.lower() in skill.lower():
                    matches += 1
                    break
        
        # Calculate match ratio
        total_skills = len(profile_skills)
        match_ratio = matches / total_skills if total_skills > 0 else 0
        
        return min(match_ratio * 2, 1.0)  # Cap at 1.0
    
    def _match_experience(self, job: Dict) -> float:
        """Match experience level"""
        if not self.profile_data:
            return 0.5
        
        profile_years = self.profile_data.get('experience_years', 0)
        
        # Check for experience level in job title
        job_title = job.get('title', '').lower()
        
        if 'senior' in job_title:
            return 1.0 if profile_years >= 5 else 0.3
        elif 'junior' in job_title:
            return 1.0 if profile_years <= 3 else 0.5
        else:
            return 0.7  # Mid-level