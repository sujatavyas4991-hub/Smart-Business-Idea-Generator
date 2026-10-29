#!/usr/bin/env python3
"""
Smart Business Idea Generator - Startup Script
IBM Granite AI · Multi-Agent Agentic Application
"""
import os
import sys
import subprocess
import webbrowser
import time


def check_python():
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required. Please upgrade Python.")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]}")


def install_requirements():
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    print("📦 Installing dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", req_file, "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"⚠️  Some packages may not have installed correctly:\n{result.stderr[:500]}")
    else:
        print("✅ Dependencies installed successfully")


def main():
    print("=" * 60)
    print("  Smart Business Idea Generator")
    print("  Powered by IBM Granite AI · Multi-Agent System")
    print("=" * 60)
    print()

    check_python()

    install_requirements()

    print()
    print("🚀 Starting Flask application...")
    print("📍 URL: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print()

    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_APP"] = app_path

    # Open browser after delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:5000")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Run the app
    os.chdir(os.path.dirname(__file__))
    subprocess.run([sys.executable, "app.py"])


if __name__ == "__main__":
    main()
