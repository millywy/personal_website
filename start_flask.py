#!/usr/bin/env python3
"""
Startup script for HKJC Race Scraper Flask Application
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Flask requirements if not already installed."""
    try:
        import flask
        print("✅ Flask is already installed")
    except ImportError:
        print("📦 Installing Flask requirements...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_flask.txt'])

def start_app():
    """Start the Flask application."""
    print("🏇 HKJC Race Scraper - Flask Web Application")
    print("=" * 60)
    print("🚀 Starting Flask server...")
    print("🌐 Open your browser and go to: http://localhost:8080")
    print("=" * 60)
    print()
    
    # Start the Flask app
    os.system(f"{sys.executable} app.py")

if __name__ == '__main__':
    install_requirements()
    start_app()
