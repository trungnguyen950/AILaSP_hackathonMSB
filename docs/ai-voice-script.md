# 🎙️ AI Voice Script — MSB SmartForm AI Demo (3 phút)

> **Mục đích:** Feed vào AI TTS (ElevenLabs / Azure TTS / Google TTS) để tạo voiceover
> **Ngôn ngữ:** Tiếng Việt (vi-VN) · **Giọng:** Nam, tự tin, chuyên nghiệp, tốc độ vừa
> **Thời lượng:** 3 phút (180 giây) · **Nguồn:** tách từ `demo-video-script.md`

---

## 📝 CÁCH DÙNG

1. Copy từng block text theo thứ tự timeline
2. Dòng `[SILENCE Xs]` = khoảng lặng X giây (không generate audio)
3. Dòng `[PAUSE]` = ngắt 0.5 giây trong cùng 1 câu
4. Text in **bold** = nhấn mạnh (TTS: tăng pitch/prosody)
5. Ghép các block lại theo timestamp → ghép audio → sync với video

---

## 🎙️ VOICEOVER SCRIPT

### ═══ [0:00] PHẦN 0: INTRO ═══

```
[SILENCE 3s]

MSB SmartForm AI [PAUSE] từ một câu nói đến bộ hồ sơ sẵn sàng ký. [PAUSE] Demo end-to-end trong 3 phút.

[SILENCE 4s]
```

---

### ═══ [0:12] PHẦN 1: CHAT FDI BILINGUAL ═══

```
Bắt đầu với khách hàng FDI [PAUSE] doanh nghiệp có vốn đầu tư nước ngoài, cần biểu mẫu song ngữ Việt–Anh.

[WAIT 5s — Agent respond]

Agent tự phát hiện tiếng Anh, chọn form MSB-EBANK-01-FDI, và giải thích từng trường kèm ví dụ [PAUSE] bằng tiếng Anh.

[WAIT 5s — scroll]

Khách chỉ cần gõ "ready" [PAUSE] Agent hỏi đúng 7 trường còn thiếu.

[WAIT 4s — paste data]

Khách cung cấp dữ liệu theo format pipe-separated. [PAUSE] Agent điền 15 trường, chạy 9 quality checks, và trả về STATUS READY [PAUSE] bilingual output.

[SILENCE 3s — để BGK đọc kết quả]

15 trường, song ngữ, 9 quality checks [PAUSE] tất cả trong 1 câu hỏi.
```

---

### ═══ [0:55] PHẦN 2: SOẠN HỒ SƠ ═══

```
Nhấn "SOẠN HỒ SƠ" [PAUSE] Agent sinh checklist hồ sơ kèm theo và xuất PDF vintage.

[WAIT 3s]

Checklist: biểu mẫu, CCCD, giấy ủy quyền [PAUSE] khách biết chính xác cần nộp gì.

[WAIT 3s]

Tải PDF [PAUSE] sẵn sàng in hoặc nộp trực tuyến.

[SILENCE 3s]
```

---

### ═══ [1:15] PHẦN 3: KÝ SỐ + ZALO ═══

```
Trang Ký Số [PAUSE] upload file, AI kiểm tra, ký số, và gửi Zalo cho khách.

[WAIT 2s]

Chọn form MSB-DS-04 và chứng thư Viettel-CA.

[WAIT 3s — upload]

Upload file biểu mẫu.

[WAIT 2s]

AI kiểm tra file [PAUSE] định dạng, mã mẫu, cấu trúc. [PAUSE] Kết quả: hợp lệ, 100 trên 100.

[WAIT 3s — draw signature]

Vẽ chữ ký trên canvas [PAUSE] chuột hoặc touch.

[WAIT 2s]

Ký file [PAUSE] Agent chèn chữ ký, tạo SHA256 hash, gửi webhook.

[WAIT 3s]

File đã ký. [PAUSE] Giờ gửi cho khách hàng qua Zalo Bot.

[WAIT 3s]

Khách nhận PDF đã ký + thông báo trên Zalo [PAUSE] end-to-end hoàn chỉnh.

[SILENCE 3s]
```

---

### ═══ [1:55] PHẦN 4: DASHBOARD BUSINESS KPI ═══

```
Dashboard Điều hành [PAUSE] business KPI realtime cho quản lý ngân hàng, cập nhật mỗi 3 giây.

[WAIT 3s]

Tổng hồ sơ đã xử lý, tỷ lệ nộp đúng lần đầu 86%, thời gian xử lý trung bình 12 phút [PAUSE] và AEV dự kiến: 28 tỷ đồng mỗi năm.

[WAIT 3s]

Trạng thái hồ sơ: READY, MISSING, NEED REVIEW [PAUSE] quản lý nhìn 1 cái là biết tình hình.

[WAIT 3s]

Phân khúc khách hàng: Doanh nghiệp, FDI song ngữ, Cá nhân.

[WAIT 3s]

Hiệu suất chuyên viên RM [PAUSE] top 5, ai xử lý bao nhiêu hồ sơ, tỷ lệ READY bao nhiêu.

[WAIT 3s]

Và FDI [PAUSE] segment chiến lược, 156 khách đã phục vụ, CSAT 4.6 trên 5.

[SILENCE 3s]
```

