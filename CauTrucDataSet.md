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
  "url": "https://portal.huflit.edu.vn/tuyen-sinh/dai-hoc-2024",
  "category": "Tuyển sinh",
  "date": "2024-03-15",
  "content": "Trường Đại học Ngoại ngữ - Tin học TP.HCM thông báo...",
  "tokens": ["trường", "đại_học", "ngoại_ngữ", "tin_học", "thông_báo"],
}
```

**Lưu ý:**
- Trường `content` là plain text đã strip HTML, dùng cho indexing và snippet.
- Trường `tokens` là list sau khi tokenize + remove stopwords, dùng trực tiếp khi build index, không cần tokenize lại.
- `id` format: `huflit_XXXX` với XXXX là số thứ tự 4 chữ số, padding zero.

### 3.3 Các loại entity được tách

| type | Mô tả | Ví dụ |
|------|-------|-------|
| DATE | Ngày tháng cụ thể | 15/3/2024, ngày 6/1/2025 |
| MONEY | Số tiền | 16.500.000 VNĐ, 12 triệu |
| SEMESTER | Học kỳ | học kỳ I, HK2 2024-2025 |
| GRADE | GPA hoặc điểm | GPA 3.6, điểm 2.0 |
| CERTIFICATE | Chứng chỉ | B1, IELTS 6.0, TOEFL 80 |
| MAJOR | Ngành học | Công nghệ thông tin, Ngôn ngữ Anh |
| CREDIT | Số tín chỉ | 120 tín chỉ, 12 tín chỉ |
| ACADEMIC_YEAR | Năm học | 2024-2025 |
| PERCENTAGE | Phần trăm | 100% học phí, 50% chi phí |

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
