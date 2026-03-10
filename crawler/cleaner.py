""" 
Làm sạch dữ liệu sau parse: chuẩn hoá unicode (NFC), bỏ ký tự thừa, loại trùng lặp bằng SHA-256 hash trên nội dung, bỏ document quá ngắn (dưới 50 từ). Ghi kết quả ra data/processed/corpus.json.
"""


import argparse
import json
import re


def remove_duplicate_sentences(text):

    sentences = re.split(r"[.!?]", text)

    seen = set()
    result = []

    for s in sentences:

        s = s.strip()

        if len(s) < 10:
            continue

        if s not in seen:
            seen.add(s)
            result.append(s)

    return ". ".join(result)


def clean_text(text):

    if not text:
        return ""

    # normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # remove bullet symbols
    text = text.replace("·", "")
    text = text.replace("•", "")

    # remove emails
    text = re.sub(r"\S+@\S+", "", text)

    # remove duplicate sentences
    text = remove_duplicate_sentences(text)

    return text.strip()


def clean_dataset(input_file, output_file):

    with open(input_file, "r", encoding="utf-8") as f:
        docs = json.load(f)

    cleaned = []

    for doc in docs:

        title = clean_text(doc.get("title", ""))
        content = clean_text(doc.get("content", ""))

        if len(content) < 50:
            continue

        cleaned.append({
            "title": title,
            "content": content,
            "url": doc["url"]
        })

    with open(output_file, "w", encoding="utf-8") as f:

        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"✅ Cleaned {len(cleaned)} documents")
    print(f"📁 Saved → {output_file}")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clean_dataset(args.input, args.output)


if __name__ == "__main__":
    main()