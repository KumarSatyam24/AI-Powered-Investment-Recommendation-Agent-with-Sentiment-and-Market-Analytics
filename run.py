#!/usr/bin/env python3
"""
Quick Start Script
=================

Fast access to common system functions.
"""

import sys
import os
import subprocess

def show_usage():
    """Display usage information."""
    print("""
🚀 Investment Recommendation System - Quick Access
==================================================

Usage: python run.py <command> [arguments]

Commands:
  analyze <TICKER>     - Analyze a stock (e.g., python run.py analyze AAPL)
  dashboard           - Start web dashboard
  health              - Check system health
  test                - Run all tests
  setup               - Initial system setup

Examples:
  python run.py analyze TSLA
  python run.py dashboard
  python run.py health
""")

def main():
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'analyze':
        if len(sys.argv) < 3:
            print("❌ Please specify a stock ticker: python run.py analyze AAPL")
            sys.exit(1)
        ticker = sys.argv[2].upper()
        subprocess.run([sys.executable, "main.py", ticker])
    
    elif command == 'dashboard':
        print("🌐 Starting web dashboard...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/ui/dashboard.py"])
    
    elif command == 'health':
        print("🏥 Checking system health...")
        subprocess.run([sys.executable, "scripts/health_check.py"])
    
    elif command == 'test':
        print("🧪 Running tests...")
        subprocess.run([sys.executable, "tests/api_test.py"])
    
    elif command == 'setup':
        print("⚙️ Running system setup...")
        subprocess.run([sys.executable, "scripts/setup.py"])
    
    else:
        print(f"❌ Unknown command: {command}")
        show_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
