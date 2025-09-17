"""Selector utilities for dynamic header mapping and XPath helpers."""

import re
from typing import Dict, List, Optional, Tuple

from playwright.sync_api import ElementHandle, Page

from .constants import EXPECTED_HEADERS, SELECTORS
from .utils import extract_text_safe, normalize_text, setup_logging


class SelectorHelper:
    """Helper class for finding elements using dynamic selectors."""
    
    def __init__(self, page: Page, logger=None):
        self.page = page
        self.logger = logger or setup_logging()
    
    def find_table_by_headers(
        self, 
        expected_headers: List[str],
        table_selectors: Optional[List[str]] = None
    ) -> Optional[ElementHandle]:
        """Find table containing the expected headers."""
        if table_selectors is None:
            table_selectors = [SELECTORS["race_table"]]
        
        # First try to find tables with specific selectors
        for table_selector in table_selectors:
            try:
                tables = self.page.query_selector_all(table_selector)
                for table in tables:
                    if self._table_has_headers(table, expected_headers):
                        self.logger.debug(f"Found table with headers: {expected_headers}")
                        return table
            except Exception as e:
                self.logger.debug(f"Error checking table selector '{table_selector}': {e}")
                continue
        
        # If no table found with specific selectors, try all tables on the page
        try:
            all_tables = self.page.query_selector_all("table")
            for table in all_tables:
                if self._table_has_headers(table, expected_headers):
                    self.logger.debug(f"Found table with headers in generic search: {expected_headers}")
                    return table
        except Exception as e:
            self.logger.debug(f"Error in generic table search: {e}")
        
        self.logger.warning(f"No table found with expected headers: {expected_headers}")
        return None
    
    def _table_has_headers(self, table: ElementHandle, expected_headers: List[str]) -> bool:
        """Check if table contains the expected headers."""
        try:
            # Get all header cells (th elements or first row cells)
            header_cells = table.query_selector_all("th")
            if not header_cells:
                # If no th elements, check first row
                first_row = table.query_selector("tr")
                if first_row:
                    header_cells = first_row.query_selector_all("td, th")
            
            if not header_cells:
                return False
            
            # Extract header texts
            header_texts = []
            for cell in header_cells:
                text = normalize_text(extract_text_safe(cell))
                if text:
                    header_texts.append(text)
            
            # Check if we have at least some of the expected headers
            found_headers = 0
            for expected in expected_headers:
                for header_text in header_texts:
                    if self._header_matches(expected, header_text):
                        found_headers += 1
                        break
            
            # Require at least 3 matching headers to be confident
            return found_headers >= 3
            
        except Exception as e:
            self.logger.debug(f"Error checking table headers: {e}")
            return False
    
    def _header_matches(self, expected: str, actual: str) -> bool:
        """Check if header text matches expected (with fuzzy matching)."""
        # Exact match
        if expected == actual:
            return True
        
        # Contains match
        if expected in actual or actual in expected:
            return True
        
        # Remove common variations and normalize
        expected_clean = re.sub(r'[^\w]', '', expected)
        actual_clean = re.sub(r'[^\w]', '', actual)
        
        if expected_clean == actual_clean:
            return True
        
        # Additional fuzzy matching for Chinese characters
        # Check if the core characters match (ignoring punctuation)
        expected_core = re.sub(r'[^\u4e00-\u9fff]', '', expected)
        actual_core = re.sub(r'[^\u4e00-\u9fff]', '', actual)
        
        if expected_core and actual_core:
            # Check if one contains the other
            if expected_core in actual_core or actual_core in expected_core:
                return True
            
            # Check for partial matches (at least 2 characters)
            if len(expected_core) >= 2 and len(actual_core) >= 2:
                for i in range(len(expected_core) - 1):
                    if expected_core[i:i+2] in actual_core:
                        return True
        
        return False
    
    def get_header_column_map(
        self, 
        table: ElementHandle, 
        expected_headers: List[str]
    ) -> Dict[str, int]:
        """Get mapping of header text to column index."""
        column_map = {}
        
        try:
            # Get header row
            header_row = table.query_selector("tr")
            if not header_row:
                return column_map
            
            # Get all header cells
            header_cells = header_row.query_selector_all("td, th")
            
            for col_index, cell in enumerate(header_cells):
                header_text = normalize_text(extract_text_safe(cell))
                if not header_text:
                    continue
                
                # Find matching expected header
                for expected in expected_headers:
                    if self._header_matches(expected, header_text):
                        column_map[expected] = col_index
                        self.logger.debug(f"Mapped header '{expected}' to column {col_index}")
                        break
            
        except Exception as e:
            self.logger.error(f"Error mapping headers: {e}")
        
        return column_map
    
    def get_cell_by_header(
        self, 
        row: ElementHandle, 
        header: str, 
        column_map: Dict[str, int]
    ) -> str:
        """Get cell text by header name using column mapping."""
        try:
            if header not in column_map:
                return ""
            
            col_index = column_map[header]
            cells = row.query_selector_all("td, th")
            
            if col_index < len(cells):
                return normalize_text(extract_text_safe(cells[col_index]))
            
        except Exception as e:
            self.logger.debug(f"Error getting cell for header '{header}': {e}")
        
        return ""
    
    def find_tab_by_text(
        self, 
        tab_texts: List[str], 
        tab_selectors: Optional[List[str]] = None
    ) -> Optional[ElementHandle]:
        """Find tab element by Chinese text."""
        if tab_selectors is None:
            tab_selectors = [SELECTORS["detail_tabs"]]
        
        for tab_selector in tab_selectors:
            try:
                tabs = self.page.query_selector_all(tab_selector)
                for tab in tabs:
                    tab_text = normalize_text(extract_text_safe(tab))
                    for target_text in tab_texts:
                        if self._header_matches(target_text, tab_text):
                            self.logger.debug(f"Found tab: '{target_text}' -> '{tab_text}'")
                            return tab
            except Exception as e:
                self.logger.debug(f"Error checking tab selector '{tab_selector}': {e}")
                continue
        
        self.logger.warning(f"No tab found for texts: {tab_texts}")
        return None
    
    def click_tab_safe(self, tab: ElementHandle) -> bool:
        """Safely click tab element."""
        try:
            # Check if tab is already active
            if tab.get_attribute("class") and "active" in tab.get_attribute("class"):
                self.logger.debug("Tab is already active")
                return True
            
            tab.click()
            self.logger.debug("Tab clicked successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking tab: {e}")
            return False
    
    def wait_for_tab_content(
        self, 
        content_selectors: Optional[List[str]] = None,
        timeout: int = 5000
    ) -> bool:
        """Wait for tab content to load."""
        if content_selectors is None:
            content_selectors = [SELECTORS["detail_content"]]
        
        for selector in content_selectors:
            try:
                self.page.wait_for_selector(selector, timeout=timeout)
                return True
            except Exception:
                continue
        
        self.logger.warning("Tab content did not load within timeout")
        return False
    
    def find_table_in_content(
        self, 
        content_selectors: Optional[List[str]] = None
    ) -> Optional[ElementHandle]:
        """Find table within tab content."""
        if content_selectors is None:
            content_selectors = [SELECTORS["detail_content"]]
        
        for content_selector in content_selectors:
            try:
                content = self.page.query_selector(content_selector)
                if content:
                    table = content.query_selector("table")
                    if table:
                        return table
            except Exception as e:
                self.logger.debug(f"Error finding table in content: {e}")
                continue
        
        return None
    
    def extract_table_data(
        self, 
        table: ElementHandle,
        max_rows: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Extract data from table as list of dictionaries."""
        data = []
        
        try:
            # Get header row
            header_row = table.query_selector("tr")
            if not header_row:
                return data
            
            # Get headers
            header_cells = header_row.query_selector_all("td, th")
            headers = []
            for cell in header_cells:
                header_text = normalize_text(extract_text_safe(cell))
                headers.append(header_text)
            
            # Get data rows
            rows = table.query_selector_all("tr")[1:]  # Skip header row
            if max_rows:
                rows = rows[:max_rows]
            
            for row in rows:
                cells = row.query_selector_all("td, th")
                row_data = {}
                
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        cell_text = normalize_text(extract_text_safe(cell))
                        row_data[headers[i]] = cell_text
                
                if row_data:  # Only add non-empty rows
                    data.append(row_data)
            
        except Exception as e:
            self.logger.error(f"Error extracting table data: {e}")
        
        return data
    
    def find_horse_links(self, table: ElementHandle) -> List[Tuple[str, str]]:
        """Find horse detail links in table rows."""
        links = []
        
        try:
            rows = table.query_selector_all("tr")[1:]  # Skip header row
            
            for row in rows:
                # Look for links in the row
                link_elements = row.query_selector_all("a")
                for link in link_elements:
                    href = link.get_attribute("href")
                    if href and ("Horse.aspx" in href or "horse" in href):
                        link_text = normalize_text(extract_text_safe(link))
                        links.append((link_text, href))
                        break  # Only take first link per row
            
        except Exception as e:
            self.logger.error(f"Error finding horse links: {e}")
        
        return links
