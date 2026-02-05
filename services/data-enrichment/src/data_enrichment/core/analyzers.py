"""Analyzers for data enrichment (Gap Analysis, Skill Verification)."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re
from .models import GitHubRepositoryInsights

class GapAnalyzer:
    """Analyzes timeline gaps in experience."""
    
    @staticmethod
    def detect_gaps(experience_data: Dict[str, Any], threshold_days: int = 90) -> List[Dict[str, Any]]:
        """
        Detect gaps between employment periods greater than threshold_days.
        
        Args:
            experience_data: Experience dictionary containing 'dates' or structured positions
            threshold_days: Number of days to consider a gap (default 90)
            
        Returns:
            List of gap dictionaries with 'start', 'end', 'duration_days'
        """
        # Extract dates list if raw dates are provided
        dates_raw = experience_data.get('dates', [])
        
        if not dates_raw:
            return []
            
        # Parse dates into (start, end) tuples
        intervals = []
        for date_str in dates_raw:
            interval = GapAnalyzer._parse_date_range(date_str)
            if interval:
                intervals.append(interval)
                
        if not intervals:
            return []
            
        # Sort by start date
        intervals.sort(key=lambda x: x[0])
        
        gaps = []
        
        # Check for gaps between consecutive intervals
        # Iterate and merge overlaps first if needed, but for simple gap detection:
        # We compare end of current with start of next.
        
        # First, allow overlap coalescence effectively? 
        # Actually, let's track the "latest end date seen so far".
        
        if not intervals:
            return []
            
        current_max_end = intervals[0][1]
        
        for i in range(1, len(intervals)):
            next_start = intervals[i][0]
            next_end = intervals[i][1]
            
            # If next job started after current max end + threshold
            if next_start > current_max_end:
                gap_days = (next_start - current_max_end).days
                if gap_days > threshold_days:
                    gaps.append({
                        'start': current_max_end.strftime('%Y-%m-%d'),
                        'end': next_start.strftime('%Y-%m-%d'),
                        'duration_days': gap_days,
                        'reason': f"Gap of {gap_days} days detected between positions"
                    })
            
            # Update max end date
            if next_end > current_max_end:
                current_max_end = next_end
                
        return gaps

    @staticmethod
    def _parse_date_range(date_str: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse a date range string (e.g. 'Jan 2020 - Present') into (start, end)."""
        # Determine "Present" or "Current"
        is_present = bool(re.search(r'\b(Present|Current|Now)\b', date_str, re.IGNORECASE))
        
        # Extract years (YYYY)
        years = re.findall(r'\b(19|20)\d{2}\b', date_str)
        
        if not years and not is_present:
            return None
            
        try:
            # Default start/end
            start_date = datetime.now()
            end_date = datetime.now()
            
            if years:
                start_year = int(years[0])
                start_date = datetime(start_year, 1, 1) # Default to Jan 1st
                
                if len(years) > 1:
                    end_year = int(years[1])
                    end_date = datetime(end_year, 12, 31) # Default to Dec 31st
                elif is_present:
                    end_date = datetime.now()
                else:
                    # Only one year found and not present -> assume it's a single year duration?
                    # Or maybe start=end?
                    end_date = datetime(start_year, 12, 31)
            else:
                 # Only "Present"? Unlikely to have range without start.
                 return None

            return (start_date, end_date)
            
        except Exception:
            return None


class SkillVerifier:
    """Verifies skills against evidence sources (GitHub, etc.)."""
    
    @staticmethod
    def verify_skill_with_github(skill_name: str, github_insights: GitHubRepositoryInsights) -> Dict[str, Any]:
        """
        Verify if a skill is supported by GitHub repository analysis.
        
        Args:
            skill_name: Name of the skill (e.g. 'Python')
            github_insights: Insights from GitHub analysis
            
        Returns:
            Verification result dictionary
        """
        skill_lower = skill_name.lower()
        
        verification = {
            'verified': False,
            'confidence': 0.0,
            'evidence': []
        }
        
        # Check languages distribution
        for lang, bytes_count in github_insights.languages_distribution.items():
            if lang.lower() == skill_lower:
                verification['verified'] = True
                verification['confidence'] = 0.9
                verification['evidence'].append(f"Used in repositories ({bytes_count} bytes)")
                return verification
                
        # Check detected frameworks/topics
        for framework in github_insights.frameworks_detected:
            if framework.lower() == skill_lower:
                verification['verified'] = True
                verification['confidence'] = 0.8
                verification['evidence'].append("Detected as framework/dependency")
                return verification
        
        # Partial match fallback (e.g. 'React.js' matching 'JavaScript' repo?)
        # For now, strict matching is safer to avoid false positives.
        
        return verification
