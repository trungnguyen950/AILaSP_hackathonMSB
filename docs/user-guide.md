# Hướng dẫn sử dụng MSB SmartForm AI

> **One request. The right form. Ready to sign.**
>
> Trợ lý AI lập hồ sơ & biểu mẫu khách hàng MSB — hỗ trợ cả khách hàng trong nước và doanh nghiệp FDI (song ngữ Việt – Anh).

---

## Truy cập hệ thống

Mở trình duyệt tại địa chỉ:

```
https://endpoint-f1ef0f3c-da52-4977-8b6e-e096c3af9588.agentbase-runtime.aiplatform.vngcloud.vn
```

Thanh điều hướng trên cùng có 3 trang:

| Nút | Trang | Chức năng |
|---|---|---|
| 💬 Chat | `/` | Chat với AI Agent để chọn mẫu, điền hồ sơ |
| 📋 Mẫu Biểu Mẫu | `/forms/` | Thư viện 9 biểu mẫu MSB |
| ✍️ Ký Số | `/sign/` | Mô phỏng ký chữ ký số lên file |

---

## Trang 1: 💬 Chat (Trang chính)

### Mục đích

Khách hàng mô tả nhu cầu bằng ngôn ngữ tự nhiên → AI Agent tự động chọn đúng mẫu MSB, giải thích từng trường, đưa ví dụ mẫu, rồi thu thập dữ liệu.

### Các nhóm khách hàng demo

Thanh persona có 6 thẻ — **nhấn vào bất kỳ thẻ nào để bắt đầu demo**:

| Thẻ | Loại khách | Ngôn ngữ | Mô tả |
|---|---|---|---|
| **CTCP X** | Công ty Cổ phần | Tiếng Việt | Thêm kế toán eBank (Maker + Approver) |
| **TNHH MTV Y** | TNHH 1 thành viên | Tiếng Việt | Thay đổi người đại diện pháp luật |
| **TNHH 2TV Z** | TNHH ≥2 thành viên | Tiếng Việt | Thuế điện tử + chữ ký số |
| **DNTN A** | Doanh nghiệp tư nhân | Tiếng Việt | Ủy quyền kế toán eBank |
| **FDI Alpha 🌐** | Doanh nghiệp FDI | Tiếng Anh (song ngữ) | Bilingual VI/EN · eBank + Maker/Approver |
| **Cá nhân A** | Khách hàng cá nhân | Tiếng Việt | Đổi SĐT, email & eBank |

> Mỗi thẻ persona sử dụng một **session độc lập** — chuyển sang persona khác sẽ tạo session mới, không bị dính dữ liệu cũ.

### Luồng chat từng bước

#### Bước 1: Chọn persona hoặc tự mô tả nhu cầu

**Cách 1 — Nhấn thẻ persona:** Agent tự động gửi prompt demo.

**Cách 2 — Tự gõ:** Ví dụ:
```
Công ty CP X muốn thêm kế toán vào eBank, kế toán lập lệnh, giám đốc duyệt
```

#### Bước 2: Agent giải thích form (FORM EXPLAINED)

Agent phản hồi với:
- Lời chào + xác nhận loại khách hàng
- **Mẫu biểu mẫu phù hợp** (mã + tên + mục đích)
- **Danh sách từng trường cần điền** kèm hướng dẫn:
  - Tên trường + dấu `*` (bắt buộc) hoặc `(tự chọn)`
  - Hướng dẫn 1 dòng: lấy ở đâu, định dạng gì, ví dụ cụ thể

Ví dụ:
```
📝 Các trường cần điền:
  1. Tên doanh nghiệp *
  2. Mã số thuế * — 10 chữ số, ví dụ: 0101234567 — xem Giấy chứng nhận ĐKDN
  3. Số tài khoản MSB * — 9–12 chữ số, ví dụ: 123456789999
  4. Vai trò * — Maker (lập lệnh) / Checker (kiểm soát) / Approver (duyệt)
  5. Số điện thoại * — Số điện thoại VN, ví dụ: 0901234567
  6. Email * — Email hợp lệ, ví dụ: name@company.com
```

#### Bước 3: Agent đưa mẫu giả lập

Agent tạo **mẫu giả lập (DEMO)** với dữ liệu demo điền sẵn, kèm gợi ý:
```
💡 Quý khách có thể nhập theo dạng:
  giátrị1 | giátrị2 | giátrị3  (phân tách bằng dấu |)

Khi sẵn sàng, vui lòng cung cấp thông tin hoặc nhập "sẵn sàng" để bắt đầu.
```

#### Bước 4: Khách hàng nói "sẵn sàng"

Gõ `sẵn sàng` (hoặc `ready`, `ok`) → Agent chuyển sang thu thập dữ liệu, **chỉ hỏi các trường bắt buộc còn thiếu**.

#### Bước 5: Khách hàng cung cấp dữ liệu

Có **3 cách nhập**:

**Cách 1 — Pipe-separated (nhanh nhất):**
```
Nguyễn Văn B | 001098765432 | Kế toán | Maker | OTP | 0901234567 | b@congtyx.vn
```

