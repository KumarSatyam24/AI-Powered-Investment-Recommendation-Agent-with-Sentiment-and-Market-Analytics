#!/usr/bin/env python3
"""
Setup Script for Investment Recommendation System
=================================================

Handles initial setup, dependency installation, and configuration.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def check_api_keys():
    """Check if API keys are configured."""
    print("🔑 Checking API key configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    required_keys = [
        'ALPHA_VANTAGE_KEY',
        'FRED_API_KEY', 
        'MARKETAUX_API_KEY',
        'NEWS_API_KEY'
    ]
    
    missing_keys = []
    for key in required_keys:
        if f'{key}=YOUR_' in env_content or key not in env_content:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("📝 Please update your .env file with actual API keys")
        return False
    else:
        print("✅ All API keys configured!")
        return True

def run_tests():
    """Run system tests."""
    print("🧪 Running system tests...")
    try:
        os.chdir("tests")
        result = subprocess.run([sys.executable, "api_test.py"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False
    finally:
        os.chdir("..")

def setup_directories():
    """Ensure all necessary directories exist."""
    print("📁 Setting up directory structure...")
    
    directories = [
        "data",
        "logs", 
        "cache",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directory structure ready!")

def main():
    """Main setup function."""
    print("🚀 Investment Recommendation System Setup")
    print("=" * 50)
    
    # Setup directories
    setup_directories()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check API keys
    keys_configured = check_api_keys()
    
    # Run tests
    if keys_configured:
        if run_tests():
            print("\n🎉 Setup completed successfully!")
            print("💡 Try: python main.py AAPL")
            print("🌐 Or run: streamlit run src/ui/dashboard.py")
        else:
            print("\n⚠️  Setup completed with test failures")
    else:
        print("\n⚠️  Setup completed but API keys need configuration")
        print("📖 See docs/API_INTEGRATION_GUIDE.md for help")

if __name__ == "__main__":
    main()
