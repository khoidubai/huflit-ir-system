"""
Script để sinh corpus_new.json từ corpus.json:
- Thêm trường id (huflit_XXXX)
- Trích xuất date từ title/content (format YYYY-MM-DD, null nếu không tìm được)
- Thêm trường category (để trống cho user fill sau)
"""
import json
import re
from datetime import datetime
from pathlib import Path

CORPUS_PATH = Path("data/processed/corpus.json")
OUTPUT_PATH = Path("data/processed/corpus_new.json")

def extract_date(title, content):
    """Extract the most relevant date from title+content."""
    date_pattern = r'(\d{1,2})/(\d{1,2})/(\d{4})'
    
    def parse_matches(text):
        matches = re.findall(date_pattern, text)
        dates = []
        for day, month, year in matches:
            try:
                d = datetime(int(year), int(month), int(day))
                if 2020 <= d.year <= 2027:
                    dates.append(d)
            except ValueError:
                continue
        return dates

    # Priority 1: dates in title (latest)
    title_dates = parse_matches(title)
    if title_dates:
        return max(title_dates).strftime('%Y-%m-%d')
    
    # Priority 2: latest date in content
    content_dates = parse_matches(content)
    if content_dates:
        return max(content_dates).strftime('%Y-%m-%d')
    
    return None

def main():
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    corpus_new = []
    date_count = 0

    for i, doc in enumerate(corpus):
        doc_id = doc.get('id', f"huflit_{i+1:04d}")
        date = extract_date(doc.get('title', ''), doc.get('content', ''))
        if date:
            date_count += 1

        corpus_new.append({
            "id": doc_id,
            "title": doc.get('title', ''),
            "content": doc.get('content', ''),
            "url": doc.get('url', ''),
            "category": "",
            "date": date
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(corpus_new, f, ensure_ascii=False, indent=2)

    print(f"Done! {len(corpus_new)} docs -> {OUTPUT_PATH}")
    print(f"  With date: {date_count}")
    print(f"  Null date: {len(corpus_new) - date_count}")
    print()
    for doc in corpus_new[:3]:
        print(f"  [{doc['id']}] date={doc['date']} | {doc['title'][:70]}")
    print("  ...")
    for doc in corpus_new[-3:]:
        print(f"  [{doc['id']}] date={doc['date']} | {doc['title'][:70]}")

if __name__ == "__main__":
    main()
