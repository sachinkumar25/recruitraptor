"""Playwright-based LinkedIn profile scraper for bypassing auth walls."""

import asyncio
import time
import random
import re
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout

from ..core.config import settings
from ..core.models import LinkedInProfile, DiscoveryStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LinkedInClient:
    """Playwright-based LinkedIn profile scraper."""

    def __init__(self):
        """Initialize LinkedIn client."""
        self.logger = logger
        self._browser: Optional[Browser] = None
        self._playwright = None
        self.last_request_time = 0
        self.min_request_interval = 3.0  # Minimum 3 seconds between requests
        self.requests_made = 0
        self.max_requests_per_session = 50  # Limit requests per browser session

    async def _ensure_browser(self) -> Browser:
        """Ensure browser is initialized."""
        if self._browser is None or not self._browser.is_connected():
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            )
            self.logger.info("Playwright browser initialized")
        return self._browser

    @asynccontextmanager
    async def _get_stealth_context(self):
        """Create a stealth browser context with anti-detection measures."""
        browser = await self._ensure_browser()

        # Randomize viewport and user agent
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1440, "height": 900},
        ]

        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]

        viewport = random.choice(viewports)
        user_agent = random.choice(user_agents)

        context = await browser.new_context(
            viewport=viewport,
            user_agent=user_agent,
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'longitude': -73.935242, 'latitude': 40.730610},
            permissions=['geolocation'],
            java_script_enabled=True,
            bypass_csp=True,
        )

        # Add stealth scripts to evade detection
        await context.add_init_script("""
            // Override navigator properties
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

            // Override chrome property
            window.chrome = { runtime: {} };

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        try:
            yield context
        finally:
            await context.close()

    async def _rate_limit_check(self) -> bool:
        """Check and enforce rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            # Add some randomness to appear more human-like
            sleep_time += random.uniform(0.5, 1.5)
            await asyncio.sleep(sleep_time)

        if self.requests_made >= self.max_requests_per_session:
            self.logger.warning("Session request limit reached, rotating browser")
            await self._rotate_browser()
            self.requests_made = 0

        self.last_request_time = time.time()
        self.requests_made += 1
        return True

    async def _rotate_browser(self) -> None:
        """Close and recreate browser to avoid detection."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        # Wait before creating new browser
        await asyncio.sleep(random.uniform(2, 5))
        await self._ensure_browser()
        self.logger.info("Browser rotated")

    async def _human_like_scroll(self, page: Page) -> None:
        """Simulate human-like scrolling behavior."""
        # Random scroll pattern
        scroll_steps = random.randint(3, 6)
        for _ in range(scroll_steps):
            scroll_amount = random.randint(100, 400)
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(0.3, 0.8))

    async def search_linkedin_profiles(
        self,
        name: str,
        location: Optional[str] = None,
        company: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for LinkedIn profiles using Google search with Playwright.

        Args:
            name: Full name to search for
            location: Optional location to include in search
            company: Optional company to include in search

        Returns:
            List of LinkedIn profile search results
        """
        await self._rate_limit_check()

        try:
            async with self._get_stealth_context() as context:
                page = await context.new_page()

                # Build search query
                query_parts = [f'"{name}"']
                if location:
                    query_parts.append(location)
                if company:
                    query_parts.append(company)
                query_parts.append("site:linkedin.com/in/")

                query = " ".join(query_parts)
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

                # Navigate to Google search
                await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

                # Wait for results to load
                await asyncio.sleep(random.uniform(1.5, 3))

                # Simulate human behavior
                await self._human_like_scroll(page)

                # Extract LinkedIn profile links
                linkedin_profiles = []

                # Find all search result links
                links = await page.query_selector_all("a[href*='linkedin.com/in/']")

                for link in links[:10]:  # Limit to first 10 results
                    try:
                        href = await link.get_attribute("href")
                        if href and "linkedin.com/in/" in href:
                            # Clean up the URL
                            if href.startswith("/url?q="):
                                href = href.split("/url?q=")[1].split("&")[0]

                            # Extract the parent search result for title/snippet
                            parent = await link.evaluate_handle("el => el.closest('[data-hveid]') || el.closest('.g')")

                            title = ""
                            snippet = ""

                            if parent:
                                title_el = await parent.query_selector("h3")
                                if title_el:
                                    title = await title_el.inner_text()

                                snippet_el = await parent.query_selector("[data-sncf], .VwiC3b, span[class*='st']")
                                if snippet_el:
                                    snippet = await snippet_el.inner_text()

                            profile_data = {
                                "profile_url": href,
                                "title": title,
                                "snippet": snippet,
                                "position": len(linkedin_profiles) + 1
                            }

                            # Avoid duplicates
                            if not any(p["profile_url"] == href for p in linkedin_profiles):
                                linkedin_profiles.append(profile_data)

                    except Exception as e:
                        self.logger.debug(f"Error extracting link: {e}")
                        continue

                await page.close()

                self.logger.info(
                    "LinkedIn profile search completed",
                    name=name,
                    location=location,
                    company=company,
                    results_count=len(linkedin_profiles)
                )

                return linkedin_profiles

        except PlaywrightTimeout as e:
            self.logger.warning(f"Timeout during LinkedIn search: {e}")
            return []
        except Exception as e:
            self.logger.error(f"LinkedIn profile search failed: {e}")
            return []

    async def extract_profile_data(self, profile_url: str) -> Optional[LinkedInProfile]:
        """
        Extract comprehensive profile data from LinkedIn using Playwright.

        Args:
            profile_url: LinkedIn profile URL

        Returns:
            LinkedInProfile object or None if extraction fails
        """
        await self._rate_limit_check()

        try:
            async with self._get_stealth_context() as context:
                page = await context.new_page()

                # Navigate to LinkedIn profile
                await page.goto(profile_url, wait_until="domcontentloaded", timeout=45000)

                # Check for auth wall
                is_auth_wall = await self._check_auth_wall(page)

                if is_auth_wall:
                    # Try to extract limited data from auth wall
                    profile = await self._extract_limited_profile(page, profile_url)
                else:
                    # Extract full profile data
                    profile = await self._extract_full_profile(page, profile_url)

                await page.close()

                if profile:
                    self.logger.info("LinkedIn profile extracted", profile_url=profile_url)
                return profile

        except PlaywrightTimeout as e:
            self.logger.warning(f"Timeout extracting profile: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to extract LinkedIn profile: {e}", profile_url=profile_url)
            return None

    async def _check_auth_wall(self, page: Page) -> bool:
        """Check if the page shows an authentication wall."""
        auth_indicators = [
            "authwall",
            "join-form",
            "login-form",
            "Sign in to view",
            "Join to view",
            "Sign Up"
        ]

        content = await page.content()
        return any(indicator.lower() in content.lower() for indicator in auth_indicators)

    async def _extract_limited_profile(self, page: Page, profile_url: str) -> Optional[LinkedInProfile]:
        """Extract limited profile data from auth wall page."""
        try:
            profile = LinkedInProfile(profile_url=profile_url)

            # Simulate scrolling to load more content
            await self._human_like_scroll(page)
            await asyncio.sleep(random.uniform(1, 2))

            # Extract name from title or heading
            title = await page.title()
            if title:
                # LinkedIn titles often format as "Name - Title | LinkedIn"
                name_match = re.match(r'^([^-|]+)', title)
                if name_match:
                    profile.name = name_match.group(1).strip()

            # Try to extract from visible elements
            name_selectors = [
                "h1",
                "[data-tracking-control-name='public_profile_browsemap'] h1",
                ".top-card-layout__title",
                ".text-heading-xlarge"
            ]

            for selector in name_selectors:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        text = await el.inner_text()
                        if text and len(text) < 100:  # Sanity check
                            profile.name = text.strip()
                            break
                except Exception:
                    continue

            # Extract headline
            headline_selectors = [
                ".top-card-layout__headline",
                ".text-body-medium",
                "[data-test-id='headline']"
            ]

            for selector in headline_selectors:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        text = await el.inner_text()
                        if text and len(text) < 300:
                            profile.headline = text.strip()
                            break
                except Exception:
                    continue

            # Extract location
            location_selectors = [
                ".top-card-layout__first-subline",
                ".top-card__subline-item",
                "[class*='location']"
            ]

            for selector in location_selectors:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        text = await el.inner_text()
                        if text and len(text) < 100:
                            profile.location = text.strip()
                            break
                except Exception:
                    continue

            # Extract current position from headline if available
            if profile.headline:
                # Common patterns: "Title at Company" or "Title @ Company"
                position_match = re.match(r'^([^@|at]+?)(?:\s+(?:at|@)\s+(.+))?$', profile.headline, re.IGNORECASE)
                if position_match:
                    profile.current_position = position_match.group(1).strip()
                    if position_match.group(2):
                        profile.current_company = position_match.group(2).strip()

            return profile if profile.name else None

        except Exception as e:
            self.logger.error(f"Error extracting limited profile: {e}")
            return None

    async def _extract_full_profile(self, page: Page, profile_url: str) -> Optional[LinkedInProfile]:
        """Extract full profile data from logged-in or public profile view."""
        try:
            profile = LinkedInProfile(profile_url=profile_url)

            # Simulate human behavior
            await self._human_like_scroll(page)
            await asyncio.sleep(random.uniform(1.5, 2.5))

            # Extract name
            name_selectors = [
                "h1.text-heading-xlarge",
                ".pv-text-details__left-panel h1",
                ".top-card-layout__title",
                "h1"
            ]

            for selector in name_selectors:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        text = await el.inner_text()
                        if text and len(text) < 100:
                            profile.name = text.strip()
                            break
                except Exception:
                    continue

            # Extract headline
            headline_selectors = [
                ".text-body-medium.break-words",
                ".pv-text-details__left-panel .text-body-medium",
                ".top-card-layout__headline"
            ]

            for selector in headline_selectors:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        text = await el.inner_text()
                        if text and len(text) < 500:
                            profile.headline = text.strip()
                            break
                except Exception:
                    continue

            # Extract location
            location_selectors = [
                ".text-body-small.inline.t-black--light.break-words",
                ".pv-text-details__left-panel .text-body-small",
                ".top-card-layout__first-subline"
            ]

            for selector in location_selectors:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        text = await el.inner_text()
                        if text and len(text) < 100:
                            profile.location = text.strip()
                            break
                except Exception:
                    continue

            # Extract About/Summary section
            about_selectors = [
                "#about ~ .display-flex .inline-show-more-text",
                ".pv-about-section .pv-about__summary-text",
                "[data-test-id='about-section']"
            ]

            for selector in about_selectors:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        text = await el.inner_text()
                        if text and len(text) < 5000:
                            profile.summary = text.strip()
                            break
                except Exception:
                    continue

            # Extract Experience section
            experience_data = await self._extract_experience(page)
            if experience_data:
                if experience_data.get("current_position"):
                    profile.current_position = experience_data["current_position"]
                if experience_data.get("current_company"):
                    profile.current_company = experience_data["current_company"]
                if experience_data.get("positions"):
                    profile.experience_positions = experience_data["positions"]

            # Extract Education
            education_data = await self._extract_education(page)
            if education_data:
                profile.education = education_data

            # Extract Skills
            skills_data = await self._extract_skills(page)
            if skills_data:
                profile.skills = skills_data

            return profile if profile.name else None

        except Exception as e:
            self.logger.error(f"Error extracting full profile: {e}")
            return None

    async def _extract_experience(self, page: Page) -> Optional[Dict[str, Any]]:
        """Extract experience information from profile."""
        try:
            experience = {"positions": []}

            # Find experience section
            exp_items = await page.query_selector_all("#experience ~ .pvs-list__outer-container li.artdeco-list__item")

            if not exp_items:
                # Try alternative selectors
                exp_items = await page.query_selector_all(".experience-section li, .pv-experience-section__list-item")

            for i, item in enumerate(exp_items[:5]):  # Limit to first 5 positions
                try:
                    position = {}

                    # Extract title
                    title_el = await item.query_selector(".t-bold span, .pv-entity__summary-info h3")
                    if title_el:
                        position["title"] = (await title_el.inner_text()).strip()

                    # Extract company
                    company_el = await item.query_selector(".t-normal span, .pv-entity__secondary-title")
                    if company_el:
                        position["company"] = (await company_el.inner_text()).strip()

                    # Extract duration
                    duration_el = await item.query_selector(".t-black--light span, .pv-entity__date-range span:nth-child(2)")
                    if duration_el:
                        position["duration"] = (await duration_el.inner_text()).strip()

                    if position.get("title") or position.get("company"):
                        experience["positions"].append(position)

                        # Set current position (first position)
                        if i == 0:
                            experience["current_position"] = position.get("title", "")
                            experience["current_company"] = position.get("company", "")

                except Exception:
                    continue

            return experience if experience["positions"] else None

        except Exception as e:
            self.logger.debug(f"Error extracting experience: {e}")
            return None

    async def _extract_education(self, page: Page) -> Optional[List[Dict[str, str]]]:
        """Extract education information from profile."""
        try:
            education = []

            # Find education section
            edu_items = await page.query_selector_all("#education ~ .pvs-list__outer-container li.artdeco-list__item")

            if not edu_items:
                edu_items = await page.query_selector_all(".education-section li, .pv-education-section__list-item")

            for item in edu_items[:3]:  # Limit to first 3 education entries
                try:
                    edu_entry = {}

                    # School name
                    school_el = await item.query_selector(".t-bold span, .pv-entity__school-name")
                    if school_el:
                        edu_entry["school"] = (await school_el.inner_text()).strip()

                    # Degree
                    degree_el = await item.query_selector(".t-normal span, .pv-entity__degree-name span")
                    if degree_el:
                        edu_entry["degree"] = (await degree_el.inner_text()).strip()

                    if edu_entry.get("school"):
                        education.append(edu_entry)

                except Exception:
                    continue

            return education if education else None

        except Exception as e:
            self.logger.debug(f"Error extracting education: {e}")
            return None

    async def _extract_skills(self, page: Page) -> Optional[List[str]]:
        """Extract skills from profile."""
        try:
            skills = []

            # Find skills section
            skill_items = await page.query_selector_all("#skills ~ .pvs-list__outer-container li .t-bold span")

            if not skill_items:
                skill_items = await page.query_selector_all(".pv-skill-category-entity__name-text")

            for item in skill_items[:20]:  # Limit to first 20 skills
                try:
                    skill = (await item.inner_text()).strip()
                    if skill and len(skill) < 100 and skill not in skills:
                        skills.append(skill)
                except Exception:
                    continue

            return skills if skills else None

        except Exception as e:
            self.logger.debug(f"Error extracting skills: {e}")
            return None

    def validate_profile(
        self,
        profile: LinkedInProfile,
        candidate_data: Dict[str, Any]
    ) -> tuple[float, str]:
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
                confidence += 0.2
                reasoning_parts.append("Location matches")

        # Position matching
        if profile.current_position and candidate_data.get('experience', {}).get('positions'):
            positions = candidate_data['experience']['positions']
            if positions and isinstance(positions, list) and len(positions) > 0:
                candidate_positions = [p.lower() for p in positions if isinstance(p, str)]
                profile_position = profile.current_position.lower()

                if any(position in profile_position or profile_position in position for position in candidate_positions):
                    confidence += 0.25
                    reasoning_parts.append("Position matches")

        # Company matching
        if profile.current_company and candidate_data.get('experience', {}).get('companies'):
            companies = candidate_data['experience']['companies']
            if companies and isinstance(companies, list) and len(companies) > 0:
                candidate_companies = [c.lower() for c in companies if isinstance(c, str)]
                profile_company = profile.current_company.lower()

                if any(company in profile_company or profile_company in company for company in candidate_companies):
                    confidence += 0.25
                    reasoning_parts.append("Company matches")

        # Skills matching
        if profile.skills and candidate_data.get('skills', {}).get('technical_skills'):
            candidate_skills = [s.lower() for s in candidate_data['skills']['technical_skills'] if isinstance(s, str)]
            profile_skills = [s.lower() for s in profile.skills]

            matching_skills = len(set(candidate_skills) & set(profile_skills))
            if matching_skills > 0:
                confidence += min(0.2, matching_skills * 0.05)
                reasoning_parts.append(f"{matching_skills} skills match")

        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)

        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Limited match evidence"

        return confidence, reasoning

    async def close(self) -> None:
        """Close browser and cleanup resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        self.logger.info("LinkedIn client closed")


# Singleton instance for reuse
_linkedin_client: Optional[LinkedInClient] = None


def get_linkedin_client() -> LinkedInClient:
    """Get or create LinkedIn client singleton."""
    global _linkedin_client
    if _linkedin_client is None:
        _linkedin_client = LinkedInClient()
    return _linkedin_client
