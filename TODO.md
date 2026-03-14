# TODO List

- [ ] Crawl Data
- [ ] Xây dựng bộ chỉ mục (Build Index)
- [ ] Kiểm tra bằng Terminal (Test Search)
- [ ] Khởi chạy Backend API
- [ ] Khởi chạy Frontend (Giao diện Web)
- [ ] Thông tin Model AI (Local - Offline 100%)
- [ ] Lưu ý:
- [ ] Nếu dữ liệu (`corpus.json`) thay đổi, bạn **bắt buộc** phải chạy lại Bước 3 (Build cả Sparse + Dense Index).
- [ ] Trên Windows, nếu gặp lỗi model không load, chạy `python repair_hf_cache.py` để sửa HuggingFace cache trước.
- [ ] Lần đầu chạy `--use_llm`, hệ thống cần ~20-30 giây để nạp file GGUF 4.3GB vào RAM.

*Tiếp theo sẽ triển khai thêm gọi api model LLM online thay vì chạy model offline (trl rất chậm)