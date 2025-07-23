"""Main discovery service for orchestrating profile discovery."""

import time
import json
from typing import Dict, List, Optional, Any
import redis
import httpx
import structlog

from ..core.config import settings
from ..core.models import (
    DiscoveryRequest, DiscoveryResponse, DiscoveryMetadata,
    GitHubProfileMatch, LinkedInProfileMatch, DiscoveryStrategy,
    ExtractedResumeData, DiscoveryOptions
)
from ..clients.github_client import GitHubClient
from ..clients.search_client import SearchClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DiscoveryService:
    """Main service for orchestrating profile discovery."""
    
    def __init__(self):
        """Initialize discovery service."""
        self.logger = logger
        
        # Initialize clients
        self.github_client = GitHubClient()
        self.search_client = SearchClient()
        
        # Initialize Redis for caching
        self.redis_client = None
        self._init_redis()
        
        # Initialize HTTP client for Resume Parser communication
        self.http_client = httpx.AsyncClient(timeout=settings.request_timeout)
    
    def _init_redis(self) -> None:
        """Initialize Redis connection for caching."""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            self.logger.info("Redis connection established")
        except Exception as e:
            self.logger.warning("Redis connection failed, caching disabled", error=str(e))
            self.redis_client = None
    
    def _get_cache_key(self, candidate_data: ExtractedResumeData) -> str:
        """Generate cache key for candidate data."""
        # Use email and name for cache key
        email = candidate_data.personal_info.email.value or ""
        name = candidate_data.personal_info.name.value or ""
        return f"discovery:{email}:{name}".lower().replace(" ", "_")
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached discovery result."""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            self.logger.warning("Failed to get cached result", error=str(e))
        
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache discovery result."""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                cache_key,
                settings.redis_cache_ttl,
                json.dumps(result)
            )
        except Exception as e:
            self.logger.warning("Failed to cache result", error=str(e))
    
    async def discover_profiles(self, request: DiscoveryRequest) -> DiscoveryResponse:
        """
        Main method for discovering GitHub and LinkedIn profiles.
        
        Args:
            request: Discovery request with candidate data
            
        Returns:
            Discovery response with found profiles
        """
        start_time = time.time()
        candidate_data = request.candidate_data
        options = request.discovery_options or DiscoveryOptions()
        
        # Generate cache key
        cache_key = self._get_cache_key(candidate_data)
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info("Using cached discovery result", cache_key=cache_key)
            return DiscoveryResponse(**cached_result)
        
        # Initialize metadata
        metadata = DiscoveryMetadata(
            total_processing_time_ms=0.0,
            github_search_time_ms=0.0,
            linkedin_search_time_ms=0.0,
            strategies_used=[],
            cache_hits=0,
            api_calls_made=0,
            errors_encountered=[]
        )
        
        github_profiles = []
        linkedin_profiles = []
        
        try:
            # Extract candidate information
            candidate_info = self._extract_candidate_info(candidate_data)
            
            # Discover GitHub profiles
            if options.search_github:
                github_start = time.time()
                github_profiles = await self._discover_github_profiles(candidate_info, options, candidate_data)
                metadata.github_search_time_ms = (time.time() - github_start) * 1000
                # Add strategies based on what was actually used
                if candidate_info['github_url']:
                    metadata.strategies_used.append(DiscoveryStrategy.DIRECT_URL)
                if candidate_info['email']:
                    metadata.strategies_used.append(DiscoveryStrategy.EMAIL_BASED)
                if candidate_info['name']:
                    metadata.strategies_used.append(DiscoveryStrategy.NAME_CONTEXT)
            
            # Discover LinkedIn profiles
            if options.search_linkedin:
                linkedin_start = time.time()
                linkedin_profiles = await self._discover_linkedin_profiles(candidate_info, options, candidate_data)
                metadata.linkedin_search_time_ms = (time.time() - linkedin_start) * 1000
                # Add strategies based on what was actually used
                if candidate_info['linkedin_url']:
                    metadata.strategies_used.append(DiscoveryStrategy.DIRECT_URL)
                if candidate_info['name']:
                    metadata.strategies_used.append(DiscoveryStrategy.SEARCH_ENGINE)
            
            # Calculate total processing time
            total_time = (time.time() - start_time) * 1000
            metadata.total_processing_time_ms = total_time
            
            # Create response
            response = DiscoveryResponse(
                success=True,
                github_profiles=github_profiles,
                linkedin_profiles=linkedin_profiles,
                discovery_metadata=metadata,
                processing_time_ms=total_time
            )
            
            # Cache the result
            self._cache_result(cache_key, response.model_dump())
            
            self.logger.info("Profile discovery completed",
                           github_count=len(github_profiles),
                           linkedin_count=len(linkedin_profiles),
                           processing_time_ms=total_time)
            
            return response
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            self.logger.error("Profile discovery failed", 
                            error=str(e), 
                            traceback=error_traceback)
            metadata.errors_encountered.append(f"{str(e)}: {error_traceback}")
            
            return DiscoveryResponse(
                success=False,
                github_profiles=[],
                linkedin_profiles=[],
                discovery_metadata=metadata,
                processing_time_ms=(time.time() - start_time) * 1000,
                error_message=f"{str(e)}: {error_traceback}"
            )
    
    def _extract_candidate_info(self, candidate_data: ExtractedResumeData) -> Dict[str, Any]:
        """Extract relevant information from candidate data."""
        # Handle both structured objects and dictionaries for compatibility
        if hasattr(candidate_data.experience, 'companies'):
            # Structured object from Resume Parser
            companies = candidate_data.experience.companies
            positions = candidate_data.experience.positions
        else:
            # Dictionary format (fallback)
            companies = candidate_data.experience.get('companies', []) if isinstance(candidate_data.experience, dict) else []
            positions = candidate_data.experience.get('positions', []) if isinstance(candidate_data.experience, dict) else []
        
        if hasattr(candidate_data.skills, 'technical_skills'):
            # Structured object from Resume Parser
            skills = candidate_data.skills.technical_skills
        else:
            # Dictionary format (fallback)
            skills = candidate_data.skills.get('technical_skills', []) if isinstance(candidate_data.skills, dict) else []
        
        candidate_info = {
            'name': candidate_data.personal_info.name.value,
            'email': candidate_data.personal_info.email.value,
            'location': candidate_data.personal_info.location.value,
            'github_url': candidate_data.personal_info.github_url.value,
            'linkedin_url': candidate_data.personal_info.linkedin_url.value,
            'companies': companies,
            'positions': positions,
            'skills': skills
        }
        
        # Log extracted candidate information for debugging
        self.logger.info("Extracted candidate information",
                        name=candidate_info['name'],
                        email=candidate_info['email'],
                        github_url=candidate_info['github_url'],
                        linkedin_url=candidate_info['linkedin_url'],
                        companies_count=len(candidate_info['companies']),
                        skills_count=len(candidate_info['skills']))
        
        return candidate_info
    
    async def _discover_github_profiles(self, candidate_info: Dict[str, Any], options: Any, candidate_data: ExtractedResumeData) -> List[GitHubProfileMatch]:
        """Discover GitHub profiles using multiple strategies."""
        self.logger.info("Starting GitHub profile discovery", 
                        candidate_info=candidate_info,
                        options=options.model_dump() if hasattr(options, 'model_dump') else str(options))
        
        github_profiles = []
        seen_usernames = set()
        
        # Strategy 0: Direct URL validation (highest priority)
        if candidate_info['github_url']:
            self.logger.info("Checking provided GitHub URL", url=candidate_info['github_url'])
            username = self._extract_github_username(candidate_info['github_url'])
            self.logger.info("Extracted GitHub username", username=username)
            
            if username and username not in seen_usernames:
                self.logger.info("Fetching GitHub profile", username=username)
                profile = self.github_client.get_user_profile(username)
                
                if profile:
                    self.logger.info("GitHub profile fetched successfully", 
                                   username=username, 
                                   name=profile.name,
                                   company=profile.company,
                                   location=profile.location)
                    
                    confidence, reasoning = self.github_client.validate_profile_match(profile, candidate_data.model_dump())
                    self.logger.info("GitHub profile validation completed", 
                                   username=username,
                                   confidence=confidence,
                                   reasoning=reasoning,
                                   min_confidence=options.min_confidence_score)
                    
                    if confidence >= options.min_confidence_score:
                        # Get repositories and analysis
                        repositories = []
                        languages_used = {}
                        frameworks_detected = []
                        
                        if options.include_repository_analysis:
                            repositories = self.github_client.get_user_repositories(username)
                            languages_used, frameworks_detected = self.github_client.analyze_languages_and_frameworks(repositories)
                        
                        match = GitHubProfileMatch(
                            profile=profile,
                            confidence=confidence,
                            match_reasoning=reasoning,
                            repositories=repositories,
                            languages_used=languages_used,
                            frameworks_detected=frameworks_detected,
                            discovery_strategy=DiscoveryStrategy.DIRECT_URL
                        )
                        github_profiles.append(match)
                        seen_usernames.add(username)
                        self.logger.info("Direct GitHub URL validation successful", username=username, confidence=confidence)
                else:
                    self.logger.warning("GitHub profile not found for provided URL", username=username)
        
        # Strategy 1: Email-based search
        if candidate_info['email']:
            self.logger.info("Performing email-based GitHub search", email=candidate_info['email'])
            email_results = self.github_client.search_users_by_email(candidate_info['email'])
            for result in email_results:
                username = result['username']
                if username not in seen_usernames:
                    profile = self.github_client.get_user_profile(username)
                    if profile:
                        confidence, reasoning = self.github_client.validate_profile_match(profile, candidate_data.model_dump())
                        if confidence >= options.min_confidence_score:
                            # Get repositories and analysis
                            repositories = []
                            languages_used = {}
                            frameworks_detected = []
                            
                            if options.include_repository_analysis:
                                repositories = self.github_client.get_user_repositories(username)
                                languages_used, frameworks_detected = self.github_client.analyze_languages_and_frameworks(repositories)
                            
                            match = GitHubProfileMatch(
                                profile=profile,
                                confidence=confidence,
                                match_reasoning=reasoning,
                                repositories=repositories,
                                languages_used=languages_used,
                                frameworks_detected=frameworks_detected,
                                discovery_strategy=DiscoveryStrategy.EMAIL_BASED
                            )
                            github_profiles.append(match)
                            seen_usernames.add(username)
        
        # Strategy 2: Name and context search
        if candidate_info['name']:
            self.logger.info("Performing name-based GitHub search", name=candidate_info['name'])
            name_results = self.github_client.search_users_by_name(
                candidate_info['name'],
                location=candidate_info['location'],
                company=candidate_info['companies'][0] if candidate_info['companies'] and len(candidate_info['companies']) > 0 else None
            )
            
            for result in name_results:
                username = result['username']
                if username not in seen_usernames:
                    profile = self.github_client.get_user_profile(username)
                    if profile:
                        confidence, reasoning = self.github_client.validate_profile_match(profile, candidate_data.model_dump())
                        if confidence >= options.min_confidence_score:
                            # Get repositories and analysis
                            repositories = []
                            languages_used = {}
                            frameworks_detected = []
                            
                            if options.include_repository_analysis:
                                repositories = self.github_client.get_user_repositories(username)
                                languages_used, frameworks_detected = self.github_client.analyze_languages_and_frameworks(repositories)
                            
                            match = GitHubProfileMatch(
                                profile=profile,
                                confidence=confidence,
                                match_reasoning=reasoning,
                                repositories=repositories,
                                languages_used=languages_used,
                                frameworks_detected=frameworks_detected,
                                discovery_strategy=DiscoveryStrategy.NAME_CONTEXT
                            )
                            github_profiles.append(match)
                            seen_usernames.add(username)
        
        # Sort by confidence and limit results
        github_profiles.sort(key=lambda x: x.confidence, reverse=True)
        return github_profiles[:options.max_github_results]
    
    async def _discover_linkedin_profiles(self, candidate_info: Dict[str, Any], options: Any, candidate_data: ExtractedResumeData) -> List[LinkedInProfileMatch]:
        """Discover LinkedIn profiles using multiple strategies."""
        self.logger.info("Starting LinkedIn profile discovery", 
                        candidate_info=candidate_info,
                        options=options.model_dump() if hasattr(options, 'model_dump') else str(options))
        
        linkedin_profiles = []
        
        # Strategy 0: Direct URL validation (highest priority)
        if candidate_info['linkedin_url']:
            self.logger.info("Checking provided LinkedIn URL", url=candidate_info['linkedin_url'])
            profile_url = self._normalize_linkedin_url(candidate_info['linkedin_url'])
            if profile_url:
                # Extract profile data from provided URL
                profile = self.search_client.extract_linkedin_profile_data(profile_url)
                if profile:
                    confidence, reasoning = self.search_client.validate_linkedin_profile(profile, candidate_data.model_dump())
                    if confidence >= options.min_confidence_score:
                        match = LinkedInProfileMatch(
                            profile=profile,
                            confidence=confidence,
                            match_reasoning=reasoning,
                            discovery_strategy=DiscoveryStrategy.DIRECT_URL
                        )
                        linkedin_profiles.append(match)
                        self.logger.info("Direct LinkedIn URL validation successful", url=profile_url, confidence=confidence)
                else:
                    self.logger.warning("LinkedIn profile not found for provided URL", url=profile_url)
        
        # Strategy 1: Search-based discovery (fallback)
        if not candidate_info['name']:
            return linkedin_profiles
        
        self.logger.info("Performing search-based LinkedIn discovery", name=candidate_info['name'])
        # Search for LinkedIn profiles
        search_results = self.search_client.search_linkedin_profiles(
            name=candidate_info['name'],
            location=candidate_info['location'],
            company=candidate_info['companies'][0] if candidate_info['companies'] and len(candidate_info['companies']) > 0 else None
        )
        
        for result in search_results:
            profile_url = result['profile_url']
            
            # Extract profile data
            profile = self.search_client.extract_linkedin_profile_data(profile_url)
            if profile:
                confidence, reasoning = self.search_client.validate_linkedin_profile(profile, candidate_data.model_dump())
                if confidence >= options.min_confidence_score:
                    match = LinkedInProfileMatch(
                        profile=profile,
                        confidence=confidence,
                        match_reasoning=reasoning,
                        discovery_strategy=DiscoveryStrategy.SEARCH_ENGINE
                    )
                    linkedin_profiles.append(match)
        
        # Sort by confidence and limit results
        linkedin_profiles.sort(key=lambda x: x.confidence, reverse=True)
        return linkedin_profiles[:options.max_linkedin_results]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of external services."""
        health_status = {
            'github': 'unknown',
            'linkedin': 'unknown',
            'redis': 'unknown'
        }
        
        # Check GitHub API
        try:
            rate_limit = self.github_client.get_rate_limit_status()
            if rate_limit:
                health_status['github'] = 'healthy'
            else:
                health_status['github'] = 'unhealthy'
        except Exception as e:
            health_status['github'] = 'error'
            self.logger.error("GitHub health check failed", error=str(e))
        
        # Check LinkedIn search
        try:
            rate_limit = self.search_client.get_rate_limit_status()
            if rate_limit['remaining'] > 0:
                health_status['linkedin'] = 'healthy'
            else:
                health_status['linkedin'] = 'rate_limited'
        except Exception as e:
            health_status['linkedin'] = 'error'
            self.logger.error("LinkedIn health check failed", error=str(e))
        
        # Check Redis
        if self.redis_client:
            try:
                self.redis_client.ping()
                health_status['redis'] = 'healthy'
            except Exception as e:
                health_status['redis'] = 'error'
                self.logger.error("Redis health check failed", error=str(e))
        else:
            health_status['redis'] = 'not_configured'
        
        return health_status
    
    async def close(self) -> None:
        """Close HTTP client connections."""
        await self.http_client.aclose()
    
    def _extract_github_username(self, github_url: str) -> Optional[str]:
        """
        Extract GitHub username from various URL formats.
        
        Args:
            github_url: GitHub URL in various formats
            
        Returns:
            GitHub username or None if invalid
        """
        if not github_url:
            return None
        
        # Remove whitespace
        github_url = github_url.strip()
        
        # Handle different URL formats
        if github_url.startswith('https://github.com/'):
            # https://github.com/username
            username = github_url.replace('https://github.com/', '').split('/')[0]
        elif github_url.startswith('http://github.com/'):
            # http://github.com/username
            username = github_url.replace('http://github.com/', '').split('/')[0]
        elif github_url.startswith('github.com/'):
            # github.com/username
            username = github_url.replace('github.com/', '').split('/')[0]
        elif github_url.startswith('www.github.com/'):
            # www.github.com/username
            username = github_url.replace('www.github.com/', '').split('/')[0]
        else:
            # Assume it's just a username
            username = github_url.split('/')[0]
        
        # Clean up username (remove trailing slashes, etc.)
        username = username.rstrip('/').split('?')[0].split('#')[0]
        
        # Validate username format
        if username and len(username) > 0 and len(username) <= 39:
            return username
        
        return None
    
    def _normalize_linkedin_url(self, linkedin_url: str) -> Optional[str]:
        """
        Normalize LinkedIn URL to standard format.
        
        Args:
            linkedin_url: LinkedIn URL in various formats
            
        Returns:
            Normalized LinkedIn URL or None if invalid
        """
        if not linkedin_url:
            return None
        
        # Remove whitespace
        linkedin_url = linkedin_url.strip()
        
        # Handle different URL formats
        if linkedin_url.startswith('https://www.linkedin.com/'):
            # https://www.linkedin.com/in/username
            return linkedin_url
        elif linkedin_url.startswith('http://www.linkedin.com/'):
            # http://www.linkedin.com/in/username
            return linkedin_url.replace('http://', 'https://')
        elif linkedin_url.startswith('https://linkedin.com/'):
            # https://linkedin.com/in/username
            return linkedin_url.replace('linkedin.com/', 'www.linkedin.com/')
        elif linkedin_url.startswith('http://linkedin.com/'):
            # http://linkedin.com/in/username
            return linkedin_url.replace('http://linkedin.com/', 'https://www.linkedin.com/')
        elif linkedin_url.startswith('www.linkedin.com/'):
            # www.linkedin.com/in/username
            return f'https://{linkedin_url}'
        elif linkedin_url.startswith('linkedin.com/'):
            # linkedin.com/in/username
            return f'https://www.{linkedin_url}'
        else:
            # Assume it's a relative path or username
            if linkedin_url.startswith('/'):
                return f'https://www.linkedin.com{linkedin_url}'
            elif 'linkedin.com' not in linkedin_url:
                return f'https://www.linkedin.com/in/{linkedin_url}'
            else:
                return f'https://www.{linkedin_url}'
