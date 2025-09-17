"""Unit tests for HTML parsing helpers."""

import pytest
from unittest.mock import Mock

from hkjc_scraper.models import HorseRecord, InjuryRecord, PastRunRecord, ToplineData
from hkjc_scraper.utils import normalize_text, validate_date_format, validate_course, validate_race_number


class TestTextNormalization:
    """Test text normalization functions."""
    
    def test_normalize_text_basic(self):
        """Test basic text normalization."""
        assert normalize_text("  hello  world  ") == "hello world"
        assert normalize_text("") == ""
        assert normalize_text(None) == ""
    
    def test_normalize_text_fullwidth_spaces(self):
        """Test normalization of full-width spaces."""
        assert normalize_text("hello　world") == "hello world"
        assert normalize_text("　　hello　　") == "hello"
    
    def test_normalize_text_multiple_spaces(self):
        """Test normalization of multiple spaces."""
        assert normalize_text("hello    world") == "hello world"
        assert normalize_text("hello\t\nworld") == "hello world"


class TestValidation:
    """Test input validation functions."""
    
    def test_validate_date_format(self):
        """Test date format validation."""
        assert validate_date_format("2025/09/17") is True
        assert validate_date_format("2025/12/31") is True
        assert validate_date_format("2025/01/01") is True
        
        assert validate_date_format("2025-09-17") is False
        assert validate_date_format("25/09/17") is False
        assert validate_date_format("2025/9/17") is False
        assert validate_date_format("invalid") is False
    
    def test_validate_course(self):
        """Test course validation."""
        assert validate_course("HV") is True
        assert validate_course("ST") is True
        assert validate_course("hv") is True
        assert validate_course("st") is True
        
        assert validate_course("ABC") is False
        assert validate_course("") is False
    
    def test_validate_race_number(self):
        """Test race number validation."""
        assert validate_race_number(1) is True
        assert validate_race_number(6) is True
        assert validate_race_number(12) is True
        
        assert validate_race_number(0) is False
        assert validate_race_number(13) is False
        assert validate_race_number(-1) is False


class TestModels:
    """Test Pydantic models."""
    
    def test_injury_record(self):
        """Test InjuryRecord model."""
        injury = InjuryRecord(date="2025-01-01", description="Test injury")
        assert injury.date == "2025-01-01"
        assert injury.description == "Test injury"
        
        # Test with empty values
        injury_empty = InjuryRecord()
        assert injury_empty.date == ""
        assert injury_empty.description == ""
    
    def test_past_run_record(self):
        """Test PastRunRecord model."""
        past_run = PastRunRecord(
            race_date="2025-01-01",
            venue="HV",
            distance="1200",
            position="1"
        )
        assert past_run.race_date == "2025-01-01"
        assert past_run.venue == "HV"
        assert past_run.distance == "1200"
        assert past_run.position == "1"
    
    def test_topline_data(self):
        """Test ToplineData model."""
        data = {
            "馬號": "1",
            "馬名": "Test Horse",
            "騎師": "Test Jockey",
            "練馬師": "Test Trainer"
        }
        topline = ToplineData(**data)
        assert topline.馬號 == "1"
        assert topline.馬名 == "Test Horse"
        assert topline.騎師 == "Test Jockey"
        assert topline.練馬師 == "Test Trainer"
        
        # Test default values
        assert topline.馬匹ID == ""
        assert topline.傷病記錄 == []
        assert topline.往績紀錄 == []
    
    def test_horse_record(self):
        """Test HorseRecord model."""
        data = {
            "馬號": "1",
            "馬名": "Test Horse",
            "騎師": "Test Jockey",
            "練馬師": "Test Trainer",
            "傷病記錄": [{"date": "2025-01-01", "description": "Test injury"}],
            "往績紀錄": [{"race_date": "2025-01-01", "venue": "HV", "position": "1"}]
        }
        horse = HorseRecord(**data)
        assert horse.馬號 == "1"
        assert horse.馬名 == "Test Horse"
        assert len(horse.傷病記錄) == 1
        assert len(horse.往績紀錄) == 1
        assert horse.傷病記錄[0].date == "2025-01-01"
        assert horse.往績紀錄[0].venue == "HV"
    
    def test_string_conversion(self):
        """Test automatic string conversion."""
        data = {
            "馬號": 1,  # Integer should be converted to string
            "馬名": "Test Horse",
            "當前評分": 85.5,  # Float should be converted to string
        }
        topline = ToplineData(**data)
        assert topline.馬號 == "1"
        assert topline.當前評分 == "85.5"
        assert isinstance(topline.馬號, str)
        assert isinstance(topline.當前評分, str)


class TestSelectorHelper:
    """Test selector helper functionality."""
    
    def test_header_matching(self):
        """Test header text matching logic."""
        from hkjc_scraper.selectors import SelectorHelper
        
        # Mock page object
        mock_page = Mock()
        helper = SelectorHelper(mock_page)
        
        # Test exact matches
        assert helper._header_matches("馬號", "馬號") is True
        assert helper._header_matches("馬名", "馬名") is True
        
        # Test contains matches
        assert helper._header_matches("馬號", "馬號 (Horse No.)") is True
        assert helper._header_matches("馬名", "馬名 (Horse Name)") is True
        
        # Test no matches
        assert helper._header_matches("馬號", "騎師") is False
        assert helper._header_matches("馬名", "練馬師") is False


if __name__ == "__main__":
    pytest.main([__file__])
