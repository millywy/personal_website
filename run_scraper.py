#!/usr/bin/env python3
"""
Simple script to run the HKJC scraper and serve the results via a local web server.
This allows users to get real data from the Python scraper.
"""

import subprocess
import json
import sys
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import time

def run_scraper(date, course, raceno):
    """Run the HKJC scraper with the given parameters."""
    try:
        # Run the scraper
        result = subprocess.run([
            sys.executable, '-m', 'hkjc_scraper',
            '--date', date,
            '--course', course,
            '--raceno', str(raceno),
            '--out', 'scraped_data.json',
            '--log-level', 'INFO'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode != 0:
            print(f"Error running scraper: {result.stderr}")
            return None
            
        # Read the output file
        with open('scraped_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_data_endpoint(data):
    """Create a simple data endpoint for the web interface."""
    class DataHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/data':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
            else:
                super().do_GET()
                
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
    
    return DataHandler

def main():
    if len(sys.argv) != 4:
        print("Usage: python run_scraper.py <date> <course> <raceno>")
        print("Example: python run_scraper.py 2025/09/17 HV 4")
        sys.exit(1)
    
    date, course, raceno = sys.argv[1], sys.argv[2], int(sys.argv[3])
    
    print(f"Scraping HKJC data for {date} {course} Race {raceno}...")
    
    # Run the scraper
    data = run_scraper(date, course, raceno)
    
    if data is None:
        print("Failed to scrape data")
        sys.exit(1)
    
    print(f"Successfully scraped {len(data.get('horses', []))} horses")
    
    # Start a local web server
    port = 8080
    handler = create_data_endpoint(data)
    httpd = HTTPServer(('localhost', port), handler)
    
    print(f"Starting web server on http://localhost:{port}")
    print("Open the website and it will automatically load the real scraped data!")
    
    # Open the website
    webbrowser.open(f'http://localhost:{port}')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.shutdown()

if __name__ == '__main__':
    main()
