"""Race card scraping module for extracting top-line horse data."""

from typing import Dict, List, Optional, Tuple

from playwright.sync_api import Browser, Page

from .constants import EXPECTED_HEADERS, get_config
from .models import ToplineData
from .selectors import SelectorHelper
from .utils import (
    build_racecard_url,
    extract_href_safe,
    random_delay,
    retry_with_backoff,
    setup_logging,
    wait_for_selector_safe,
)


class RaceCardScraper:
    """Scraper for race card pages."""
    
    def __init__(self, browser: Browser, logger=None):
        self.browser = browser
        self.logger = logger or setup_logging()
        self.config = get_config()
    
    def scrape_race(
        self, 
        date: str, 
        course: str, 
        raceno: int
    ) -> List[ToplineData]:
        """Scrape race card for given date, course, and race number."""
        url = build_racecard_url(date, course, raceno)
        self.logger.info(f"Scraping race card: {url}")
        
        def _scrape():
            page = self.browser.new_page()
            try:
                # Set user agent
                page.set_extra_http_headers({
                    "User-Agent": self.config["user_agent"]
                })
                
                # Navigate to race card page
                page.goto(url, timeout=self.config["page_load_timeout"])
                
                # Wait for page to load
                wait_for_selector_safe(page, "body", self.config["selector_timeout"], self.logger)
                random_delay()
                
                # Find and scrape the race table
                return self._scrape_race_table(page)
                
            finally:
                page.close()
        
        return retry_with_backoff(_scrape, logger=self.logger)
    
    def _scrape_race_table(self, page: Page) -> List[ToplineData]:
        """Scrape the main race table."""
        selector_helper = SelectorHelper(page, self.logger)
        
        # Find the race table
        table = selector_helper.find_table_by_headers(EXPECTED_HEADERS)
        if not table:
            self.logger.error("Could not find race table with expected headers")
            return []
        
        # Get header to column mapping
        column_map = selector_helper.get_header_column_map(table, EXPECTED_HEADERS)
        if not column_map:
            self.logger.error("Could not map table headers to columns")
            return []
        
        self.logger.info(f"Found {len(column_map)} mapped headers: {list(column_map.keys())}")
        
        # Extract horse data from table rows
        horses = []
        try:
            rows = table.query_selector_all("tr")[1:]  # Skip header row
            
            for row_index, row in enumerate(rows):
                try:
                    horse_data = self._extract_horse_data(row, column_map, selector_helper)
                    if horse_data:
                        horses.append(horse_data)
                        self.logger.debug(f"Extracted horse {row_index + 1}: {horse_data.馬名}")
                except Exception as e:
                    self.logger.warning(f"Error extracting horse data from row {row_index + 1}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error processing table rows: {e}")
        
        self.logger.info(f"Successfully extracted {len(horses)} horses from race table")
        return horses
    
    def _extract_horse_data(
        self, 
        row, 
        column_map: Dict[str, int], 
        selector_helper: SelectorHelper
    ) -> Optional[ToplineData]:
        """Extract horse data from a table row."""
        try:
            # Extract basic fields using column mapping
            horse_data = {}
            
            # Map actual table headers to our schema fields
            field_mapping = {
                "編號": "馬號",           # Number -> Horse number
                "馬名": "馬名",           # Horse name
                "排位體重": "排位",        # Barrier weight -> Barrier position  
                "負磅": "負磅",           # Carried weight
                "評分": "當前評分",        # Rating -> Current rating
                "馬齡": "馬齡",           # Age (new field)
                "6次近績": "最近6輪",      # Recent 6 runs
                "練馬師": "練馬師",        # Trainer
                "優先參賽次序": "練馬師喜好", # Priority -> Trainer preference
                "配備": "配備",           # Equipment
                "騎師": "騎師",           # Jockey
                "讓磅": "讓磅",           # Weight allowance
                "獨贏": "獨贏",           # Win odds
                "位置": "位置",           # Place odds
                "馬匹編號": "馬匹編號",    # Horse code
                "國際評分": "國際評分",    # International rating
            }
            
            # Extract fields from table
            for table_header, schema_field in field_mapping.items():
                if table_header in column_map:
                    value = selector_helper.get_cell_by_header(row, table_header, column_map)
                    horse_data[schema_field] = value
                else:
                    horse_data[schema_field] = ""
            
            # Set default values for required fields
            if "練馬師喜好" not in horse_data:
                horse_data["練馬師喜好"] = "1"
            
            # Find horse detail link
            detail_url = self._find_horse_detail_link(row)
            if detail_url:
                horse_data["detail_url"] = detail_url
                # Try to extract horse ID from URL
                horse_id = self._extract_horse_id_from_url(detail_url)
                if horse_id:
                    horse_data["馬匹ID"] = horse_id
            
            # Create ToplineData object
            return ToplineData(**horse_data)
            
        except Exception as e:
            self.logger.error(f"Error creating horse data object: {e}")
            return None
    
    def _find_horse_detail_link(self, row) -> Optional[str]:
        """Find horse detail link in table row."""
        try:
            # Look for links in the row
            links = row.query_selector_all("a")
            for link in links:
                href = extract_href_safe(link)
                if href and ("Horse.aspx" in href or "horse" in href):
                    # Make absolute URL if needed
                    if href.startswith("/"):
                        href = f"https://racing.hkjc.com{href}"
                    return href
            
        except Exception as e:
            self.logger.debug(f"Error finding horse detail link: {e}")
        
        return None
    
    def _extract_horse_id_from_url(self, url: str) -> Optional[str]:
        """Extract horse ID from detail URL."""
        try:
            # Common patterns for horse IDs in URLs
            import re
            
            # Pattern 1: Horse.aspx?HorseId=HK_2024_K106 -> extract K106 (last segment)
            match = re.search(r'HorseId=([A-Z0-9_]+)', url)
            if match:
                full_id = match.group(1)
                # Extract the last segment after the last underscore
                parts = full_id.split('_')
                if len(parts) > 1:
                    return parts[-1]  # Return just the last part (e.g., K106)
                return full_id
            
            # Pattern 2: Horse.aspx?HorseId=12345 (numeric ID)
            match = re.search(r'HorseId=(\d+)', url)
            if match:
                return match.group(1)
            
            # Pattern 3: /horse/12345/
            match = re.search(r'/horse/(\d+)/', url)
            if match:
                return match.group(1)
            
            # Pattern 4: horse_id=12345
            match = re.search(r'horse_id=(\d+)', url)
            if match:
                return match.group(1)
            
        except Exception as e:
            self.logger.debug(f"Error extracting horse ID from URL: {e}")
        
        return None
