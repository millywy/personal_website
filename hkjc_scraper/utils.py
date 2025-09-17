"""Utility functions for logging, retries, text normalization, and browser operations."""

import json
import logging
import random
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from .constants import get_config
from .models import HorseRecord


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Set up structured logging with rich formatting."""
    logger = logging.getLogger("hkjc_scraper")
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def normalize_text(text: str) -> str:
    """Normalize text by removing full-width spaces and collapsing whitespace."""
    if not text:
        return ""
    
    # Replace full-width spaces with regular spaces
    text = text.replace("　", " ")
    
    # Collapse multiple whitespace characters into single space
    text = re.sub(r"\s+", " ", text)
    
    # Strip leading/trailing whitespace
    return text.strip()


def random_delay() -> None:
    """Apply random delay between actions for respectful scraping."""
    config = get_config()
    delay_ms = random.randint(config["min_delay_ms"], config["max_delay_ms"])
    time.sleep(delay_ms / 1000.0)


def retry_with_backoff(
    func,
    max_retries: Optional[int] = None,
    base_delay_ms: Optional[int] = None,
    max_delay_ms: Optional[int] = None,
    logger: Optional[logging.Logger] = None,
) -> Any:
    """Retry function with exponential backoff and jitter."""
    config = get_config()
    max_retries = max_retries or config["max_retries"]
    base_delay_ms = base_delay_ms or config["retry_base_delay_ms"]
    max_delay_ms = max_delay_ms or config["retry_max_delay_ms"]
    
    if logger is None:
        logger = setup_logging()
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                # Exponential backoff with jitter
                delay_ms = min(
                    base_delay_ms * (2 ** attempt) + random.randint(0, 1000),
                    max_delay_ms
                )
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay_ms}ms..."
                )
                time.sleep(delay_ms / 1000.0)
            else:
                logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
    
    raise last_exception


def wait_for_selector_safe(
    page: Page,
    selector: str,
    timeout: Optional[int] = None,
    logger: Optional[logging.Logger] = None,
) -> bool:
    """Safely wait for selector with timeout and logging."""
    config = get_config()
    timeout = timeout or config["selector_timeout"]
    
    if logger is None:
        logger = setup_logging()
    
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        logger.warning(f"Selector '{selector}' not found within {timeout}ms")
        return False


def extract_text_safe(
    element,
    default: str = "",
    normalize: bool = True,
) -> str:
    """Safely extract text from element with fallback."""
    try:
        text = element.inner_text() if hasattr(element, 'inner_text') else str(element)
        return normalize_text(text) if normalize else text
    except Exception:
        return default


def extract_href_safe(element, default: str = "") -> str:
    """Safely extract href from element with fallback."""
    try:
        return element.get_attribute("href") or default
    except Exception:
        return default


def save_checkpoint(
    data: List[HorseRecord],
    checkpoint_path: Union[str, Path],
    logger: Optional[logging.Logger] = None,
) -> None:
    """Save checkpoint data to JSON file."""
    if logger is None:
        logger = setup_logging()
    
    try:
        checkpoint_path = Path(checkpoint_path)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict format for JSON serialization
        checkpoint_data = [record.model_dump() for record in data]
        
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Checkpoint saved: {len(data)} horses -> {checkpoint_path}")
    except Exception as e:
        logger.error(f"Failed to save checkpoint: {e}")


def load_checkpoint(
    checkpoint_path: Union[str, Path],
    logger: Optional[logging.Logger] = None,
) -> List[HorseRecord]:
    """Load checkpoint data from JSON file."""
    if logger is None:
        logger = setup_logging()
    
    try:
        checkpoint_path = Path(checkpoint_path)
        if not checkpoint_path.exists():
            logger.info(f"Checkpoint file not found: {checkpoint_path}")
            return []
        
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            checkpoint_data = json.load(f)
        
        # Convert back to HorseRecord objects
        records = [HorseRecord(**record_data) for record_data in checkpoint_data]
        logger.info(f"Checkpoint loaded: {len(records)} horses from {checkpoint_path}")
        return records
    except Exception as e:
        logger.error(f"Failed to load checkpoint: {e}")
        return []


def save_final_output(
    data: List[HorseRecord],
    output_path: Union[str, Path],
    logger: Optional[logging.Logger] = None,
) -> None:
    """Save final output data to JSON file."""
    if logger is None:
        logger = setup_logging()
    
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict format for JSON serialization
        output_data = [record.model_dump() for record in data]
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Final output saved: {len(data)} horses -> {output_path}")
    except Exception as e:
        logger.error(f"Failed to save final output: {e}")


def validate_date_format(date_str: str) -> bool:
    """Validate date string format (YYYY/MM/DD)."""
    try:
        time.strptime(date_str, "%Y/%m/%d")
        return True
    except ValueError:
        return False


def validate_course(course: str) -> bool:
    """Validate racecourse code."""
    from .constants import VALID_COURSES
    return course.upper() in VALID_COURSES


def validate_race_number(raceno: int) -> bool:
    """Validate race number."""
    return 1 <= raceno <= 12


def build_racecard_url(date: str, course: str, raceno: int) -> str:
    """Build racecard URL from parameters."""
    from .constants import RACECARD_URL_TEMPLATE
    return RACECARD_URL_TEMPLATE.format(
        date=date,
        course=course.upper(),
        raceno=raceno
    )
