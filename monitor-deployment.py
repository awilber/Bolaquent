#!/usr/bin/env python3
"""
Deployment Health Monitor for Bolaquent
Verifies that all critical functionality is working after deployment
"""

import requests
import sys
import time
from typing import List, Tuple


def check_endpoint(url: str, description: str) -> bool:
    """Check if an endpoint is accessible"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {description}: OK")
            return True
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return False


def check_static_file_content(url: str, expected_content: str, description: str) -> bool:
    """Check if static file contains expected content"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and expected_content in response.text:
            print(f"✅ {description}: Content verified")
            return True
        else:
            print(f"❌ {description}: Content missing or inaccessible")
            return False
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return False


def main():
    """Main monitoring function"""
    base_url = "http://54.161.222.239"
    
    print("🔍 Bolaquent Deployment Health Check")
    print("=" * 50)
    
    checks = [
        # Core application
        (f"{base_url}/", "Main application"),
        (f"{base_url}/auth/guest", "Guest authentication"),
        
        # Critical static files
        (f"{base_url}/static/css/themes.css", "Themes CSS"),
        (f"{base_url}/static/css/dashboard.css", "Dashboard CSS"),
        (f"{base_url}/static/css/hero-backgrounds.css", "Hero backgrounds CSS"),
        (f"{base_url}/static/css/additional-themes.css", "Additional themes CSS"),
    ]
    
    # Content verification checks
    content_checks = [
        (f"{base_url}/static/css/themes.css", "--surface-color", "CSS variables for text readability"),
        (f"{base_url}/static/css/themes.css", "backdrop-filter", "Backdrop filter for text contrast"),
    ]
    
    success_count = 0
    total_checks = len(checks) + len(content_checks)
    
    print("\n📡 Endpoint Accessibility Tests:")
    for url, description in checks:
        if check_endpoint(url, description):
            success_count += 1
        time.sleep(0.5)  # Rate limiting
    
    print("\n🎨 CSS Content Verification:")
    for url, content, description in content_checks:
        if check_static_file_content(url, content, description):
            success_count += 1
        time.sleep(0.5)  # Rate limiting
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {success_count}/{total_checks} checks passed")
    
    if success_count == total_checks:
        print("🎉 All deployment checks PASSED!")
        print("✅ Bolaquent is fully operational")
        return 0
    else:
        print("⚠️  Some deployment checks FAILED!")
        print("❌ Manual intervention may be required")
        return 1


if __name__ == "__main__":
    sys.exit(main())