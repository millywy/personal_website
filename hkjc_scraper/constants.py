"""Constants and configuration for HKJC scraper."""

import os
from typing import Dict, List

# URL templates
RACECARD_URL_TEMPLATE = (
    "https://racing.hkjc.com/racing/information/Chinese/racing/"
    "RaceCard.aspx?RaceDate={date}&Racecourse={course}&RaceNo={raceno}"
)

# Expected table headers in Chinese (based on actual HKJC website structure)
EXPECTED_HEADERS = [
    "編號",      # Horse number (馬號)
    "馬名",      # Horse name
    "排位體重",   # Barrier weight
    "負磅",      # Carried weight
    "評分",      # Rating (當前評分)
    "馬齡",      # Age
    "6次近績",   # Recent 6 runs (最近6輪)
    "練馬師",    # Trainer
    "優先參賽次序", # Priority
    "配備",      # Equipment
    # Additional headers that might be present
    "騎師",      # Jockey
    "讓磅",      # Weight allowance
    "獨贏",      # Win odds
    "位置",      # Place odds
    "練馬師喜好", # Trainer preference
    "馬匹編號",  # Horse code
    "國際評分",  # International rating
]

# Tab names for horse detail pages
DETAIL_TABS = {
    "injuries": ["傷病記錄", "健康記錄", "醫療記錄"],
    "past_runs": ["往績紀錄", "賽績", "歷史賽績"],
    "profile": ["馬匹基本資料", "基本資料", "馬匹資料"],
}

# Selectors for different page elements
SELECTORS = {
    "race_table": "table, .raceTable table, table.tableBorder",
    "table_headers": "th, .header, .tableHeader, thead th",
    "table_rows": "tr, tbody tr",
    "table_cells": "td, th",
    "horse_links": "a[href*='Horse.aspx'], a[href*='horse'], a[href*='HorseId']",
    "detail_tabs": ".tab, .tabButton, .tabLink",
    "detail_content": ".tabContent, .content, .detailContent",
    "injury_table": "table",
    "past_run_table": "table",
    "profile_content": ".profile, .basicInfo, .horseInfo",
}

# Configuration from environment variables
def get_config() -> Dict[str, any]:
    """Get configuration from environment variables with defaults."""
    return {
        "headless": os.getenv("HEADLESS", "true").lower() == "true",
        "min_delay_ms": int(os.getenv("MIN_DELAY_MS", "400")),
        "max_delay_ms": int(os.getenv("MAX_DELAY_MS", "1200")),
        "page_load_timeout": int(os.getenv("PAGE_LOAD_TIMEOUT", "30000")),
        "selector_timeout": int(os.getenv("SELECTOR_TIMEOUT", "10000")),
        "navigation_timeout": int(os.getenv("NAVIGATION_TIMEOUT", "20000")),
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),
        "retry_base_delay_ms": int(os.getenv("RETRY_BASE_DELAY_MS", "1000")),
        "retry_max_delay_ms": int(os.getenv("RETRY_MAX_DELAY_MS", "5000")),
        "checkpoint_interval": int(os.getenv("CHECKPOINT_INTERVAL", "2")),
        "user_agent": os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }

# Valid racecourses
VALID_COURSES = ["HV", "ST"]

# Date format
DATE_FORMAT = "%Y/%m/%d"