**Cách 2 — Label: value (rõ ràng nhất):**
```
Họ tên người dùng mới: Nguyễn Văn B
CCCD/Hộ chiếu: 001098765432
Chức danh: Kế toán
Vai trò: Maker
Phương thức xác thực: OTP
Số điện thoại: 0901234567
Email: b@congtyx.vn
```

**Cách 3 — Chat tự nhiên:**
```
Nguyễn Văn B, CCCD 001098765432, kế toán, vai trò Maker, 
xác thực OTP, SĐT 0901234567, email b@congtyx.vn
```

Agent tự nhận diện và điền vào form.

#### Bước 6: Kết quả (READY / NEED MSB REVIEW)

Khi đủ dữ liệu, Agent trả về:
- **STATUS: READY** — hồ sơ hoàn thiện
- **STATUS: NEED MSB REVIEW** — cần chuyên viên MSB xác nhận
- Panel bên phải hiển thị: mẫu đã chọn, hồ sơ đã điền, checklist

#### Bước 7: SOẠN HỒ SƠ

Nhấn nút **SOẠN HỒ SƠ** (panel bên phải) → Agent đóng gói:
- Checklist trước khi nộp MSB
- Bản mềm (.txt) — nhấn **⬇ Tải Text**
- PDF vintage — nhấn **⬇ Tải PDF**

#### Nút "↻ Xoá thông tin cũ, thực hiện lại"

Nhấn khi muốn:
- Thử persona khác
- Làm lại từ đầu
- Xoá toàn bộ dữ liệu đã nhập

→ Agent reset session, UI quay về welcome message.

---

## Trang 2: 📋 Mẫu Biểu Mẫu (`/forms/`)

### Mục đích

Thư viện **9 biểu mẫu MSB** — duyệt, tìm kiếm, tải xuống, xem trước, hoặc yêu cầu AI điền giúp.

### Giao diện

- **Search bar**: tìm theo tên, mã, mô tả
- **Category dropdown**: lọc theo nhóm (eBank, Tài khoản, Chữ ký số, Thuế điện tử)
- **Grid 3 cột** (desktop) / 2 cột (tablet) / 1 cột (mobile)

### Mỗi thẻ biểu mẫu có 3 nút

| Nút | Chức năng |
|---|---|
| **⬇ Download** | Tải file template `.txt` (chứa tất cả trường + người ký + hồ sơ kèm) |
| **👁 Xem Trước** | Mở modal hiển thị chi tiết: bảng trường, người ký, hồ sơ kèm theo |
| **🤖 AI Fill** | Chuyển sang trang Chat với form đã chọn → Agent giải thích + hướng dẫn điền |

### Danh sách 9 biểu mẫu

| Mã | Tên | Nhóm | Đối tượng |
|---|---|---|---|
| MSB-EBANK-01 | Đăng ký bổ sung người sử dụng eBank | eBank | KHTC |
| MSB-EBANK-01-FDI | Bổ sung người dùng eBank — FDI (Song ngữ) | eBank | FDI |
| MSB-IB-02 | Đăng ký dịch vụ Internet Banking (cá nhân) | eBank | KHCN |
| MSB-ETAX-03 | Đăng ký tài khoản nộp thuế điện tử | Thuế điện tử | KHTC |
| MSB-DS-04 | Đăng ký/thay đổi chữ ký số | Chữ ký số | KHTC |
| MSB-AC-05 | Thay đổi thông tin DN & người đại diện | Tài khoản | KHTC |
| MSB-EBANK-06 | Thay đổi hạn mức & phê duyệt eBank | eBank | KHTC |
| MSB-EBANK-07 | Khóa/mở khóa dịch vụ eBank | eBank | KHTC |
| MSB-AC-08 | Thay đổi thông tin liên hệ (ĐT/email/OTP) | Tài khoản | KHCN/KHTC |

### Luồng AI Fill

1. Nhấn **🤖 AI Fill** trên card → chuyển sang trang Chat
2. Agent tự động gửi: "Tôi muốn điền mẫu MSB-XX-XX..."
3. Agent giải thích từng trường + đưa mẫu giả lập
4. Gõ `sẵn sàng` → Agent hỏi **tất cả trường bắt buộc** (không pre-fill demo data)
5. Cung cấp dữ liệu → READY → SOẠN HỒ SƠ

---

## Trang 3: ✍️ Ký Số (`/sign/`)

### Mục đích

Mô phỏng luồng ký chữ ký số — vẽ chữ ký → chọn chứng thư số → ký file/PDF → tải file đã ký.

### Hai chế độ ký

#### Chế độ 1: Upload file rồi ký

**Bước 1: Chọn biểu mẫu + chứng thư số**

- Dropdown **biểu mẫu**: chọn 1 trong 9 mẫu MSB
- Dropdown **chứng thư số** (Mock USB Token): 3 lựa chọn
  - `MOCK-CERT-001` — Viettel-CA (Nguyễn Văn X)
  - `MOCK-CERT-002` — VNPT-CA (Nguyễn Văn Y)
  - `MOCK-CERT-003` — FPT-CA (Nguyễn Văn A)

