"""GitHub API client for profile discovery and repository analysis."""

import time
from typing import Dict, List, Optional, Any
from github import Github, GithubException
from github.Repository import Repository
from github.NamedUser import NamedUser
import structlog

from profile_discovery.core.config import settings
from profile_discovery.core.models import GitHubProfile, GitHubRepository, DiscoveryStrategy
from profile_discovery.utils.logger import get_logger

logger = get_logger(__name__)


class GitHubClient:
    """GitHub API client with rate limiting and error handling."""
    
    def __init__(self):
        """Initialize GitHub client."""
        self.logger = logger
        
        if not settings.github_token:
            self.logger.warning("No GitHub token provided, using unauthenticated API (limited rate)")
            self.github = Github()
        else:
            self.github = Github(settings.github_token)
        
        # Rate limiting
        self.rate_limit = settings.github_rate_limit
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
    
    def _rate_limit_check(self) -> None:
        """Check and enforce rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_users_by_email(self, email: str) -> List[Dict[str, Any]]:
        """
        Search GitHub users by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            List of user search results
        """
        self._rate_limit_check()
        
        try:
            # GitHub API doesn't support direct email search, but we can try
            # searching for the email in user profiles
            query = f'"{email}" in:email'
            users = self.github.search_users(query=query, sort='followers', order='desc')
            
            results = []
            for user in users[:5]:  # Limit to top 5 results
                results.append({
                    'username': user.login,
                    'name': user.name,
                    'email': user.email,
                    'bio': user.bio,
                    'location': user.location,
                    'company': user.company,
                    'followers': user.followers,
                    'public_repos': user.public_repos,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'avatar_url': user.avatar_url,
                    'profile_url': user.html_url
                })
            
            self.logger.info("GitHub email search completed", 
                           email=email, 
                           results_count=len(results))
            return results
            
        except GithubException as e:
            self.logger.error("GitHub email search failed", 
                            email=email, 
                            error=str(e))
            return []
    
    def search_users_by_name(self, name: str, location: Optional[str] = None, company: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search GitHub users by name and context.
        
        Args:
            name: Full name to search for
            location: Optional location to include in search
            company: Optional company to include in search
            
        Returns:
            List of user search results
        """
        self._rate_limit_check()
        
        try:
            # Build search query
            query_parts = [f'"{name}" in:name']
            if location:
                query_parts.append(f'location:"{location}"')
            if company:
                query_parts.append(f'company:"{company}"')
            
            query = ' '.join(query_parts)
            users = self.github.search_users(query=query, sort='followers', order='desc')
            
            results = []
            for user in users[:10]:  # Limit to top 10 results
                results.append({
                    'username': user.login,
                    'name': user.name,
                    'email': user.email,
                    'bio': user.bio,
                    'location': user.location,
                    'company': user.company,
                    'followers': user.followers,
                    'public_repos': user.public_repos,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'avatar_url': user.avatar_url,
                    'profile_url': user.html_url
                })
            
            self.logger.info("GitHub name search completed", 
                           name=name, 
                           location=location,
                           company=company,
                           results_count=len(results))
            return results
            
        except GithubException as e:
            self.logger.error("GitHub name search failed", 
                            name=name, 
                            error=str(e))
            return []
    
    def get_user_profile(self, username: str) -> Optional[GitHubProfile]:
        """
        Get detailed GitHub user profile.
        
        Args:
            username: GitHub username
            
        Returns:
            GitHubProfile object or None if not found
        """
        self._rate_limit_check()
        
        try:
            user = self.github.get_user(username)
            
            profile = GitHubProfile(
                username=user.login,
                name=user.name,
                bio=user.bio,
                location=user.location,
                company=user.company,
                email=user.email,
                blog=user.blog,
                public_repos=user.public_repos,
                public_gists=user.public_gists,
                followers=user.followers,
                following=user.following,
                created_at=user.created_at.isoformat() if user.created_at else None,
                updated_at=user.updated_at.isoformat() if user.updated_at else None,
                avatar_url=user.avatar_url,
                profile_url=user.html_url
            )
            
            self.logger.debug("GitHub profile retrieved", username=username)
            return profile
            
        except GithubException as e:
            self.logger.error("Failed to get GitHub profile", 
                            username=username, 
                            error=str(e))
            return None
    
    def get_user_repositories(self, username: str, max_repos: int = 20) -> List[GitHubRepository]:
        """
        Get user repositories with analysis.
        
        Args:
            username: GitHub username
            max_repos: Maximum number of repositories to fetch
            
        Returns:
            List of GitHubRepository objects
        """
        self._rate_limit_check()
        
        try:
            user = self.github.get_user(username)
            repos = user.get_repos(sort='updated', direction='desc')
            
            repositories = []
            for repo in repos[:max_repos]:
                try:
                    repository = GitHubRepository(
                        name=repo.name,
                        full_name=repo.full_name,
                        description=repo.description,
                        language=repo.language,
                        stars=repo.stargazers_count,
                        forks=repo.forks_count,
                        created_at=repo.created_at.isoformat() if repo.created_at else None,
                        updated_at=repo.updated_at.isoformat() if repo.updated_at else None,
                        topics=repo.get_topics() if repo.has_issues else [],
                        is_fork=repo.fork,
                        is_archived=repo.archived
                    )
                    repositories.append(repository)
                except GithubException as e:
                    self.logger.warning("Failed to get repository details", 
                                      repo_name=repo.name, 
                                      error=str(e))
                    continue
            
            self.logger.info("GitHub repositories retrieved", 
                           username=username, 
                           repos_count=len(repositories))
            return repositories
            
        except GithubException as e:
            self.logger.error("Failed to get GitHub repositories", 
                            username=username, 
                            error=str(e))
            return []
    
    def analyze_languages_and_frameworks(self, repositories: List[GitHubRepository]) -> tuple[Dict[str, int], List[str]]:
        """
        Analyze programming languages and frameworks from repositories.
        
        Args:
            repositories: List of GitHub repositories
            
        Returns:
            Tuple of (languages_used, frameworks_detected)
        """
        languages_used = {}
        frameworks_detected = []
        
        # Framework keywords to detect
        framework_keywords = {
            'react': ['react', 'next.js', 'gatsby'],
            'angular': ['angular'],
            'vue': ['vue', 'nuxt'],
            'django': ['django'],
            'flask': ['flask'],
            'spring': ['spring'],
            'express': ['express'],
            'laravel': ['laravel'],
            'asp.net': ['asp.net', 'aspnet'],
            'fastapi': ['fastapi'],
            'node.js': ['node', 'nodejs'],
            'docker': ['docker'],
            'kubernetes': ['kubernetes', 'k8s'],
            'aws': ['aws', 'amazon'],
            'azure': ['azure'],
            'gcp': ['gcp', 'google cloud'],
            'jenkins': ['jenkins'],
            'gitlab': ['gitlab'],
            'github': ['github']
        }
        
        for repo in repositories:
            # Count languages
            if repo.language:
                languages_used[repo.language] = languages_used.get(repo.language, 0) + 1
            
            # Detect frameworks from topics and description
            search_text = ' '.join([
                repo.description or '',
                ' '.join(repo.topics),
                repo.name
            ]).lower()
            
            for framework, keywords in framework_keywords.items():
                if any(keyword in search_text for keyword in keywords):
                    if framework not in frameworks_detected:
                        frameworks_detected.append(framework)
        
        return languages_used, frameworks_detected
    
    def validate_profile_match(self, profile: GitHubProfile, candidate_data: Dict[str, Any]) -> tuple[float, str]:
        """
        Validate GitHub profile match with candidate data.
        
        Args:
            profile: GitHub profile to validate
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
                confidence += 0.3
                reasoning_parts.append("Name matches")
            elif any(word in profile_name for word in candidate_name.split()):
                confidence += 0.2
                reasoning_parts.append("Partial name match")
        
        # Email matching
        if profile.email and candidate_data.get('email', {}).get('value'):
            if profile.email.lower() == candidate_data['email']['value'].lower():
                confidence += 0.4
                reasoning_parts.append("Email matches exactly")
        
        # Location matching
        if profile.location and candidate_data.get('location', {}).get('value'):
            candidate_location = candidate_data['location']['value'].lower()
            profile_location = profile.location.lower()
            
            if candidate_location in profile_location or profile_location in candidate_location:
                confidence += 0.2
                reasoning_parts.append("Location matches")
        
        # Company matching
        if profile.company and candidate_data.get('experience', {}).get('companies'):
            companies = candidate_data['experience']['companies']
            if companies and isinstance(companies, list) and len(companies) > 0:
                candidate_companies = [c.lower() for c in companies]
                profile_company = profile.company.lower()
                
                if any(company in profile_company or profile_company in company for company in candidate_companies):
                    confidence += 0.2
                    reasoning_parts.append("Company matches")
        
        # Activity level bonus
        if profile.public_repos > 5:
            confidence += 0.1
            reasoning_parts.append("Active developer")
        
        if profile.followers > 10:
            confidence += 0.1
            reasoning_parts.append("Well-connected")
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Limited match evidence"
        
        return confidence, reasoning
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current GitHub API rate limit status."""
        try:
            rate_limit = self.github.get_rate_limit()
            return {
                'core': {
                    'limit': rate_limit.core.limit,
                    'remaining': rate_limit.core.remaining,
                    'reset_time': rate_limit.core.reset.isoformat() if rate_limit.core.reset else None
                },
                'search': {
                    'limit': rate_limit.search.limit,
                    'remaining': rate_limit.search.remaining,
                    'reset_time': rate_limit.search.reset.isoformat() if rate_limit.search.reset else None
                }
            }
        except Exception as e:
            self.logger.error("Failed to get rate limit status", error=str(e))
            return {}
