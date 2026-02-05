"""Email permutation logic for profile discovery."""

from typing import List, Set
import re

class EmailPermutator:
    """Generates valid email variants for profile discovery."""
    
    @staticmethod
    def generate_variants(email: str) -> List[str]:
        """
        Generate variations of the email username part.
        Useful for finding GitHub/LinkedIn profiles where users might use slight variations.
        
        Args:
            email: Original email address
            
        Returns:
            List of email variants (just the username part mostly, or full emails if needed for search)
            For GitHub search, we usually want the *username* variants.
            But if we are searching by email, we might want email variants.
            
            Let's assume we return valid GitHub username guesses based on the email.
        """
        if not email or '@' not in email:
            return []
            
        username_part = email.split('@')[0]
        domain_part = email.split('@')[1]
        
        variants = {username_part} # Set to avoid duplicates
        
        # Split by common separators
        parts = re.split(r'[._-]', username_part)
        
        if len(parts) >= 2:
            first = parts[0]
            last = parts[-1]
            
            # first.last
            variants.add(f"{first}.{last}")
            variants.add(f"{first}{last}")
            variants.add(f"{first}-{last}")
            variants.add(f"{first}_{last}")
            
            # f.last
            variants.add(f"{first[0]}.{last}")
            variants.add(f"{first[0]}{last}")
            
            # first.l
            variants.add(f"{first}.{last[0]}")
            variants.add(f"{first}{last[0]}")
            
            # last.first
            variants.add(f"{last}.{first}")
            variants.add(f"{last}{first}")
            
        # Common dev suffixes
        variants.add(f"{username_part}dev")
        variants.add(f"{username_part}codes")
        variants.add(f"{username_part}engineer")
        
        return list(variants)
