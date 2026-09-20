# MSB SmartForm AI — Tóm tắt cho Ban Lãnh Đạo

> **Đọc trong 2 phút** · Gửi: Phó Tổng Giám Đốc Ngân hàng Bán lẻ & Doanh nghiệp · MSB AI Hackathon 2026

---

## Sản phẩm là gì?

**MSB SmartForm AI** là trợ lý AI lập hồ sơ & biểu mẫu khách hàng. Khách hàng chỉ cần **mô tả nhu cầu bằng 1 câu tự nhiên** — Agent tự chọn đúng mẫu MSB, giải thích từng trường kèm ví dụ, thu thập dữ liệu thiếu, điền form, chạy 9 bước kiểm tra, sinh checklist, xuất PDF, ký số và gửi qua Zalo Bot.

**One request. The right form. Ready to sign.**

## Vấn đề đang giải

Khách hàng MSB phải tự tìm trong hàng chục mẫu biểu, hay nộp sai/thiếu → hồ sơ bị trả lại nhiều vòng. Khách FDI cần form song ngữ VI–EN không có ở đâu. RM tốn 45 phút/lượt hướng dẫn thủ công. Tỷ lệ hồ sơ trả lại ~30%.

## Giá trị mang lại

| | |
|---|---|
| **Quy mô tiếp cận** | 150K KH doanh nghiệp + 3K FDI + 5 triệu KH cá nhân = **310K lượt cần form/năm** |
| **AEV (ước tính)** | **28–43 tỷ VND/năm** — giảm 35 phút RM/lượt + giảm hồ sơ trả lại từ 30% → 3% |
| **Khác biệt** | Knowledge Base MSB thật (không hallucinate) · Guided flow 8 bước · 9 quality checks · song ngữ VI–EN cho FDI · end-to-end chat→PDF→ký số→Zalo |
| **An toàn** | Không lưu PIN/OTP/private key · không phê duyệt (quyền thuộc MSB) · dữ liệu demo |

## Độ khả thi

Đã **deploy lên GreenNode AgentBase** (1 container, port 8080). Tech: LangGraph guided FSM + RAG + 9 QC checks + Next.js. Chạy được cả khi LLM down (rule-based fallback). Demo end-to-end với 6 persona (CTCP, TNHH, DNTN, FDI, cá nhân).

## Đề xuất pilot

**3 tháng · 30 mẫu tần suất cao nhất · Khối Doanh nghiệp (HN + HCM) · 1 container · 1 FTE.** Đo baseline → so sánh thời gian xử lý, tỷ lệ trả lại, NPS → quyết định scale bằng số. Mở rộng mẫu mới qua Form Registry admin — không cần deploy lại.

---
*Track: AI for Customers · Repo: github.com/…/Team05-HackathonAI · Pitch deck: docs/MSB_SmartForm_AI_Hackathon_2026_7min_Demo.pptx*
