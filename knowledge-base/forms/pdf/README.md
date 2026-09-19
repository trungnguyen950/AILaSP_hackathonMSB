# Folder PDF gốc (placeholder)

Thư mục này dành để đặt **file PDF/mẫu thật của MSB** sau này.

## Cách dùng
- Đặt file PDF gốc theo quy ước: `<MA_MAU>_v<PHIEN_BAN>.pdf` (vd `MSB-EBANK-01_v2.1.pdf`).
- Khi có PDF thật, Form Engine chuyển từ "render từ template JSON" sang "map field → vị trí trên PDF (AcroForm/layout)" — xem ADR-6 trong `docs/08-ADR.md`.
- Cập nhật cột `File nguồn` trong `knowledge-base/form-registry.md` trỏ tới file tương ứng.

> v0.1: folder rỗng. Form Engine dùng template JSON (mock) để render.
