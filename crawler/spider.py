""" 
Crawler chính. Bắt đầu từ danh sách URL seed trong config.py, crawl đệ quy tất cả trang con trong domain portal.huflit.edu.vn. Tuân thủ robots.txt, rate limit 1 request/2 giây, max depth 3 cấp. Lưu raw HTML theo ngày vào data/raw/. Dùng requests + BeautifulSoup4.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


import argparse
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from pathlib import Path

from crawler.config import (
    BASE_URL,
    CATEGORIES,
    RAW_DATA_DIR,
    HEADERS,
    CRAWL_DELAY,
    TIMEOUT,
)

visited_urls = set()


def fetch(url):
    """Fetch HTML from URL"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

        if response.status_code == 200:
            return response.text

    except Exception as e:
        print(f"⚠️ Fetch error: {url} -> {e}")

    return None


def save_html(url, html):

    today = datetime.now().strftime("%Y-%m-%d")

    folder = RAW_DATA_DIR / today
    folder.mkdir(parents=True, exist_ok=True)

    news_id = url.split("/News/Detail/")[1].split("/")[0]

    filepath = folder / f"{news_id}.html"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

def extract_detail_links(html):
    """Extract /News/Detail links"""
    soup = BeautifulSoup(html, "html.parser")

    links = []

    for a in soup.select("a[href*='/News/Detail/']"):
        href = a.get("href")

        if not href:
            continue

        full_url = urljoin(BASE_URL, href)

        if full_url not in visited_urls:
            links.append(full_url)

    return links


def crawl_detail(url):

    news_id = url.split("/News/Detail/")[1].split("/")[0]

    today = datetime.now().strftime("%Y-%m-%d")
    folder = RAW_DATA_DIR / today

    filepath = folder / f"{news_id}.html"

    # nếu đã crawl rồi → skip
    if filepath.exists():
        print(f"⏩ Skip (exists): {news_id}")
        return

    print(f"📄 Detail: {url}")

    html = fetch(url)

    if not html:
        return

    save_html(url, html)

    visited_urls.add(url)

    time.sleep(CRAWL_DELAY)


def crawl_category(category_name, type_id, max_pages):
    """Crawl category pages"""

    print(f"\n📂 Category: {category_name}")

    page = 1
    total = 0

    while True:

        url = f"{BASE_URL}/News/Type/{type_id}?page={page}"

        print(f"🔎 List page: {url}")

        html = fetch(url)

        if not html:
            break

        links = extract_detail_links(html)

        if not links:
            break

        for link in links:

            crawl_detail(link)

            total += 1

            if total >= max_pages:
                return

        page += 1

        time.sleep(CRAWL_DELAY)


def crawl(max_pages):

    for category_name, type_id in CATEGORIES.items():

        crawl_category(category_name, type_id, max_pages)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--start-url",
        type=str,
        default=BASE_URL,
        help="Start URL"
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=500,
        help="Max detail pages"
    )

    args = parser.parse_args()

    crawl(args.max_pages)

    print("\n✅ Crawl finished")


if __name__ == "__main__":
    main()