**Bước 2: Upload file biểu mẫu**

- Kéo thả file vào khung **hoặc** click để chọn file
- Hỗ trợ: `.txt` và `.pdf` (tối đa 5MB)
- Hiển thị tên file + dung lượng

**Bước 3: AI kiểm tra file**

Nhấn **🤖 AI Kiểm Tra File** → Agent kiểm tra:
- Định dạng hợp lệ
- Mã mẫu có trong file
- Cấu trúc biểu mẫu
- Nội dung không trống

Kết quả hiển thị: **✅ File hợp lệ** (score/100) hoặc **❌ File không hợp lệ** + chi tiết từng check.

**Bước 4: Vẽ chữ ký**

Dùng chuột hoặc ngón tay (touch screen) vẽ vào khung canvas.
- Nút **🗑 Xóa** để vẽ lại

**Bước 5: Ký & Xác Nhận**

Nhấn **✍️ Ký File Đã Upload** → Agent:
- Chèn chữ ký vào file (.txt: append / .pdf: merge signature page)
- Tạo hash SHA256
- Gửi webhook thông báo cho AI Agent
- Trả về file đã ký

**Bước 6: Tải file đã ký**

Nhấn **⬇ Tải xuống file đã ký** → file về máy.

Kết quả hiển thị:
- File đã ký (tên file)
- SHA256 hash
- Webhook payload (JSON)
- Trạng thái: `Đã ký số thành công`

#### Chế độ 2: Ký PDF tạo sẵn từ form

Nếu **không upload file**:
1. Chọn biểu mẫu + chứng thư số
2. Vẽ chữ ký
3. Nhấn **✍️ Ký PDF Tạo Sẵn (từ form)**
4. Agent tạo PDF 2 trang (trang 1: dữ liệu form, trang 2: chữ ký)
5. Tải xuống PDF đã ký

---

## Luồng end-to-end đầy đủ (Demo pitch)

### Kịch bản 1: Khách hàng FDI (song ngữ)

```
1. Mở trang web → nhấn "FDI Alpha 🌐"
2. Agent giải thích form MSB-EBANK-01-FDI bằng tiếng Anh
3. Gõ: ready
4. Agent hỏi 7 trường thiếu (tiếng Anh)
5. Gõ: Nguyen Thi Lan | 001098765432 | Ke toan | Maker | OTP | 0901234567 | lan@alphavietnam.vn
6. → READY (15 fields filled, bilingual output)
7. Nhấn SOẠN HỒ SƠ → checklist + bản mềm + PDF
```

### Kịch bản 2: Khách hàng trong nước

```
1. Nhấn "CTCP X"
2. Agent giải thích form MSB-EBANK-01 bằng tiếng Việt có dấu
3. Gõ: sẵn sàng
4. Agent hỏi 7 trường thiếu (tiếng Việt)
5. Gõ: Nguyễn Văn B | 001098765432 | Kế toán | Maker | OTP | 0901234567 | b@congtyx.vn
6. → READY
7. Nhấn SOẜN HỒ SƠ → tải Text + PDF
```

### Kịch bản 3: Upload file + ký số

```
1. Vào trang ✍️ Ký Số
2. Chọn form MSB-DS-04 + chứng thư Viettel-CA
3. Upload file .txt chứa nội dung form
4. Nhấn 🤖 AI Kiểm Tra File → ✅ hợp lệ
5. Vẽ chữ ký
6. Nhấn ✍️ Ký File Đã Upload
7. Tải xuống file đã ký
```

---

## Câu hỏi thường gặp

**Q: Tôi muốn thử persona khác nhưng bị dính dữ liệu cũ?**
A: Mỗi persona dùng session riêng — nhấn persona khác sẽ tự reset. Hoặc nhấn nút "↻ Xoá thông tin cũ, thực hiện lại".

**Q: Agent trả lời tiếng Việt không dấu?**
A: Không. Agent luôn trả lời tiếng Việt có dấu đầy đủ. Nếu khách hàng FDI nhập tiếng Anh, Agent tự chuyển sang tiếng Anh.

**Q: Tôi có thể nhập dữ liệu theo định dạng nào?**
A: 3 cách: (1) `giátrị1 | giátrị2 | giátrị3`, (2) `Nhãn: giá trị` mỗi dòng, (3) chat tự nhiên.

**Q: AI Fill từ trang /forms có pre-fill dữ liệu demo không?**
A: Không. AI Fill yêu cầu khách hàng điền **tất cả trường bắt buộc** từ đầu.

**Q: File upload tối đa bao nhiêu?**
A: 5MB. Định dạng: `.txt` hoặc `.pdf`.

**Q: Dữ liệu khách hàng có thật không?**
A: Không. 100% dữ liệu giả lập. Agent chỉ chuẩn bị hồ sơ — không phê duyệt. Không lưu PIN/OTP/private key.

---

> **Lưu ý:** Dữ liệu khách hàng 100% giả lập. Agent chỉ chuẩn bị hồ sơ — quyền phê duyệt thuộc MSB.
