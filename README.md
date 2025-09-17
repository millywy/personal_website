# HKJC Race Data Scraper

A production-ready Python scraper for Hong Kong Jockey Club race data that extracts comprehensive horse information including race details, injuries, past performance, and profiles.

## Features

- **Complete Race Data**: Scrapes top-line race information (horse numbers, names, jockeys, trainers, odds, ratings, etc.)
- **Detailed Horse Profiles**: Extracts injury records, past performance history, and basic horse information
- **Robust Scraping**: Dynamic column detection, retry logic with exponential backoff, and respectful throttling
- **Checkpoint Support**: Resume interrupted scraping sessions
- **Production Ready**: Comprehensive error handling, logging, and validation

## Installation

### Prerequisites

- Python 3.11 or higher
- Playwright browser binaries

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd hkjc-scraper
   ```

2. **Install dependencies**:
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Or using uv (faster)
   uv pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

4. **Configure environment** (optional):
   ```bash
   cp env.example .env
   # Edit .env with your preferred settings
   ```

## Quick Start

### Basic Usage

```bash
python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 1 --out hv_r1.json
```

### With Checkpoint Support

```bash
python -m hkjc_scraper \
  --date 2025/09/17 \
  --course HV \
  --raceno 1 \
  --out hv_r1.json \
  --checkpoint hv_r1.chk.json
```

### Headful Mode (Visible Browser)

```bash
python -m hkjc_scraper \
  --date 2025/09/17 \
  --course HV \
  --raceno 1 \
  --out hv_r1.json \
  --headful
```

## Command Line Options

| Option | Required | Description |
|--------|----------|-------------|
| `--date` | Yes | Race date in YYYY/MM/DD format |
| `--course` | Yes | Racecourse code (HV for Happy Valley, ST for Sha Tin) |
| `--raceno` | Yes | Race number (1-12) |
| `--out` | Yes | Output JSON file path |
| `--checkpoint` | No | Checkpoint file for resuming interrupted runs |
| `--headful` | No | Run browser in visible mode (default: headless) |
| `--max-retries` | No | Maximum retries per operation (default: 3) |
| `--log-level` | No | Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO) |

## Output Schema

The scraper outputs a JSON array of horse objects with the following exact schema:

```json
[
  {
    "馬號": "1",
    "馬匹ID": "12345",
    "馬名": "Horse Name",
    "馬匹編號": "A123",
    "最近6輪": "1-2-3-4-5-6",
    "排位": "3",
    "負磅": "126",
    "騎師": "Jockey Name",
    "練馬師": "Trainer Name",
    "獨贏": "3.5",
    "位置": "1.8",
    "當前評分": "85",
    "國際評分": "90",
    "配備": "B",
    "讓磅": "0",
    "練馬師喜好": "1",
    "傷病記錄": [
      {
        "date": "2025-01-01",
        "description": "Injury description"
      }
    ],
    "往績紀錄": [
      {
        "race_date": "2025-01-01",
        "venue": "HV",
        "distance": "1200",
        "barrier": "3",
        "weight": "126",
        "jockey": "Jockey Name",
        "position": "1",
        "time": "1:09.5",
        "equipment": "B",
        "rating": "85",
        "odds": "3.5"
      }
    ],
    "馬匹基本資料": "Age: 4, Sex: G, Color: Bay, Country: AUS, Sire: Sire Name, Dam: Dam Name, Owner: Owner Name"
  }
]
```

## Configuration

Create a `.env` file to customize behavior:

```env
# Browser settings
HEADLESS=true
MIN_DELAY_MS=400
MAX_DELAY_MS=1200

# Timeouts (in milliseconds)
PAGE_LOAD_TIMEOUT=30000
SELECTOR_TIMEOUT=10000
NAVIGATION_TIMEOUT=20000

# Retry settings
MAX_RETRIES=3
RETRY_BASE_DELAY_MS=1000
RETRY_MAX_DELAY_MS=5000

# Checkpoint settings
CHECKPOINT_INTERVAL=2

# User agent (optional)
USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

## Development

### Running Tests

```bash
# Unit tests only
python -m pytest tests/test_parsing_unit.py -v

# E2E tests (requires internet connection)
SKIP_E2E_TESTS=false python -m pytest tests/test_e2e_dryrun.py -v

# All tests
python -m pytest tests/ -v
```

### Code Quality

```bash
# Format code
black hkjc_scraper/ tests/

# Lint code
ruff check hkjc_scraper/ tests/

# Type checking
mypy hkjc_scraper/
```

## Troubleshooting

### Common Issues

1. **Playwright browser not found**:
   ```bash
   playwright install chromium
   ```

2. **Permission denied errors**:
   - Ensure you have write permissions for output and checkpoint files
   - Check that the output directory exists

3. **Network timeouts**:
   - Increase timeout values in `.env`
   - Check your internet connection
   - The HKJC website might be temporarily unavailable

4. **No horses found**:
   - Verify the race date, course, and race number are correct
   - Check if the race exists on the HKJC website
   - Some races might not be available immediately after posting

5. **Partial data extraction**:
   - Use checkpoint files to resume interrupted runs
   - Check logs for specific error messages
   - Some horse detail pages might be temporarily unavailable

### Debug Mode

Run with debug logging to see detailed information:

```bash
python -m hkjc_scraper \
  --date 2025/09/17 \
  --course HV \
  --raceno 1 \
  --out hv_r1.json \
  --log-level DEBUG
```

### Headful Mode for Debugging

Use `--headful` to see the browser in action:

```bash
python -m hkjc_scraper \
  --date 2025/09/17 \
  --course HV \
  --raceno 1 \
  --out hv_r1.json \
  --headful \
  --log-level DEBUG
```

## Architecture

The scraper is organized into several modules:

- **`main.py`**: CLI entrypoint and orchestration
- **`racecard.py`**: Race table scraping with dynamic column detection
- **`horse_detail.py`**: Individual horse detail page scraping
- **`selectors.py`**: Selector utilities and header mapping
- **`models.py`**: Pydantic models for data validation
- **`utils.py`**: Utility functions for logging, retries, and file operations
- **`constants.py`**: Configuration constants and URL templates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. Please respect the HKJC website's terms of service and robots.txt file. Use appropriate delays between requests and avoid overloading their servers.
