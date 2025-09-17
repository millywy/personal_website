#!/bin/bash

# Example script for running HKJC scraper
# This script demonstrates how to use the scraper with different options

set -e  # Exit on any error

echo "HKJC Scraper Example Script"
echo "=========================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if the scraper module is available
if ! python -c "import hkjc_scraper" 2>/dev/null; then
    echo "Error: hkjc_scraper module not found. Please install dependencies first:"
    echo "  pip install -r requirements.txt"
    echo "  playwright install chromium"
    exit 1
fi

# Example 1: Basic scraping
echo ""
echo "Example 1: Basic race scraping"
echo "Command: python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 1 --out example_hv_r1.json"
echo ""

# Uncomment the line below to run the actual scraping
# python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 1 --out example_hv_r1.json

echo "Note: Uncomment the line above to run actual scraping"

# Example 2: With checkpoint support
echo ""
echo "Example 2: Scraping with checkpoint support"
echo "Command: python -m hkjc_scraper --date 2025/09/17 --course ST --raceno 2 --out example_st_r2.json --checkpoint example_st_r2.chk.json"
echo ""

# Uncomment the line below to run the actual scraping
# python -m hkjc_scraper --date 2025/09/17 --course ST --raceno 2 --out example_st_r2.json --checkpoint example_st_r2.chk.json

echo "Note: Uncomment the line above to run actual scraping"

# Example 3: Debug mode with visible browser
echo ""
echo "Example 3: Debug mode with visible browser"
echo "Command: python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 3 --out example_hv_r3.json --headful --log-level DEBUG"
echo ""

# Uncomment the line below to run the actual scraping
# python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 3 --out example_hv_r3.json --headful --log-level DEBUG

echo "Note: Uncomment the line above to run actual scraping"

# Example 4: Multiple races
echo ""
echo "Example 4: Scraping multiple races"
echo "Commands:"
echo "  python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 1 --out hv_r1.json"
echo "  python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 2 --out hv_r2.json"
echo "  python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 3 --out hv_r3.json"
echo ""

# Uncomment the lines below to run multiple races
# python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 1 --out hv_r1.json
# python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 2 --out hv_r2.json
# python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 3 --out hv_r3.json

echo "Note: Uncomment the lines above to run multiple races"

echo ""
echo "Script completed. Check the output files for results."
echo ""
echo "To run actual scraping, uncomment the relevant commands above."
echo "Make sure to:"
echo "  1. Use valid race dates (check HKJC website)"
echo "  2. Use correct course codes (HV for Happy Valley, ST for Sha Tin)"
echo "  3. Use valid race numbers (1-12)"
echo "  4. Ensure you have internet connection"
echo ""
