"""Horse detail page scraping module for injuries, past runs, and profile data."""

from typing import Dict, List, Optional

from playwright.sync_api import Browser, Page

from .constants import DETAIL_TABS, get_config
from .models import InjuryRecord, PastRunRecord
from .selectors import SelectorHelper
from .utils import (
    extract_href_safe,
    extract_text_safe,
    normalize_text,
    random_delay,
    retry_with_backoff,
    setup_logging,
    wait_for_selector_safe,
)


class HorseDetailScraper:
    """Scraper for individual horse detail pages."""
    
    def __init__(self, browser: Browser, logger=None):
        self.browser = browser
        self.logger = logger or setup_logging()
        self.config = get_config()
    
    def scrape_horse_details(self, detail_url: str) -> Dict[str, any]:
        """Scrape all details for a horse from its detail page."""
        if not detail_url:
            return {}
        
        self.logger.info(f"Scraping horse details: {detail_url}")
        
        def _scrape():
            page = self.browser.new_page()
            try:
                # Set user agent
                page.set_extra_http_headers({
                    "User-Agent": self.config["user_agent"]
                })
                
                # Navigate to horse detail page
                page.goto(detail_url, timeout=self.config["page_load_timeout"])
                
                # Wait for page to load
                wait_for_selector_safe(page, "body", self.config["selector_timeout"], self.logger)
                random_delay()
                
                # Extract all detail data
                details = {}
                
                # Extract horse ID and international rating from page
                details.update(self._extract_basic_info(page))
                
                # Scrape past performance records from the main page
                details["往績紀錄"] = self._scrape_past_runs_from_main_page(page)
                
                # Scrape horse profile from the main page
                details["馬匹基本資料"] = self._scrape_profile_from_main_page(page)
                
                # Scrape injuries/health records from separate page
                details["傷病記錄"] = self._scrape_injuries_from_separate_page(page)
                
                return details
                
            finally:
                page.close()
        
        return retry_with_backoff(_scrape, logger=self.logger)
    
    def _extract_basic_info(self, page: Page) -> Dict[str, str]:
        """Extract basic horse information from the page."""
        info = {}
        
        try:
            # Try to extract horse ID from URL or page content
            current_url = page.url
            horse_id = self._extract_horse_id_from_url(current_url)
            if horse_id:
                info["馬匹ID"] = horse_id
            
            # Try to find international rating on the page
            international_rating = self._find_international_rating(page)
            if international_rating:
                info["國際評分"] = international_rating
            
        except Exception as e:
            self.logger.debug(f"Error extracting basic info: {e}")
        
        return info
    
    def _extract_horse_id_from_url(self, url: str) -> Optional[str]:
        """Extract horse ID from URL."""
        try:
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
    
    def _find_international_rating(self, page: Page) -> Optional[str]:
        """Find international rating on the page."""
        try:
            # Common selectors for international rating
            selectors = [
                "text=國際評分",
                "text=International Rating",
                ".international-rating",
                ".rating-international",
            ]
            
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        # Get the rating value (usually in next sibling or parent)
                        rating_text = element.inner_text()
                        # Extract number from text
                        import re
                        match = re.search(r'(\d+)', rating_text)
                        if match:
                            return match.group(1)
                except Exception:
                    continue
            
        except Exception as e:
            self.logger.debug(f"Error finding international rating: {e}")
        
        return None
    
    def _scrape_past_runs_from_main_page(self, page: Page) -> List[PastRunRecord]:
        """Scrape past performance records from the main horse page."""
        past_runs = []
        
        try:
            # First try to find structured race data in tables
            tables = page.query_selector_all("table")
            
            for table in tables:
                try:
                    # Check if this table contains race data
                    rows = table.query_selector_all("tr")
                    if len(rows) < 2:  # Need at least header + data rows
                        continue
                    
                    # Get header row to identify columns
                    header_row = rows[0]
                    header_cells = header_row.query_selector_all("td, th")
                    headers = []
                    
                    for cell in header_cells:
                        header_text = normalize_text(extract_text_safe(cell))
                        headers.append(header_text)
                    
                    # Check if this looks like a comprehensive race results table
                    comprehensive_indicators = ["場次", "名次", "日期", "馬場", "跑道", "賽道", "途程", "場地狀況", 
                                              "賽事班次", "檔位", "評分", "練馬師", "騎師", "頭馬距離", "獨贏賠率", 
                                              "實際負磅", "沿途走位", "完成時間", "排位體重", "配備"]
                    found_comprehensive = sum(1 for indicator in comprehensive_indicators 
                                            if any(indicator in header for header in headers))
                    
                    # Also check for basic indicators
                    basic_indicators = ["日期", "場地", "途程", "檔位", "負磅", "騎師", "名次", "時間", "配備", "評分", "獨贏"]
                    found_basic = sum(1 for indicator in basic_indicators 
                                    if any(indicator in header for header in headers))
                    
                    if found_comprehensive >= 8:  # Comprehensive table
                        self.logger.debug(f"Found comprehensive race table with {found_comprehensive} race indicators")
                        
                        # Create header mapping
                        header_mapping = {}
                        for i, header in enumerate(headers):
                            header_mapping[header] = i
                        
                        # Extract race data (limit to last 6 races)
                        data_rows = rows[1:7]  # Skip header, take up to 6 races
                        
                        for row in data_rows:
                            try:
                                cells = row.query_selector_all("td, th")
                                if len(cells) < 10:  # Need substantial data for comprehensive table
                                    continue
                                
                                # Extract comprehensive race information using header mapping
                                past_run = PastRunRecord(
                                    race_date=self._get_cell_value(cells, header_mapping, ["日期", "Date"]),
                                    venue=self._get_cell_value(cells, header_mapping, ["馬場", "跑道", "賽道", "場地", "Venue"]),
                                    distance=self._get_cell_value(cells, header_mapping, ["途程", "Distance"]),
                                    barrier=self._get_cell_value(cells, header_mapping, ["檔位", "Barrier"]),
                                    weight=self._get_cell_value(cells, header_mapping, ["實際負磅", "負磅", "Weight"]),
                                    jockey=self._get_cell_value(cells, header_mapping, ["騎師", "Jockey"]),
                                    position=self._get_cell_value(cells, header_mapping, ["名次", "Position"]),
                                    time=self._get_cell_value(cells, header_mapping, ["完成時間", "時間", "Time"]),
                                    equipment=self._get_cell_value(cells, header_mapping, ["配備", "Equipment"]),
                                    rating=self._get_cell_value(cells, header_mapping, ["評分", "Rating"]),
                                    odds=self._get_cell_value(cells, header_mapping, ["獨贏賠率", "獨贏", "Odds"])
                                )
                                
                                # Add additional comprehensive fields if available
                                if hasattr(past_run, '__dict__'):
                                    past_run.track_condition = self._get_cell_value(cells, header_mapping, ["場地狀況", "Track Condition"])
                                    past_run.race_class = self._get_cell_value(cells, header_mapping, ["賽事班次", "Class"])
                                    past_run.distance_to_winner = self._get_cell_value(cells, header_mapping, ["頭馬距離", "Distance to Winner"])
                                    past_run.running_position = self._get_cell_value(cells, header_mapping, ["沿途走位", "Running Position"])
                                    past_run.barrier_weight = self._get_cell_value(cells, header_mapping, ["排位體重", "Barrier Weight"])
                                    past_run.trainer = self._get_cell_value(cells, header_mapping, ["練馬師", "Trainer"])
                                
                                # Only add if we have meaningful data
                                if any([past_run.race_date, past_run.position, past_run.jockey]):
                                    past_runs.append(past_run)
                                    
                            except Exception as e:
                                self.logger.debug(f"Error parsing comprehensive race row: {e}")
                                continue
                                
                    elif found_basic >= 3:  # Basic table
                        self.logger.debug(f"Found basic race table with {found_basic} race indicators")
                        
                        # Create header mapping
                        header_mapping = {}
                        for i, header in enumerate(headers):
                            header_mapping[header] = i
                        
                        # Extract race data (limit to last 6 races)
                        data_rows = rows[1:7]  # Skip header, take up to 6 races
                        
                        for row in data_rows:
                            try:
                                cells = row.query_selector_all("td, th")
                                if len(cells) < len(headers):
                                    continue
                                
                                # Extract basic race information using header mapping
                                past_run = PastRunRecord(
                                    race_date=self._get_cell_value(cells, header_mapping, ["日期", "Date"]),
                                    venue=self._get_cell_value(cells, header_mapping, ["場地", "Venue"]),
                                    distance=self._get_cell_value(cells, header_mapping, ["途程", "Distance"]),
                                    barrier=self._get_cell_value(cells, header_mapping, ["檔位", "Barrier"]),
                                    weight=self._get_cell_value(cells, header_mapping, ["負磅", "Weight"]),
                                    jockey=self._get_cell_value(cells, header_mapping, ["騎師", "Jockey"]),
                                    position=self._get_cell_value(cells, header_mapping, ["名次", "Position"]),
                                    time=self._get_cell_value(cells, header_mapping, ["時間", "Time"]),
                                    equipment=self._get_cell_value(cells, header_mapping, ["配備", "Equipment"]),
                                    rating=self._get_cell_value(cells, header_mapping, ["評分", "Rating"]),
                                    odds=self._get_cell_value(cells, header_mapping, ["獨贏", "Odds"])
                                )
                                
                                # Only add if we have meaningful data
                                if any([past_run.race_date, past_run.venue, past_run.position]):
                                    past_runs.append(past_run)
                                    
                            except Exception as e:
                                self.logger.debug(f"Error parsing basic race row: {e}")
                                continue
                        
                        if past_runs:  # If we found structured data, return it
                            break
                        
                except Exception as e:
                    self.logger.debug(f"Error checking table: {e}")
                    continue
            
            # If no structured data found, try to parse from profile text
            if not past_runs:
                past_runs = self._parse_past_runs_from_profile_text(page)
            
            self.logger.debug(f"Extracted {len(past_runs)} past run records from main page")
            return past_runs
            
        except Exception as e:
            self.logger.error(f"Error scraping past runs from main page: {e}")
            return []
    
    def _parse_past_runs_from_profile_text(self, page: Page) -> List[PastRunRecord]:
        """Parse past runs from profile text that contains race results."""
        past_runs = []
        
        try:
            # Get all text content from the page
            page_text = page.inner_text()
            
            # Look for patterns like "場次: 名次 | 843: 06 | 779: 08 | 730: 10"
            import re
            
            # Pattern to match race results: race_number: position
            race_pattern = r'(\d+):\s*(\d+)'
            matches = re.findall(race_pattern, page_text)
            
            if matches:
                self.logger.debug(f"Found {len(matches)} race result patterns in profile text")
                
                # Take the last 6 races (most recent)
                recent_matches = matches[-6:]
                
                for race_num, position in recent_matches:
                    try:
                        # Create a basic past run record with available data
                        past_run = PastRunRecord(
                            race_date="",  # Not available in this format
                            venue="",      # Not available in this format
                            distance="",   # Not available in this format
                            barrier="",    # Not available in this format
                            weight="",     # Not available in this format
                            jockey="",     # Not available in this format
                            position=position,
                            time="",       # Not available in this format
                            equipment="",  # Not available in this format
                            rating="",     # Not available in this format
                            odds="",       # Not available in this format
                        )
                        
                        past_runs.append(past_run)
                        
                    except Exception as e:
                        self.logger.debug(f"Error parsing race result: {e}")
                        continue
            
        except Exception as e:
            self.logger.debug(f"Error parsing past runs from profile text: {e}")
        
        return past_runs
    
    def _scrape_profile_from_main_page(self, page: Page) -> str:
        """Scrape horse profile/basic information from the main page."""
        profile_parts = []
        
        try:
            # Look for horse information in various formats on the page
            # Try to find text blocks that contain horse details
            
            # Look for common horse information patterns
            info_selectors = [
                "text=年齡",
                "text=性別", 
                "text=毛色",
                "text=出生地",
                "text=父系",
                "text=母系",
                "text=馬主",
                "text=Age",
                "text=Sex",
                "text=Color",
                "text=Country",
                "text=Sire",
                "text=Dam",
                "text=Owner"
            ]
            
            for selector in info_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for element in elements:
                        # Get the text content and try to find the value
                        text = normalize_text(extract_text_safe(element))
                        if text:
                            # Look for the value in the same row or nearby
                            parent = element.query_selector("xpath=..")
                            if parent:
                                parent_text = normalize_text(extract_text_safe(parent))
                                if parent_text and len(parent_text) > len(text):
                                    profile_parts.append(parent_text)
                except Exception:
                    continue
            
            # Also try to extract from any table that might contain horse info
            tables = page.query_selector_all("table")
            for table in tables:
                try:
                    rows = table.query_selector_all("tr")
                    for row in rows:
                        cells = row.query_selector_all("td, th")
                        if len(cells) >= 2:
                            # Check if this looks like horse info (key: value format)
                            key_text = normalize_text(extract_text_safe(cells[0]))
                            value_text = normalize_text(extract_text_safe(cells[1]))
                            
                            if key_text and value_text and len(key_text) < 10:  # Short key
                                profile_parts.append(f"{key_text}: {value_text}")
                except Exception:
                    continue
            
            # Combine all profile information
            if profile_parts:
                profile_text = " | ".join(profile_parts)
                self.logger.debug(f"Extracted profile text: {len(profile_text)} characters")
                return profile_text
            
        except Exception as e:
            self.logger.error(f"Error scraping profile from main page: {e}")
        
        return ""
    
    def _scrape_injuries_from_separate_page(self, page: Page) -> List[InjuryRecord]:
        """Scrape injury records from the veterinary database page."""
        injuries = []
        
        try:
            # Extract horse name from current page
            horse_name = self._extract_horse_name_from_page(page)
            
            if not horse_name:
                self.logger.debug("Could not extract horse name for injury search")
                return []
            
            # Navigate to the veterinary database page
            injury_url = "https://racing.hkjc.com/racing/information/Chinese/VeterinaryRecords/OveDatabase.aspx"
            
            self.logger.debug(f"Navigating to veterinary database: {injury_url}")
            
            page.goto(injury_url, timeout=self.config["page_load_timeout"])
            wait_for_selector_safe(page, "body", self.config["selector_timeout"], self.logger)
            random_delay()
            
            # Look for the main injury records table
            # The table contains columns: 烙印編號, 馬名, 日期, 詳情, 通過日期
            table = page.query_selector("table")
            
            if table:
                # Get all rows from the table
                rows = table.query_selector_all("tr")
                self.logger.debug(f"Found table with {len(rows)} rows")
                
                # Find rows that contain our horse name
                for i, row in enumerate(rows):
                    cells = row.query_selector_all("td, th")
                    if len(cells) >= 5:  # Should have 5 columns
                        # Check if this row contains our horse name
                        row_text = " ".join([normalize_text(extract_text_safe(cell)) for cell in cells])
                        
                        if horse_name in row_text:
                            # Extract the injury record from this row
                            try:
                                # Column structure: 烙印編號, 馬名, 日期, 詳情, 通過日期
                                horse_id_cell = normalize_text(extract_text_safe(cells[0])) if len(cells) > 0 else ""
                                horse_name_cell = normalize_text(extract_text_safe(cells[1])) if len(cells) > 1 else ""
                                date_cell = normalize_text(extract_text_safe(cells[2])) if len(cells) > 2 else ""
                                description_cell = normalize_text(extract_text_safe(cells[3])) if len(cells) > 3 else ""
                                pass_date_cell = normalize_text(extract_text_safe(cells[4])) if len(cells) > 4 else ""
                                
                                # Validate that this is actually our horse
                                if horse_name_cell == horse_name and date_cell and description_cell:
                                    injuries.append(InjuryRecord(
                                        date=date_cell,
                                        description=description_cell,
                                        pass_date=pass_date_cell if pass_date_cell != "-" else ""
                                    ))
                                    self.logger.debug(f"Found injury record: {date_cell} - {description_cell}")
                                    
                                    # Check if there are continuation rows (same horse, no horse name in first cell)
                                    # Look at subsequent rows to see if they continue this horse's records
                                    j = i + 1
                                    while j < len(rows):
                                        next_row = rows[j]
                                        next_cells = next_row.query_selector_all("td, th")
                                        
                                        if len(next_cells) >= 5:
                                            # If first cell is empty or contains a date, it's a continuation
                                            first_cell = normalize_text(extract_text_safe(next_cells[0]))
                                            second_cell = normalize_text(extract_text_safe(next_cells[1]))
                                            
                                            # If second cell is empty and first cell looks like a date, it's a continuation
                                            if not second_cell and first_cell and ("/" in first_cell or first_cell.isdigit()):
                                                # This is a continuation row for the same horse
                                                cont_date = first_cell
                                                cont_description = normalize_text(extract_text_safe(next_cells[2])) if len(next_cells) > 2 else ""
                                                cont_pass_date = normalize_text(extract_text_safe(next_cells[3])) if len(next_cells) > 3 else ""
                                                
                                                if cont_date and cont_description:
                                                    injuries.append(InjuryRecord(
                                                        date=cont_date,
                                                        description=cont_description,
                                                        pass_date=cont_pass_date if cont_pass_date != "-" else ""
                                                    ))
                                                    self.logger.debug(f"Found continuation injury record: {cont_date} - {cont_description}")
                                                j += 1
                                                continue
                                            else:
                                                # Next row is for a different horse, stop
                                                break
                                        else:
                                            break
                                    
                                    break  # Found our horse, no need to continue searching
                                    
                            except Exception as e:
                                self.logger.debug(f"Error parsing injury row: {e}")
                                continue
            
        except Exception as e:
            self.logger.error(f"Error scraping injuries from separate page: {e}")
            return []
        
        self.logger.debug(f"Extracted {len(injuries)} injury records")
        return injuries
    
    def _get_cell_value(self, cells, header_mapping, possible_headers):
        """Get cell value by trying multiple possible header names."""
        for header in possible_headers:
            if header in header_mapping:
                idx = header_mapping[header]
                if idx < len(cells):
                    return normalize_text(extract_text_safe(cells[idx]))
        return ""
    
    def _extract_horse_name_from_page(self, page: Page) -> Optional[str]:
        """Extract horse name from the current page."""
        try:
            # Look for horse name in various places on the page
            selectors = [
                "h1",
                ".horse-name",
                ".title",
                "title"
            ]
            
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = normalize_text(extract_text_safe(element))
                        if text and len(text) < 20:  # Reasonable horse name length
                            return text
                except Exception:
                    continue
            
            # Also try to extract from page title
            title = page.title()
            if title and "馬匹資料" in title:
                # Extract horse name from title like "友得盈 - 馬匹資料"
                parts = title.split(" - ")
                if len(parts) > 0:
                    return parts[0].strip()
            
        except Exception as e:
            self.logger.debug(f"Error extracting horse name: {e}")
        
        return None
    
    def _scrape_injuries(self, page: Page) -> List[InjuryRecord]:
        """Scrape injury/health records from the injuries tab."""
        selector_helper = SelectorHelper(page, self.logger)
        
        try:
            # Find and click injuries tab
            injuries_tab = selector_helper.find_tab_by_text(DETAIL_TABS["injuries"])
            if not injuries_tab:
                self.logger.debug("No injuries tab found")
                return []
            
            # Click tab and wait for content
            if not selector_helper.click_tab_safe(injuries_tab):
                return []
            
            selector_helper.wait_for_tab_content()
            random_delay()
            
            # Find injuries table
            table = selector_helper.find_table_in_content()
            if not table:
                self.logger.debug("No injuries table found")
                return []
            
            # Extract injuries data
            injuries_data = selector_helper.extract_table_data(table)
            injuries = []
            
            for row_data in injuries_data:
                try:
                    # Map common field names to our schema
                    date = row_data.get("日期", row_data.get("Date", ""))
                    description = row_data.get("描述", row_data.get("Description", row_data.get("傷病", "")))
                    
                    if date or description:  # Only add if we have some data
                        injuries.append(InjuryRecord(
                            date=date,
                            description=description
                        ))
                except Exception as e:
                    self.logger.debug(f"Error parsing injury record: {e}")
                    continue
            
            self.logger.debug(f"Extracted {len(injuries)} injury records")
            return injuries
            
        except Exception as e:
            self.logger.error(f"Error scraping injuries: {e}")
            return []
    
    def _scrape_past_runs(self, page: Page) -> List[PastRunRecord]:
        """Scrape past performance records from the past runs tab."""
        selector_helper = SelectorHelper(page, self.logger)
        
        try:
            # Find and click past runs tab
            past_runs_tab = selector_helper.find_tab_by_text(DETAIL_TABS["past_runs"])
            if not past_runs_tab:
                self.logger.debug("No past runs tab found")
                return []
            
            # Click tab and wait for content
            if not selector_helper.click_tab_safe(past_runs_tab):
                return []
            
            selector_helper.wait_for_tab_content()
            random_delay()
            
            # Find past runs table
            table = selector_helper.find_table_in_content()
            if not table:
                self.logger.debug("No past runs table found")
                return []
            
            # Extract past runs data (limit to last 6 races)
            past_runs_data = selector_helper.extract_table_data(table, max_rows=6)
            past_runs = []
            
            for row_data in past_runs_data:
                try:
                    # Map common field names to our schema
                    past_run = PastRunRecord(
                        race_date=row_data.get("賽事日期", row_data.get("Date", "")),
                        venue=row_data.get("場地", row_data.get("Venue", "")),
                        distance=row_data.get("途程", row_data.get("Distance", "")),
                        barrier=row_data.get("檔位", row_data.get("Barrier", "")),
                        weight=row_data.get("負磅", row_data.get("Weight", "")),
                        jockey=row_data.get("騎師", row_data.get("Jockey", "")),
                        position=row_data.get("名次", row_data.get("Position", "")),
                        time=row_data.get("時間", row_data.get("Time", "")),
                        equipment=row_data.get("配備", row_data.get("Equipment", "")),
                        rating=row_data.get("評分", row_data.get("Rating", "")),
                        odds=row_data.get("獨贏", row_data.get("Odds", "")),
                    )
                    
                    # Only add if we have meaningful data
                    if any([past_run.race_date, past_run.venue, past_run.position]):
                        past_runs.append(past_run)
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing past run record: {e}")
                    continue
            
            self.logger.debug(f"Extracted {len(past_runs)} past run records")
            return past_runs
            
        except Exception as e:
            self.logger.error(f"Error scraping past runs: {e}")
            return []
    
    def _scrape_profile(self, page: Page) -> str:
        """Scrape horse profile/basic information."""
        selector_helper = SelectorHelper(page, self.logger)
        
        try:
            # Find and click profile tab
            profile_tab = selector_helper.find_tab_by_text(DETAIL_TABS["profile"])
            if not profile_tab:
                self.logger.debug("No profile tab found")
                return ""
            
            # Click tab and wait for content
            if not selector_helper.click_tab_safe(profile_tab):
                return ""
            
            selector_helper.wait_for_tab_content()
            random_delay()
            
            # Find profile content
            profile_content = None
            content_selectors = [
                ".profile",
                ".basicInfo", 
                ".horseInfo",
                ".tabContent",
                ".content"
            ]
            
            for selector in content_selectors:
                try:
                    profile_content = page.query_selector(selector)
                    if profile_content:
                        break
                except Exception:
                    continue
            
            if not profile_content:
                self.logger.debug("No profile content found")
                return ""
            
            # Extract profile text
            profile_text = profile_content.inner_text()
            if profile_text:
                # Clean up the text
                import re
                profile_text = re.sub(r'\s+', ' ', profile_text)  # Normalize whitespace
                profile_text = profile_text.strip()
                
                self.logger.debug(f"Extracted profile text: {len(profile_text)} characters")
                return profile_text
            
        except Exception as e:
            self.logger.error(f"Error scraping profile: {e}")
        
        return ""