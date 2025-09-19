#!/usr/bin/env python3
"""
Flask web application for HKJC Race Scraper
Direct integration - no separate local server needed
"""

from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import json
import os
import tempfile
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Global variable to store scraping status
scraping_status = {
    'is_running': False,
    'progress': 0,
    'message': '',
    'result': None,
    'error': None
}

def run_scraper_async(date, course, raceno):
    """Run the scraper in a background thread."""
    global scraping_status
    
    try:
        scraping_status['is_running'] = True
        scraping_status['progress'] = 0
        scraping_status['message'] = 'Starting scraper...'
        scraping_status['error'] = None
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        # Run the scraper
        scraping_status['message'] = 'Scraping race data...'
        scraping_status['progress'] = 25
        
        result = subprocess.run([
            'python', '-m', 'hkjc_scraper',
            '--date', date,
            '--course', course,
            '--raceno', str(raceno),
            '--out', output_file,
            '--log-level', 'INFO'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        scraping_status['progress'] = 75
        scraping_status['message'] = 'Processing results...'
        
        if result.returncode != 0:
            scraping_status['error'] = f"Scraper failed: {result.stderr}"
            scraping_status['is_running'] = False
            return
        
        # Read the output file
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Clean up temporary file
        os.unlink(output_file)
        
        scraping_status['progress'] = 100
        scraping_status['message'] = 'Scraping complete!'
        scraping_status['result'] = data
        scraping_status['is_running'] = False
        
    except Exception as e:
        scraping_status['error'] = f"Error: {str(e)}"
        scraping_status['is_running'] = False

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape():
    """API endpoint to start scraping."""
    global scraping_status
    
    if scraping_status['is_running']:
        return jsonify({
            'error': 'Scraper is already running. Please wait for it to complete.'
        }), 400
    
    data = request.json
    date = data.get('date')
    course = data.get('course')
    raceno = data.get('raceno')
    
    if not all([date, course, raceno]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    if course not in ['HV', 'ST']:
        return jsonify({'error': 'Invalid course. Must be HV or ST'}), 400
    
    if not (1 <= raceno <= 12):
        return jsonify({'error': 'Invalid race number. Must be between 1 and 12'}), 400
    
    # Start scraping in background thread
    thread = threading.Thread(target=run_scraper_async, args=(date, course, raceno))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'Scraping started',
        'status': 'running'
    })

@app.route('/api/status')
def status():
    """Get current scraping status."""
    return jsonify(scraping_status)

@app.route('/api/result')
def result():
    """Get scraping result if available."""
    if scraping_status['result']:
        return jsonify(scraping_status['result'])
    elif scraping_status['error']:
        return jsonify({'error': scraping_status['error']}), 500
    else:
        return jsonify({'message': 'No result available yet'}), 404

@app.route('/api/download')
def download():
    """Download the scraped data as JSON file."""
    if not scraping_status['result']:
        return jsonify({'error': 'No data available to download'}), 404
    
    # Create temporary file for download
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(scraping_status['result'], f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    # Generate filename
    filename = f"hkjc_race_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return send_file(
        temp_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )

if __name__ == '__main__':
    print("🏇 HKJC Race Scraper - Flask Web Application")
    print("=" * 50)
    print("Starting Flask server...")
    print("Open your browser and go to: http://localhost:8080")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=8080)
