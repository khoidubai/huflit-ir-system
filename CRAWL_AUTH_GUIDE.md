#Crawl với Authentication

## Vấn đề

Portal HUFLIT yêu cầu đăng nhập qua **Office 365 SSO** để xem nội dung đầy đủ. Crawler cũ (`spider.py`) chỉ dùng `requests` không có authentication

## Giải pháp

Sử dụng **Playwright** để:
- Tự động handle OAuth2 flow với Microsoft
- Lưu session state (cookies) để reuse
- Crawl như một user đã đăng nhập

---

## Cài đặt

### 1. Install Playwright

```bash
pip install playwright
playwright install chromium
```

### 2. Verify installation

```bash
playwright --version
```

---

## Sử dụng

### Bước 1: Login lần đầu

```bash
python crawler/auth_spider.py --login
```

**Quá trình:**
1. Browser sẽ mở tự động
2. Trang portal.huflit.edu.vn hiển thị
3. Click nút **"Office 365 for Student"**
4. Đăng nhập với tài khoản `@student.huflit.edu.vn`
5. Sau khi login xong, quay lại terminal nhấn **ENTER**
6. Session được lưu vào `data/session_state.json`
7. Sau khi đăng nhập scripts sẽ tự gọi crawl (lệnh phía dưới, k cần chạy lại, có thể quan sát trực tiếp quá trình crawl trong browser)
"python crawler/auth_spider.py --max-pages 500"
```

**Output:**
- Raw HTML lưu trong `data/raw/YYYY-MM-DD/*.html`
- Session tự động refresh và lưu lại

### Bước parse HTML thành JSON + clean bám sát theo STEP_BY_STEP.md

---

## Notes

- Session thường hết hạn sau **24 giờ** → cần login lại
- Mỗi lần crawl sẽ tự động refresh session
- Nếu crawl bị gián đoạn, chạy lại lệnh → tự động skip các file đã tải
- Playwright chạy Chromium, cần ~200MB disk space
