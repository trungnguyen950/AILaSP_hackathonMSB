# Trang Chat — Luồng từng bước

## Bước 1: Chọn persona hoặc tự mô tả nhu cầu

**Cách 1 — Nhấn thẻ persona:** Agent tự động gửi prompt demo.

**Cách 2 — Tự gõ:** Ví dụ:
```
Công ty CP X muốn thêm kế toán vào eBank, kế toán lập lệnh, giám đốc duyệt
```

## Bước 2: Agent giải thích form (FORM EXPLAINED)

Agent phản hồi với:
- Lời chào + xác nhận loại khách hàng
- **Mẫu biểu mẫu phù hợp** (mã + tên + mục đích)
- **Danh sách từng trường cần điền** kèm hướng dẫn

## Bước 3: Agent đưa mẫu giả lập

Agent tạo **mẫu giả lập (DEMO)** với dữ liệu demo điền sẵn, kèm gợi ý.

## Bước 4: Khách hàng nói "sẵn sàng"

Gõ `sẵn sàng` (hoặc `ready`, `ok`) → Agent chuyển sang thu thập dữ liệu.

## Bước 5: Khách hàng cung cấp dữ liệu

Có **3 cách nhập**: pipe-separated, label: value, hoặc chat tự nhiên.

## Bước 6: Kết quả (READY / NEED MSB REVIEW)

Khi đủ dữ liệu, Agent trả về STATUS + panel bên phải hiển thị hồ sơ đã điền + checklist.

## Bước 7: SOẠN HỒ SƠ

Nhấn nút **SOẠN HỒ SƠ** → Agent đóng gói checklist + bản mềm (.txt) + PDF vintage.
