python crawler/spider.py --start-url https://portal.huflit.edu.vn 
--max-pages 500

python crawler/parser.py --output data/processed/corpus_raw.json

python crawler/cleaner.py --input data/processed/corpus_raw.json --output data/processed/corpus.json

---

python test_search.py "học phí học kỳ 2"