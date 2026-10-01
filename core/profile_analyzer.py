import json
import re
from typing import Dict, List
import spacy

class ProfileAnalyzer:
    def __init__(self):
        # Load NLP model
        try:
            self.nlp = spacy.load('en_core_web_md')
        except:
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_md'])
            self.nlp = spacy.load('en_core_web_md')
        
        self.keywords = [
            'IoT', 'Internet of Things', 'Robotics', 'Embedded Systems',
            'Arduino', 'Raspberry Pi', 'Sensor', 'Automation',
            'Mechatronics', 'Control Systems', 'ROS', 'Python',
            'C++', 'Machine Learning', 'Computer Vision'
        ]
    
    def analyze_profile(self, profile_data: Dict) -> Dict:
        """Analyze LinkedIn profile and extract key information"""
        
        # Extract text from profile
        profile_text = self._extract_text(profile_data)
        
        # Analyze skills
        skills = self._extract_skills(profile_text)
        
        # Analyze experience
        experience = self._extract_experience(profile_data)
        
        # Determine field
        field = self._determine_field(profile_text, skills)
        
        # Generate profile summary
        summary = {
            'field': field,
            'skills': skills,
            'experience_years': experience['total_years'],
            'key_technologies': experience['technologies'],
            'profile_strength': self._calculate_strength(profile_data)
        }
        
        # Save profile data
        self._save_profile(summary)
        
        return summary
    
    def _extract_text(self, profile_data: Dict) -> str:
        """Extract all text from profile data"""
        text_parts = []
        
        if 'headline' in profile_data:
            text_parts.append(profile_data['headline'])
        if 'summary' in profile_data:
            text_parts.append(profile_data['summary'])
        if 'experience' in profile_data:
            for exp in profile_data['experience']:
                text_parts.append(exp.get('title', ''))
                text_parts.append(exp.get('description', ''))
        if 'skills' in profile_data:
            text_parts.extend(profile_data['skills'])
        
        return ' '.join(text_parts)
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract relevant skills from text"""
        doc = self.nlp(text.lower())
        extracted_skills = []
        
        for token in doc:
            if token.text in [kw.lower() for kw in self.keywords]:
                extracted_skills.append(token.text.title())
        
        # Add related terms
        for keyword in self.keywords:
            if keyword.lower() in text.lower() and keyword not in extracted_skills:
                extracted_skills.append(keyword)
        
        return list(set(extracted_skills))
    
    def _extract_experience(self, profile_data: Dict) -> Dict:
        """Extract experience details"""
        total_years = 0
        technologies = []
        
        if 'experience' in profile_data:
            for exp in profile_data['experience']:
                if 'duration' in exp:
                    # Parse duration (simplified)
                    duration = exp['duration']
                    if 'year' in duration:
                        years = int(re.search(r'\d+', duration).group())
                        total_years += years
                
                # Extract technologies from description
                if 'description' in exp:
                    techs = self._extract_skills(exp['description'])
                    technologies.extend(techs)
        
        return {
            'total_years': total_years,
            'technologies': list(set(technologies))
        }
    
    def _determine_field(self, text: str, skills: List[str]) -> str:
        """Determine the primary field"""
        field_scores = {
            'IoT': 0,
            'Robotics': 0,
            'Embedded Systems': 0,
            'Automation': 0
        }
        
        # Score based on keywords
        field_keywords = {
            'IoT': ['iot', 'internet of things', 'sensor', 'smart'],
            'Robotics': ['robot', 'ros', 'automation', 'control'],
            'Embedded Systems': ['embedded', 'microcontroller', 'firmware'],
            'Automation': ['automation', 'plc', 'scada']
        }
        
        for field, keywords in field_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    field_scores[field] += 2
                if keyword.title() in skills:
                    field_scores[field] += 3
        
        # Return highest scoring field
        return max(field_scores, key=field_scores.get)
    
    def _calculate_strength(self, profile_data: Dict) -> str:
        """Calculate profile strength"""
        score = 0
        max_score = 10
        
        if 'headline' in profile_data and profile_data['headline']:
            score += 1
        if 'summary' in profile_data and len(profile_data['summary']) > 100:
            score += 2
        if 'experience' in profile_data and len(profile_data['experience']) > 0:
            score += 3
        if 'skills' in profile_data and len(profile_data['skills']) > 5:
            score += 2
        if 'education' in profile_data:
            score += 1
        if 'profile_picture' in profile_data:
            score += 1
        
        percentage = (score / max_score) * 100
        
        if percentage >= 80:
            return "Strong"
        elif percentage >= 60:
            return "Good"
        elif percentage >= 40:
            return "Average"
        else:
            return "Needs Improvement"
    
    def _save_profile(self, profile_data: Dict):
        """Save profile data to file"""
        import json
        with open('data/profile_data.json', 'w') as f:
            json.dump(profile_data, f, indent=2)