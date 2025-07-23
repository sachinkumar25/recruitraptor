"""SerpAPI client for LinkedIn profile search."""

import time
from typing import Dict, List, Optional, Any
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
import structlog

from ..core.config import settings
from ..core.models import LinkedInProfile, DiscoveryStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SearchClient:
    """SerpAPI client for LinkedIn profile discovery."""
    
    def __init__(self):
        """Initialize search client."""
        self.logger = logger
        
        if not settings.serpapi_key:
            self.logger.warning("No SerpAPI key provided, LinkedIn search will be limited")
        
        self.api_key = settings.serpapi_key
        self.rate_limit = settings.serpapi_rate_limit
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Minimum 2 seconds between requests
        self.requests_made = 0
    
    def _rate_limit_check(self) -> bool:
        """Check and enforce rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        if self.requests_made >= self.rate_limit:
            self.logger.warning("SerpAPI rate limit reached", 
                              requests_made=self.requests_made,
                              rate_limit=self.rate_limit)
            return False
        
        self.last_request_time = time.time()
        self.requests_made += 1
        return True
    
    def search_linkedin_profiles(self, name: str, location: Optional[str] = None, company: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for LinkedIn profiles using SerpAPI.
        
        Args:
            name: Full name to search for
            location: Optional location to include in search
            company: Optional company to include in search
            
        Returns:
            List of LinkedIn profile search results
        """
        if not self._rate_limit_check():
            return []
        
        if not self.api_key:
            self.logger.error("No SerpAPI key available for LinkedIn search")
            return []
        
        try:
            # Build search query
            query_parts = [f'"{name}"']
            if location:
                query_parts.append(location)
            if company:
                query_parts.append(company)
            query_parts.append("site:linkedin.com/in/")
            
            query = " ".join(query_parts)
            
            # Configure search parameters
            search_params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": 10,  # Number of results
                "gl": "us",  # Country
                "hl": "en"   # Language
            }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            linkedin_profiles = []
            
            if "organic_results" in results:
                for result in results["organic_results"]:
                    if "link" in result and "linkedin.com/in/" in result["link"]:
                        profile_data = {
                            "profile_url": result["link"],
                            "title": result.get("title", ""),
                            "snippet": result.get("snippet", ""),
                            "position": 1  # Will be updated with actual position
                        }
                        linkedin_profiles.append(profile_data)
            
            self.logger.info("LinkedIn profile search completed", 
                           name=name, 
                           location=location,
                           company=company,
                           results_count=len(linkedin_profiles))
            return linkedin_profiles
            
        except Exception as e:
            self.logger.error("LinkedIn profile search failed", 
                            name=name, 
                            error=str(e))
            return []
    
    def extract_linkedin_profile_data(self, profile_url: str) -> Optional[LinkedInProfile]:
        """
        Extract basic profile data from LinkedIn profile URL.
        
        Args:
            profile_url: LinkedIn profile URL
            
        Returns:
            LinkedInProfile object or None if extraction fails
        """
        if not self._rate_limit_check():
            return None
        
        try:
            # Use respectful scraping with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AI-Recruiter-Agent/1.0; +https://github.com/ai-recruiter-agent)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(profile_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic profile information
            profile = LinkedInProfile(profile_url=profile_url)
            
            # Extract name (this is limited due to LinkedIn's structure)
            name_elem = soup.find('h1') or soup.find('title')
            if name_elem:
                profile.name = name_elem.get_text().strip()
            
            # Extract headline
            headline_elem = soup.find('div', {'class': 'text-body-medium'}) or soup.find('p', {'class': 'text-body-medium'})
            if headline_elem:
                profile.headline = headline_elem.get_text().strip()
            
            # Extract location (simplified approach)
            location_spans = soup.find_all('span')
            for span in location_spans:
                text = span.get_text().strip().lower()
                if 'location' in text or 'area' in text:
                    profile.location = span.get_text().strip()
                    break
            
            # Extract current position and company
            position_elem = soup.find('h2') or soup.find('div', {'class': 'text-body-medium-bold'})
            if position_elem:
                profile.current_position = position_elem.get_text().strip()
            
            self.logger.debug("LinkedIn profile data extracted", profile_url=profile_url)
            return profile
            
        except Exception as e:
            self.logger.error("Failed to extract LinkedIn profile data", 
                            profile_url=profile_url, 
                            error=str(e))
            return None
    
    def validate_linkedin_profile(self, profile: LinkedInProfile, candidate_data: Dict[str, Any]) -> tuple[float, str]:
        """
        Validate LinkedIn profile match with candidate data.
        
        Args:
            profile: LinkedIn profile to validate
            candidate_data: Resume data for comparison
            
        Returns:
            Tuple of (confidence_score, reasoning)
        """
        confidence = 0.0
        reasoning_parts = []
        
        # Name matching
        if profile.name and candidate_data.get('name', {}).get('value'):
            candidate_name = candidate_data['name']['value'].lower()
            profile_name = profile.name.lower()
            
            if candidate_name in profile_name or profile_name in candidate_name:
                confidence += 0.4
                reasoning_parts.append("Name matches")
            elif any(word in profile_name for word in candidate_name.split()):
                confidence += 0.2
                reasoning_parts.append("Partial name match")
        
        # Location matching
        if profile.location and candidate_data.get('location', {}).get('value'):
            candidate_location = candidate_data['location']['value'].lower()
            profile_location = profile.location.lower()
            
            if candidate_location in profile_location or profile_location in candidate_location:
                confidence += 0.3
                reasoning_parts.append("Location matches")
        
        # Current position matching
        if profile.current_position and candidate_data.get('experience', {}).get('positions'):
            positions = candidate_data['experience']['positions']
            if positions and isinstance(positions, list) and len(positions) > 0:
                candidate_positions = [p.lower() for p in positions]
                profile_position = profile.current_position.lower()
                
                if any(position in profile_position or profile_position in position for position in candidate_positions):
                    confidence += 0.3
                    reasoning_parts.append("Position matches")
        
        # Headline relevance
        if profile.headline and candidate_data.get('skills', {}).get('technical_skills'):
            skills = candidate_data['skills']['technical_skills']
            if skills and isinstance(skills, list) and len(skills) > 0:
                candidate_skills = [s.lower() for s in skills]
                profile_headline = profile.headline.lower()
                
                skill_matches = sum(1 for skill in candidate_skills if skill in profile_headline)
                if skill_matches > 0:
                    confidence += min(0.2, skill_matches * 0.1)
                    reasoning_parts.append(f"{skill_matches} skill matches in headline")
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Limited match evidence"
        
        return confidence, reasoning
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current SerpAPI rate limit status."""
        return {
            'requests_made': self.requests_made,
            'rate_limit': self.rate_limit,
            'remaining': max(0, self.rate_limit - self.requests_made)
        }
    
    def reset_rate_limit_counter(self) -> None:
        """Reset the rate limit counter (call this daily)."""
        self.requests_made = 0
        self.logger.info("SerpAPI rate limit counter reset")