---

### ═══ [2:30] PHẦN 5: FORMS LIBRARY ═══

```
Thư viện 9 biểu mẫu [PAUSE] tìm kiếm, xem trước, và AI Fill từ trang này.

[WAIT 3s]

Mỗi form có 4 nút: tải Text, tải PDF, xem trước, và AI Fill [PAUSE] chuyển sang chat để điền từ đầu.

[SILENCE 3s]
```

---

### ═══ [2:42] PHẦN 6: OUTRO ═══

```
MSB SmartForm AI [PAUSE] end-to-end: chat, điền form, 9 quality checks, PDF, ký số, Zalo.

[WAIT 4s]

Song ngữ VI-EN cho FDI. [PAUSE] Không lưu bí mật. [PAUSE] Không phê duyệt [PAUSE] quyền thuộc MSB. [PAUSE] An toàn cho môi trường ngân hàng.

[WAIT 4s]

One request. [PAUSE] The right form. [PAUSE] Ready to sign.

[SILENCE 3s — fade out]
```

---

## 🔊 TTS SETTINGS (gợi ý)

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| Engine | ElevenLabs Multilingual v2 / Azure vi-VN | Hỗ trợ tiếng Việt tốt |
| Voice | Nam, trung niên, tự tin | "HoaiMy" (Azure) hoặc clone |
| Speed | 0.95× | Hơi chậm để BGK absorbe |
| Stability | 0.5 | Cân bằng, không quá biến |
| Pitch | +0 | Bình thường |

---

## 📋 FULL SCRIPT (concatenated — không có marker)

> Paste nguyên văn vào TTS nếu cần 1 lần generate liên tục:

```
MSB SmartForm AI. Từ một câu nói đến bộ hồ sơ sẵn sàng ký. Demo end-to-end trong 3 phút.

Bắt đầu với khách hàng FDI — doanh nghiệp có vốn đầu tư nước ngoài, cần biểu mẫu song ngữ Việt–Anh.

Agent tự phát hiện tiếng Anh, chọn form MSB-EBANK-01-FDI, và giải thích từng trường kèm ví dụ — bằng tiếng Anh.

Khách chỉ cần gõ "ready" — Agent hỏi đúng 7 trường còn thiếu.

Khách cung cấp dữ liệu theo format pipe-separated. Agent điền 15 trường, chạy 9 quality checks, và trả về STATUS READY — bilingual output.

15 trường, song ngữ, 9 quality checks — tất cả trong 1 câu hỏi.

Nhấn "SOẠN HỒ SƠ" — Agent sinh checklist hồ sơ kèm theo và xuất PDF vintage.

Checklist: biểu mẫu, CCCD, giấy ủy quyền — khách biết chính xác cần nộp gì.

Tải PDF — sẵn sàng in hoặc nộp trực tuyến.

Trang Ký Số — upload file, AI kiểm tra, ký số, và gửi Zalo cho khách.

Chọn form MSB-DS-04 và chứng thư Viettel-CA.

Upload file biểu mẫu.

AI kiểm tra file — định dạng, mã mẫu, cấu trúc. Kết quả: hợp lệ, 100 trên 100.

Vẽ chữ ký trên canvas — chuột hoặc touch.

Ký file — Agent chèn chữ ký, tạo SHA256 hash, gửi webhook.

File đã ký. Giờ gửi cho khách hàng qua Zalo Bot.

Khách nhận PDF đã ký + thông báo trên Zalo — end-to-end hoàn chỉnh.

Dashboard Điều hành — business KPI realtime cho quản lý ngân hàng, cập nhật mỗi 3 giây.

Tổng hồ sơ đã xử lý, tỷ lệ nộp đúng lần đầu 86%, thời gian xử lý trung bình 12 phút — và AEV dự kiến: 28 tỷ đồng mỗi năm.

Trạng thái hồ sơ: READY, MISSING, NEED REVIEW — quản lý nhìn 1 cái là biết tình hình.

Phân khúc khách hàng: Doanh nghiệp, FDI song ngữ, Cá nhân.

Hiệu suất chuyên viên RM — top 5, ai xử lý bao nhiêu hồ sơ, tỷ lệ READY bao nhiêu.

Và FDI — segment chiến lược, 156 khách đã phục vụ, CSAT 4.6 trên 5.

Thư viện 9 biểu mẫu — tìm kiếm, xem trước, và AI Fill từ trang này.

Mỗi form có 4 nút: tải Text, tải PDF, xem trước, và AI Fill — chuyển sang chat để điền từ đầu.

MSB SmartForm AI — end-to-end: chat, điền form, 9 quality checks, PDF, ký số, Zalo.

Song ngữ VI-EN cho FDI. Không lưu bí mật. Không phê duyệt — quyền thuộc MSB. An toàn cho môi trường ngân hàng.

One request. The right form. Ready to sign.
```
