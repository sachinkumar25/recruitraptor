"""Test enhanced GitHub URL extraction functionality."""

import pytest
from resume_parser.core.parser import ResumeParser


class TestGitHubUrlExtraction:
    """Test cases for GitHub URL extraction enhancement."""
    
    @pytest.fixture
    def parser(self):
        """Create a ResumeParser instance for testing."""
        return ResumeParser()
    
    def test_full_github_urls(self, parser):
        """Test extraction of full GitHub URLs."""
        text = "My GitHub profile: https://github.com/johndoe"
        urls = parser._extract_github_urls(text)
        
        assert len(urls) == 1
        assert urls[0]['url'] == 'https://github.com/johndoe'
        assert urls[0]['username'] == 'johndoe'
        assert urls[0]['confidence'] >= 0.9
    
    def test_github_without_protocol(self, parser):
        """Test extraction of GitHub URLs without protocol."""
        text = "Check out my work at github.com/janedoe/project"
        urls = parser._extract_github_urls(text)
        
        assert len(urls) == 1
        assert urls[0]['url'] == 'https://github.com/janedoe'
        assert urls[0]['username'] == 'janedoe'
        assert urls[0]['confidence'] >= 0.8
    
    def test_github_username_format(self, parser):
        """Test extraction of 'GitHub: username' format."""
        text = "GitHub: alice123"
        urls = parser._extract_github_urls(text)
        
        assert len(urls) == 1
        assert urls[0]['url'] == 'https://github.com/alice123'
        assert urls[0]['username'] == 'alice123'
        assert urls[0]['confidence'] >= 0.8
    
    def test_github_profile_format(self, parser):
        """Test extraction of 'GitHub profile: username' format."""
        text = "GitHub Profile: bob-dev"
        urls = parser._extract_github_urls(text)
        
        assert len(urls) == 1
        assert urls[0]['url'] == 'https://github.com/bob-dev'
        assert urls[0]['username'] == 'bob-dev'
        assert urls[0]['confidence'] >= 0.8
    
    def test_at_username_format(self, parser):
        """Test extraction of @username format."""
        text = "Find me on GitHub @charlie-coder"
        urls = parser._extract_github_urls(text)
        
        assert len(urls) == 1
        assert urls[0]['url'] == 'https://github.com/charlie-coder'
        assert urls[0]['username'] == 'charlie-coder'
        assert urls[0]['confidence'] >= 0.6
    
    def test_username_in_brackets(self, parser):
        """Test extraction of username in brackets."""
        text = "GitHub: (diana-dev)"
        urls = parser._extract_github_urls(text)
        
        assert len(urls) == 1
        assert urls[0]['url'] == 'https://github.com/diana-dev'
        assert urls[0]['username'] == 'diana-dev'
        assert urls[0]['confidence'] >= 0.5
    
    def test_multiple_github_urls(self, parser):
        """Test extraction of multiple GitHub URLs."""
        text = """
        GitHub: primary-user
        Also check out: https://github.com/secondary-user
        And @tertiary-user
        """
        urls = parser._extract_github_urls(text)
        
        assert len(urls) == 3
        usernames = [url['username'] for url in urls]
        assert 'primary-user' in usernames
        assert 'secondary-user' in usernames
        assert 'tertiary-user' in usernames
    
    def test_invalid_usernames_filtered(self, parser):
        """Test that invalid usernames are filtered out."""
        text = "GitHub: invalid--username"  # Double hyphen
        urls = parser._extract_github_urls(text)
        
        assert len(urls) == 0
    
    def test_username_validation(self, parser):
        """Test GitHub username validation."""
        # Valid usernames
        assert parser._is_valid_github_username("valid-user")
        assert parser._is_valid_github_username("user123")
        assert parser._is_valid_github_username("a")  # Single character
        assert parser._is_valid_github_username("a" * 39)  # Max length
        
        # Invalid usernames
        assert not parser._is_valid_github_username("")  # Empty
        assert not parser._is_valid_github_username("a" * 40)  # Too long
        assert not parser._is_valid_github_username("-invalid")  # Starts with hyphen
        assert not parser._is_valid_github_username("invalid-")  # Ends with hyphen
        assert not parser._is_valid_github_username("invalid--user")  # Double hyphen
        assert not parser._is_valid_github_username("invalid_user")  # Underscore not allowed
    
    def test_url_normalization(self, parser):
        """Test GitHub URL normalization."""
        # Already normalized
        assert parser._normalize_github_url("https://github.com/user") == "https://github.com/user"
        
        # Add protocol
        assert parser._normalize_github_url("github.com/user") == "https://github.com/user"
        
        # Just username
        assert parser._normalize_github_url("user") == "https://github.com/user"
        
        # With trailing slash
        assert parser._normalize_github_url("https://github.com/user/") == "https://github.com/user/"
    
    def test_confidence_scoring(self, parser):
        """Test confidence scoring for different patterns."""
        # Full URL should have highest confidence
        text = "https://github.com/high-confidence"
        urls = parser._extract_github_urls(text)
        assert urls[0]['confidence'] >= 0.9
        
        # Username with context should have lower confidence
        text = "Some random text with username123 in it"
        urls = parser._extract_github_urls(text)
        if urls:  # May or may not match depending on context
            assert urls[0]['confidence'] <= 0.5
    
    def test_context_bonus(self, parser):
        """Test that GitHub-related context increases confidence."""
        # With GitHub context
        text = "Check out my GitHub profile: test-user"
        urls_with_context = parser._extract_github_urls(text)
        
        # Without GitHub context
        text = "Username: test-user"
        urls_without_context = parser._extract_github_urls(text)
        
        if urls_with_context and urls_without_context:
            assert urls_with_context[0]['confidence'] > urls_without_context[0]['confidence']
    
    def test_duplicate_username_handling(self, parser):
        """Test that duplicate usernames are handled correctly."""
        text = "GitHub: user123 and also github.com/user123"
        urls = parser._extract_github_urls(text)
        
        # Should only extract one instance of each username
        usernames = [url['username'] for url in urls]
        assert len(usernames) == len(set(usernames))
        assert 'user123' in usernames 