""" 
Nhận raw HTML, trích xuất các trường: title (lấy từ thẻ h1 hoặc title), url, date (tìm trong meta hoặc nội dung), content (loại bỏ nav/header/footer/script, chỉ giữ main content), category (suy ra từ URL path hoặc breadcrumb). Output là list dict Python.
"""

import argparse
import json
from pathlib import Path
import sys
from bs4 import BeautifulSoup

# fix import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from crawler.config import RAW_DATA_DIR


def parse_html(html, url):

    soup = BeautifulSoup(html, "lxml")

    # title
    title_tag = soup.find("a", class_="title_topicdisplay")

    title = title_tag.get_text(strip=True) if title_tag else ""

    # content
    content_div = soup.find("div", style="overflow:auto")

    paragraphs = content_div.find_all("p") if content_div else []

    texts = []

    for p in paragraphs:

        text = p.get_text(" ", strip=True)

        if len(text) > 20:
            texts.append(text)

    content = " ".join(texts)

    return {
        "title": title,
        "content": content,
        "url": url
    }


def parse_directory(input_dir):

    results = []

    html_files = list(Path(input_dir).rglob("*.html"))

    print(f"📄 Found {len(html_files)} HTML files")

    for file in html_files:

        try:

            html = file.read_text(encoding="utf-8")

            news_id = file.stem

            url = f"https://portal.huflit.edu.vn/News/Detail/{news_id}"

            data = parse_html(html, url)

            results.append(data)

        except Exception as e:

            print(f"❌ Parse error: {file} -> {e}")

    return results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", default=str(RAW_DATA_DIR))
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    results = parse_directory(args.input)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:

        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ Parsed {len(results)} documents")
    print(f"📁 Saved → {args.output}")


if __name__ == "__main__":
    main()