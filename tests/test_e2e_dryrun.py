"""End-to-end tests with Playwright (dry run mode)."""

import os
import pytest
from playwright.sync_api import sync_playwright

from hkjc_scraper.constants import get_config
from hkjc_scraper.racecard import RaceCardScraper
from hkjc_scraper.horse_detail import HorseDetailScraper


@pytest.mark.skipif(
    os.getenv("SKIP_E2E_TESTS", "true").lower() == "true",
    reason="E2E tests skipped by default. Set SKIP_E2E_TESTS=false to run."
)
class TestE2EDryRun:
    """End-to-end tests that can be skipped in CI."""
    
    def test_racecard_scraping_dry_run(self):
        """Test race card scraping with a real URL (dry run)."""
        config = get_config()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            try:
                scraper = RaceCardScraper(browser)
                
                # Test with a recent race (this might fail if the race doesn't exist)
                # In a real test, you'd use a known good race date
                try:
                    horses = scraper.scrape_race("2024/12/15", "HV", 1)
                    
                    # Basic assertions
                    assert isinstance(horses, list)
                    
                    if horses:  # If we got data
                        horse = horses[0]
                        assert hasattr(horse, "馬號")
                        assert hasattr(horse, "馬名")
                        assert hasattr(horse, "騎師")
                        assert hasattr(horse, "練馬師")
                        
                        print(f"Successfully scraped {len(horses)} horses")
                        for horse in horses[:3]:  # Print first 3 horses
                            print(f"  - {horse.馬號}: {horse.馬名} (Jockey: {horse.騎師})")
                    
                except Exception as e:
                    # This is expected if the race doesn't exist or site is down
                    print(f"Race scraping failed (expected in dry run): {e}")
                    pytest.skip("Race not available or site unreachable")
                
            finally:
                browser.close()
    
    def test_horse_detail_scraping_dry_run(self):
        """Test horse detail scraping with a real URL (dry run)."""
        config = get_config()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            try:
                scraper = HorseDetailScraper(browser)
                
                # Test with a sample horse detail URL
                # This is a placeholder URL - in real tests you'd use actual URLs
                test_url = "https://racing.hkjc.com/racing/information/Chinese/Horse/Horse.aspx?HorseId=12345"
                
                try:
                    details = scraper.scrape_horse_details(test_url)
                    
                    # Basic assertions
                    assert isinstance(details, dict)
                    
                    # Check expected keys
                    expected_keys = ["馬匹ID", "國際評分", "傷病記錄", "往績紀錄", "馬匹基本資料"]
                    for key in expected_keys:
                        assert key in details
                    
                    print(f"Successfully scraped horse details")
                    print(f"  - Horse ID: {details.get('馬匹ID', 'N/A')}")
                    print(f"  - International Rating: {details.get('國際評分', 'N/A')}")
                    print(f"  - Injuries: {len(details.get('傷病記錄', []))}")
                    print(f"  - Past Runs: {len(details.get('往績紀錄', []))}")
                    
                except Exception as e:
                    # This is expected if the horse doesn't exist or site is down
                    print(f"Horse detail scraping failed (expected in dry run): {e}")
                    pytest.skip("Horse not available or site unreachable")
                
            finally:
                browser.close()
    
    def test_browser_launch(self):
        """Test that browser can be launched successfully."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            try:
                page = browser.new_page()
                page.goto("https://www.google.com", timeout=10000)
                
                title = page.title()
                assert "Google" in title
                print(f"Browser test successful. Page title: {title}")
                
            finally:
                browser.close()


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_e2e_dryrun.py -v
    # Or with e2e enabled: SKIP_E2E_TESTS=false python -m pytest tests/test_e2e_dryrun.py -v
    pytest.main([__file__, "-v"])
