## 3. CẤU TRÚC DATASET (corpus.json)

### 3.1 Nguồn dữ liệu – các category ưu tiên crawl từ portal.huflit.edu.vn

- Tuyển sinh, Học phí, Lịch thi, Lịch học, Đăng ký môn học
- Thông báo chung, Kế hoạch đào tạo, Lịch nghỉ
- Tốt nghiệp, Học bổng, Chứng chỉ ngoại ngữ
- Công tác sinh viên, Dịch vụ hành chính

### 3.2 Schema một document trong corpus.json

```json
{
  "id": "huflit_0001",
  "title": "Thông báo tuyển sinh đại học chính quy năm 2024",
  "content": "Trường Đại học Ngoại ngữ - Tin học TP.HCM thông báo...",
  "url": "https://portal.huflit.edu.vn/tuyen-sinh/dai-hoc-2024",
  "category": "Tuyển sinh",
  "date": "2024-03-15",
  "content": "Trường Đại học Ngoại ngữ - Tin học TP.HCM thông báo...",
  "keywords": ["tuyển sinh", "chỉ tiêu", "xét tuyển", "học phí"],
  "entities": [
    { "type": "YEAR", "value": "2024" },
    { "type": "MONEY", "value": "12 triệu" },
    { "type": "MAJOR", "value": "Công nghệ thông tin" }
  ],
  "tokens": ["trường", "đại_học", "ngoại_ngữ", "tin_học", "thông_báo"],
}
```

**Lưu ý:**
- Trường `content` là plain text đã strip HTML, dùng cho indexing và snippet.
- Trường `tokens` là list sau khi tokenize + remove stopwords, dùng trực tiếp khi build index, không cần tokenize lại.
- Trường `entities` được tách lúc cleaning, lưu sẵn để tránh tách lại mỗi lần query.
- `id` format: `huflit_XXXX` với XXXX là số thứ tự 4 chữ số, padding zero.
- `category`: nếu không xác định được → mặc định `"Thông báo chung"`. Có thể suy ra từ URL pattern hoặc title prefix (VD: `[Điểm rèn luyện]` → "Công tác sinh viên").
- `date`: format `YYYY-MM-DD`. Nếu không parse được ngày → dùng `null`. Document không có date không bị loại khỏi kết quả, chỉ không được boost "mới nhất".
- Tokens **không lưu** trong corpus.json — được tính on-the-fly khi build index bởi `build_index.py`.


### 3.4 Danh sách category được giới hạn trong phạm vi đề tài

| category | URL pattern | Ví dụ trang |
|----------|-------------|-------------|
| Thông báo chung | /thong-bao/* | Nghỉ lễ, sự kiện chung |
| Tuyển sinh | /tuyen-sinh/* | Chỉ tiêu, phương thức, ngành |
| Học phí | /tai-chinh/*, /hoc-phi/* | Mức phí, hạn nộp |
| Đăng ký môn | /dang-ky-mon/* | Thời gian, hướng dẫn đăng ký |
| Học bổng | /hoc-bong/* | Điều kiện, mức học bổng |
| Tốt nghiệp | /tot-nghiep/* | Điều kiện, lịch xét, lễ trao bằng |
| Chứng chỉ | /chung-chi/* | Ngoại ngữ, tin học |

---
