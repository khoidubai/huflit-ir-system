"""
Authenticated crawler sử dụng Playwright để handle Office 365 SSO login.
Lưu session state để reuse cho các lần crawl sau.

Usage:
    # Lần đầu - cần login thủ công
    python crawler/auth_spider.py --login
    
    # Các lần sau - reuse session
    python crawler/auth_spider.py --max-pages 500
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from crawler.config import (
    BASE_URL,
    CATEGORIES,
    RAW_DATA_DIR,
    CRAWL_DELAY,
)

# Session state file
SESSION_FILE = PROJECT_ROOT / "data" / "session_state.json"

visited_urls = set()


def save_session_state(context):
    """Lưu cookies và storage state để reuse"""
    state = context.storage_state()
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    print(f"✅ Session saved → {SESSION_FILE}")


def login_portal(page):
    """
    Hướng dẫn user login thủ công qua Office 365.
    Chờ user login xong rồi lưu session.
    """
    print("\n" + "="*60)
    print("🔐 AUTHENTICATION REQUIRED")
    print("="*60)
    print("\nBước 1: Browser sẽ mở portal.huflit.edu.vn")
    print("Bước 2: Click nút 'Office 365 for Student'")
    print("Bước 3: Đăng nhập với tài khoản @student.huflit.edu.vn")
    print("Bước 4: Sau khi login xong, nhấn ENTER trong terminal này")
    print("\n" + "="*60 + "\n")
    
    page.goto(BASE_URL)
    
    # Chờ user login
    input("👉 Nhấn ENTER sau khi đã login thành công...")
    
    print("✅ Login thành công!")
    return True


def save_html(url, html):
    """Lưu HTML vào data/raw/"""
    today = datetime.now().strftime("%Y-%m-%d")
    folder = RAW_DATA_DIR / today
    folder.mkdir(parents=True, exist_ok=True)
    
    # Extract news ID từ URL
    if "/News/Detail/" in url:
        news_id = url.split("/News/Detail/")[1].split("/")[0]
        filepath = folder / f"{news_id}.html"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        
        return filepath
    return None


def extract_detail_links(page):
    """Extract tất cả links /News/Detail/ từ trang hiện tại"""
    links = page.eval_on_selector_all(
        "a[href*='/News/Detail/']",
        "elements => elements.map(e => e.href)"
    )
    
    # Filter unique links
    unique_links = []
    for link in links:
        if link not in visited_urls:
            unique_links.append(link)
    
    return unique_links


def crawl_detail(page, url):
    """Crawl một trang detail"""
    news_id = url.split("/News/Detail/")[1].split("/")[0]
    
    today = datetime.now().strftime("%Y-%m-%d")
    folder = RAW_DATA_DIR / today
    filepath = folder / f"{news_id}.html"
    
    # Skip nếu đã crawl
    if filepath.exists():
        print(f"⏩ Skip (exists): {news_id}")
        return
    
    print(f"📄 Crawling: {url}")
    
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Đợi content load
        page.wait_for_selector("div[style*='overflow:auto']", timeout=10000)
        
        html = page.content()
        save_html(url, html)
        
        visited_urls.add(url)
        
        time.sleep(CRAWL_DELAY)
        
    except Exception as e:
        print(f"❌ Error crawling {url}: {e}")


def crawl_category(page, category_name, type_id, max_pages):
    """Crawl một category với pagination"""
    print(f"\n📂 Category: {category_name} (Type ID: {type_id})")
    
    page_num = 1
    total = 0
    
    while total < max_pages:
        url = f"{BASE_URL}/News/Type/{type_id}?page={page_num}"
        print(f"\n🔎 List page {page_num}: {url}")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Extract links
            links = extract_detail_links(page)
            
            if not links:
                print(f"⚠️ No more links found on page {page_num}")
                break
            
            print(f"   Found {len(links)} detail links")
            
            # Crawl từng detail page
            for link in links:
                if total >= max_pages:
                    break
                
                crawl_detail(page, link)
                total += 1
            
            page_num += 1
            time.sleep(CRAWL_DELAY)
            
        except Exception as e:
            print(f"❌ Error on list page {page_num}: {e}")
            break
    
    print(f"✅ Category '{category_name}' done: {total} pages crawled")


def crawl_all(page, max_pages_per_category):
    """Crawl tất cả categories"""
    for category_name, type_id in CATEGORIES.items():
        crawl_category(page, category_name, type_id, max_pages_per_category)


def main():
    parser = argparse.ArgumentParser(
        description="Authenticated crawler cho portal.huflit.edu.vn"
    )
    
    parser.add_argument(
        "--login",
        action="store_true",
        help="Chạy login flow và lưu session, sau đó crawl luôn"
    )
    
    parser.add_argument(
        "--login-only",
        action="store_true",
        help="Chỉ login và lưu session, KHÔNG crawl"
    )
    
    parser.add_argument(
        "--max-pages",
        type=int,
        default=500,
        help="Max pages per category"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Chạy browser ẩn (không hiển thị UI)"
    )
    
    args = parser.parse_args()
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=args.headless)
        
        # Tạo context
        if SESSION_FILE.exists() and not args.login:
            # Reuse session
            print(f"📂 Loading session from {SESSION_FILE}")
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            context = browser.new_context(storage_state=state)
        else:
            # New session
            context = browser.new_context()
        
        page = context.new_page()
        
        # Login nếu cần
        if args.login or args.login_only or not SESSION_FILE.exists():
            success = login_portal(page)
            if not success:
                print("❌ Login failed")
                browser.close()
                return
            
            save_session_state(context)
            
            # Nếu chỉ login thôi → dừng
            if args.login_only:
                print("\n✅ Login completed! Session saved.")
                print("👉 Để crawl, chạy: python crawler/auth_spider.py")
                browser.close()
                return
        
        # Verify session còn valid không
        print("\n🔍 Verifying session...")
        page.goto(BASE_URL)
        
        # Check xem có bị redirect về login page không
        current_url = page.url
        if "login" in current_url.lower() or page.query_selector("input[type='password']"):
            print("❌ Session expired - bị redirect về login page")
            print("👉 Chạy: python crawler/auth_spider.py --login-only")
            browser.close()
            return
        
        print("✅ Session valid!")
        
        # Start crawling
        print(f"\n🚀 Starting crawl (max {args.max_pages} pages per category)...\n")
        crawl_all(page, args.max_pages)
        
        # Save session lại (refresh cookies)
        save_session_state(context)
        
        browser.close()
        
        print("\n✅ Crawl finished!")
        print(f"📁 Raw HTML saved in: {RAW_DATA_DIR}")


if __name__ == "__main__":
    main()
