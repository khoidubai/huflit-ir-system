"""
Script test nhanh để verify authentication và xem portal trả về bao nhiêu content.

Usage:
    python crawler/test_auth.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json
from playwright.sync_api import sync_playwright

SESSION_FILE = PROJECT_ROOT / "data" / "session_state.json"
BASE_URL = "https://portal.huflit.edu.vn"


def test_without_auth():
    """Test crawl KHÔNG có authentication"""
    print("\n" + "="*60)
    print("TEST 1: Crawl WITHOUT Authentication")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        test_url = f"{BASE_URL}/News/Type/1?page=1"
        page.goto(test_url, wait_until="networkidle")
        
        # Count detail links
        links = page.eval_on_selector_all(
            "a[href*='/News/Detail/']",
            "elements => elements.map(e => e.href)"
        )
        
        html = page.content()
        
        print(f"\n📊 Results:")
        print(f"   - URL: {test_url}")
        print(f"   - HTML size: {len(html):,} bytes")
        print(f"   - Detail links found: {len(set(links))}")
        print(f"   - Contains login form: {'login' in html.lower()}")
        
        # Check có content thật không
        has_content = page.query_selector("div[style*='overflow:auto']") is not None
        print(f"   - Has article content: {has_content}")
        
        browser.close()
        
        return len(set(links))


def test_with_auth():
    """Test crawl CÓ authentication"""
    print("\n" + "="*60)
    print("TEST 2: Crawl WITH Authentication")
    print("="*60)
    
    if not SESSION_FILE.exists():
        print(f"\n⚠️ Session file not found: {SESSION_FILE}")
        print("👉 Chạy trước: python crawler/auth_spider.py --login")
        return 0
    
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=state)
        page = context.new_page()
        
        test_url = f"{BASE_URL}/News/Type/1?page=1"
        page.goto(test_url, wait_until="networkidle")
        
        # Count detail links
        links = page.eval_on_selector_all(
            "a[href*='/News/Detail/']",
            "elements => elements.map(e => e.href)"
        )
        
        html = page.content()
        
        print(f"\n📊 Results:")
        print(f"   - URL: {test_url}")
        print(f"   - HTML size: {len(html):,} bytes")
        print(f"   - Detail links found: {len(set(links))}")
        
        # Check logged in by absence of login form
        has_login_form = page.query_selector("input[type='password']") is not None
        print(f"   - Logged in: {not has_login_form}")
        
        # Check có content thật không
        has_content = page.query_selector("div[style*='overflow:auto']") is not None
        print(f"   - Has article content: {has_content}")
        
        browser.close()
        
        return len(set(links))


def main():
    print("\n🧪 Testing Portal Authentication Impact\n")
    
    links_without = test_without_auth()
    links_with = test_with_auth()
    
    print("\n" + "="*60)
    print("📊 COMPARISON")
    print("="*60)
    print(f"Without auth: {links_without} links")
    print(f"With auth:    {links_with} links")
    print(f"Difference:   {links_with - links_without} more links")
    
    if links_with > links_without:
        print("\n✅ Authentication DOES increase content access!")
    elif links_with == links_without:
        print("\n⚠️ Authentication doesn't seem to matter (same content)")
    else:
        print("\n❓ Unexpected result - session might be expired")


if __name__ == "__main__":
    main()
