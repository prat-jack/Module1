#!/usr/bin/env python3
"""
Customer Analytics Dashboard Runner
Run this script to start the Streamlit application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'plotly', 
        'scikit-learn', 'xlsxwriter', 'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Handle special case where package name differs from import name
            import_name = 'sklearn' if package == 'scikit-learn' else package
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n🔧 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def run_dashboard():
    """Run the Streamlit dashboard"""
    app_path = Path(__file__).parent / "app.py"
    
    if not app_path.exists():
        print("❌ app.py not found!")
        return False
    
    print("🚀 Starting Customer Analytics Dashboard...")
    print("   Opening http://localhost:8502 in your browser...")
    print("   Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", "8502",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("📊 Customer Analytics Dashboard")
    print("=" * 40)
    
    if not check_requirements():
        sys.exit(1)
    
    run_dashboard()