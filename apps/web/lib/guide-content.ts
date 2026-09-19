export type Block =
  | { type: "h2"; text: string; anchor?: string }
  | { type: "h3"; text: string; anchor?: string }
  | { type: "p"; text: string }
  | { type: "code"; code: string }
  | { type: "callout"; variant: "info" | "warning" | "tip" | "danger"; title?: string; text: string }
  | { type: "steps"; items: { title: string; desc: string }[] }
  | { type: "table"; headers: string[]; rows: string[][] }
  | { type: "list"; items: string[]; ordered?: boolean }
  | { type: "faq"; items: { q: string; a: string }[] }
  | { type: "nextSteps"; items: { label: string; href: string }[] };

export type GuidePage = {
  slug: string;
  title: string;
  description: string;
  section: string;
  icon: string;
  blocks: Block[];
};

export type NavSection = {
  section: string;
  items: { slug: string; title: string; icon: string }[];
};

export const NAV: NavSection[] = [
  {
    section: "Giới thiệu",
    items: [{ slug: "introduction", title: "Truy cập hệ thống", icon: "📖" }],
  },
  {
    section: "Trang Chat",
    items: [
      { slug: "home/overview", title: "Tổng quan", icon: "💬" },
      { slug: "home/flow", title: "Luồng từng bước", icon: "🔄" },
    ],
  },
  {
    section: "Mẫu Biểu Mẫu",
    items: [
      { slug: "forms/overview", title: "Tổng quan & 9 biểu mẫu", icon: "📋" },
      { slug: "forms/ai-fill", title: "Luồng AI Fill", icon: "🤖" },
    ],
  },
  {
    section: "Ký Số",
    items: [
      { slug: "sign/upload", title: "Upload file rồi ký", icon: "📤" },
      { slug: "sign/generated", title: "Ký PDF tạo sẵn", icon: "✍️" },
    ],
  },
  {
    section: "Demo & FAQ",
    items: [
      { slug: "demo", title: "Luồng end-to-end", icon: "🎯" },
      { slug: "faq", title: "Câu hỏi thường gặp", icon: "❓" },
    ],
  },
];

export const PAGES: Record<string, GuidePage> = {
  introduction: {
    slug: "introduction",
    title: "Giới thiệu",
    description: "Truy cập hệ thống MSB SmartForm AI và 3 trang chính",
    section: "Giới thiệu",
    icon: "📖",
    blocks: [
      { type: "callout", variant: "info", title: "One request. The right form. Ready to sign.", text: "Trợ lý AI lập hồ sơ & biểu mẫu khách hàng MSB — hỗ trợ cả khách hàng trong nước và doanh nghiệp FDI (song ngữ Việt – Anh)." },
      { type: "h2", text: "Truy cập hệ thống", anchor: "access" },
      { type: "p", text: "Mở trình duyệt tại địa chỉ:" },
      { type: "code", code: "https://endpoint-f1ef0f3c-da52-4977-8b6e-e096c3af9588.agentbase-runtime.aiplatform.vngcloud.vn" },
      { type: "p", text: "Thanh điều hướng trên cùng có 3 trang:" },
      {
        type: "table",
        headers: ["Nút", "Trang", "Chức năng"],
        rows: [
          ["💬 Chat", "/", "Chat với AI Agent để chọn mẫu, điền hồ sơ"],
          ["📋 Mẫu Biểu Mẫu", "/forms/", "Thư viện 9 biểu mẫu MSB"],
          ["✍️ Ký Số", "/sign/", "Mô phỏng ký chữ ký số lên file"],
        ],
      },
      { type: "nextSteps", items: [{ label: "Trang Chat — Tổng quan", href: "/user-guide/home/overview" }] },
    ],
  },

  "home/overview": {
    slug: "home/overview",
    title: "Trang Chat — Tổng quan",
    description: "Mục đích, các nhóm khách hàng demo và persona",
    section: "Trang Chat",
    icon: "💬",
    blocks: [
      { type: "h2", text: "Mục đích", anchor: "purpose" },
      { type: "p", text: "Khách hàng mô tả nhu cầu bằng ngôn ngữ tự nhiên → AI Agent tự động chọn đúng mẫu MSB, giải thích từng trường, đưa ví dụ mẫu, rồi thu thập dữ liệu." },
      { type: "h2", text: "Các nhóm khách hàng demo", anchor: "personas" },
      { type: "p", text: "Thanh persona có 6 thẻ — nhấn vào bất kỳ thẻ nào để bắt đầu demo:" },
      {
        type: "table",
        headers: ["Thẻ", "Loại khách", "Ngôn ngữ", "Mô tả"],
        rows: [
          ["CTCP X", "Công ty Cổ phần", "Tiếng Việt", "Thêm kế toán eBank (Maker + Approver)"],
          ["TNHH MTV Y", "TNHH 1 thành viên", "Tiếng Việt", "Thay đổi người đại diện pháp luật"],
          ["TNHH 2TV Z", "TNHH ≥2 thành viên", "Tiếng Việt", "Thuế điện tử + chữ ký số"],
          ["DNTN A", "Doanh nghiệp tư nhân", "Tiếng Việt", "Ủy quyền kế toán eBank"],
          ["FDI Alpha 🌐", "Doanh nghiệp FDI", "Tiếng Anh (song ngữ)", "Bilingual VI/EN · eBank + Maker/Approver"],
          ["Cá nhân A", "Khách hàng cá nhân", "Tiếng Việt", "Đổi SĐT, email & eBank"],
        ],
      },
      { type: "callout", variant: "tip", text: "Mỗi thẻ persona sử dụng một session độc lập — chuyển sang persona khác sẽ tạo session mới, không bị dính dữ liệu cũ." },
      { type: "nextSteps", items: [{ label: "Luồng chat từng bước", href: "/user-guide/home/flow" }] },
    ],
  },

  "home/flow": {
    slug: "home/flow",
    title: "Trang Chat — Luồng từng bước",
    description: "7 bước từ chọn persona đến soạn hồ sơ",
    section: "Trang Chat",
    icon: "🔄",
    blocks: [
      {
        type: "steps",
        items: [
          { title: "Chọn persona hoặc tự mô tả nhu cầu", desc: "Cách 1: Nhấn thẻ persona → Agent tự gửi prompt demo. Cách 2: Tự gõ, ví dụ: \"Công ty CP X muốn thêm kế toán vào eBank, kế toán lập lệnh, giám đốc duyệt\"" },
          { title: "Agent giải thích form (FORM EXPLAINED)", desc: "Agent phản hồi với lời chào + xác nhận loại khách hàng, mẫu biểu mẫu phù hợp (mã + tên + mục đích), danh sách từng trường cần điền kèm hướng dẫn." },
          { title: "Agent đưa mẫu giả lập", desc: "Agent tạo mẫu giả lập (DEMO) với dữ liệu demo điền sẵn, kèm gợi ý nhập theo dạng pipe-separated." },
          { title: "Khách hàng nói \"sẵn sàng\"", desc: "Gõ sẵn sàng (hoặc ready, ok) → Agent chuyển sang thu thập dữ liệu, chỉ hỏi các trường bắt buộc còn thiếu." },
          { title: "Khách hàng cung cấp dữ liệu", desc: "3 cách nhập: (1) Pipe-separated — nhanh nhất, (2) Label: value — rõ ràng nhất, (3) Chat tự nhiên. Agent tự nhận diện và điền vào form." },
          { title: "Kết quả (READY / NEED MSB REVIEW)", desc: "Khi đủ dữ liệu, Agent trả về STATUS: READY (hồ sơ hoàn thiện) hoặc NEED MSB REVIEW (cần chuyên viên MSB xác nhận). Panel bên phải hiển thị mẫu đã chọn, hồ sơ đã điền, checklist." },
          { title: "SOẠN HỒ SƠ", desc: "Nhấn nút SOẠN HỒ SƠ → Agent đóng gói checklist trước khi nộp MSB, bản mềm (.txt) và PDF vintage." },
        ],
      },
      { type: "h2", text: "3 cách nhập dữ liệu", anchor: "input-methods" },
      { type: "h3", text: "Cách 1 — Pipe-separated (nhanh nhất)" },
      { type: "code", code: "Nguyễn Văn B | 001098765432 | Kế toán | Maker | OTP | 0901234567 | b@congtyx.vn" },
      { type: "h3", text: "Cách 2 — Label: value (rõ ràng nhất)" },
      { type: "code", code: "Họ tên người dùng mới: Nguyễn Văn B\nCCCD/Hộ chiếu: 001098765432\nChức danh: Kế toán\nVai trò: Maker\nPhương thức xác thực: OTP\nSố điện thoại: 0901234567\nEmail: b@congtyx.vn" },
      { type: "h3", text: "Cách 3 — Chat tự nhiên" },
      { type: "code", code: "Nguyễn Văn B, CCCD 001098765432, kế toán, vai trò Maker,\nxác thực OTP, SĐT 0901234567, email b@congtyx.vn" },
      { type: "callout", variant: "warning", title: "Nút \"↻ Xoá thông tin cũ\"", text: "Nhấn khi muốn thử persona khác, làm lại từ đầu, hoặc xoá toàn bộ dữ liệu đã nhập. Agent reset session, UI quay về welcome message." },
      { type: "nextSteps", items: [{ label: "Mẫu Biểu Mẫu — Tổng quan", href: "/user-guide/forms/overview" }] },
    ],
  },

  "forms/overview": {
    slug: "forms/overview",
    title: "Mẫu Biểu Mẫu — Tổng quan",
    description: "Thư viện 9 biểu mẫu MSB, giao diện và các nút",
    section: "Mẫu Biểu Mẫu",
    icon: "📋",
    blocks: [
      { type: "h2", text: "Mục đích", anchor: "purpose" },
      { type: "p", text: "Thư viện 9 biểu mẫu MSB — duyệt, tìm kiếm, tải xuống, xem trước, hoặc yêu cầu AI điền giúp." },
      { type: "h2", text: "Giao diện", anchor: "ui" },
      { type: "list", items: ["Search bar: tìm theo tên, mã, mô tả", "Category dropdown: lọc theo nhóm (eBank, Tài khoản, Chữ ký số, Thuế điện tử)", "Grid 3 cột (desktop) / 2 cột (tablet) / 1 cột (mobile)"] },
      { type: "h2", text: "Mỗi thẻ biểu mẫu có 3 nút", anchor: "buttons" },
      {
        type: "table",
        headers: ["Nút", "Chức năng"],
        rows: [
          ["⬇ Download", "Tải file template .txt (chứa tất cả trường + người ký + hồ sơ kèm)"],
          ["👁 Xem Trước", "Mở modal hiển thị chi tiết: bảng trường, người ký, hồ sơ kèm theo"],
          ["🤖 AI Fill", "Chuyển sang trang Chat với form đã chọn → Agent giải thích + hướng dẫn điền"],
        ],
      },
      { type: "h2", text: "Danh sách 9 biểu mẫu", anchor: "list" },
      {
        type: "table",
        headers: ["Mã", "Tên", "Nhóm", "Đối tượng"],
        rows: [
          ["MSB-EBANK-01", "Đăng ký bổ sung người sử dụng eBank", "eBank", "KHTC"],
          ["MSB-EBANK-01-FDI", "Bổ sung người dùng eBank — FDI (Song ngữ)", "eBank", "FDI"],
          ["MSB-IB-02", "Đăng ký dịch vụ Internet Banking (cá nhân)", "eBank", "KHCN"],
          ["MSB-ETAX-03", "Đăng ký tài khoản nộp thuế điện tử", "Thuế điện tử", "KHTC"],
          ["MSB-DS-04", "Đăng ký/thay đổi chữ ký số", "Chữ ký số", "KHTC"],
          ["MSB-AC-05", "Thay đổi thông tin DN & người đại diện", "Tài khoản", "KHTC"],
          ["MSB-EBANK-06", "Thay đổi hạn mức & phê duyệt eBank", "eBank", "KHTC"],
          ["MSB-EBANK-07", "Khóa/mở khóa dịch vụ eBank", "eBank", "KHTC"],
          ["MSB-AC-08", "Thay đổi thông tin liên hệ (ĐT/email/OTP)", "Tài khoản", "KHCN/KHTC"],
        ],
      },
      { type: "nextSteps", items: [{ label: "Luồng AI Fill", href: "/user-guide/forms/ai-fill" }] },
    ],
  },

  "forms/ai-fill": {
    slug: "forms/ai-fill",
    title: "Mẫu Biểu Mẫu — Luồng AI Fill",
    description: "Cách dùng AI Fill để điền form tự động",
    section: "Mẫu Biểu Mẫu",
    icon: "🤖",
    blocks: [
      {
        type: "steps",
        items: [
          { title: "Nhấn 🤖 AI Fill trên card", desc: "Chuyển sang trang Chat với form đã chọn" },
          { title: "Agent tự động gửi prompt", desc: "Agent gửi: \"Tôi muốn điền mẫu MSB-XX-XX...\" và giải thích từng trường + đưa mẫu giả lập" },
          { title: "Gõ \"sẵn sàng\"", desc: "Agent hỏi tất cả trường bắt buộc (không pre-fill demo data)" },
          { title: "Cung cấp dữ liệu", desc: "Nhập dữ liệu theo 1 trong 3 cách → READY" },
          { title: "SOẠN HỒ SƠ", desc: "Nhấn nút SOẠN HỒ SƠ → tải Text + PDF" },
        ],
      },
      { type: "callout", variant: "warning", text: "AI Fill từ trang /forms không pre-fill dữ liệu demo. Khách hàng điền tất cả trường bắt buộc từ đầu." },
      { type: "nextSteps", items: [{ label: "Ký Số — Upload file", href: "/user-guide/sign/upload" }] },
    ],
  },

  "sign/upload": {
    slug: "sign/upload",
    title: "Ký Số — Upload file rồi ký",
    description: "6 bước: chọn mẫu → upload → AI check → vẽ chữ ký → ký → tải",
    section: "Ký Số",
    icon: "📤",
    blocks: [
      {
        type: "steps",
        items: [
          { title: "Chọn biểu mẫu + chứng thư số", desc: "Dropdown biểu mẫu: chọn 1 trong 9 mẫu MSB. Dropdown chứng thư số (Mock USB Token): MOCK-CERT-001 (Viettel-CA), MOCK-CERT-002 (VNPT-CA), MOCK-CERT-003 (FPT-CA)." },
          { title: "Upload file biểu mẫu", desc: "Kéo thả file vào khung hoặc click để chọn file. Hỗ trợ: .txt và .pdf (tối đa 5MB). Hiển thị tên file + dung lượng." },
          { title: "AI kiểm tra file", desc: "Nhấn 🤖 AI Kiểm Tra File → Agent kiểm tra: định dạng hợp lệ, mã mẫu có trong file, cấu trúc biểu mẫu, nội dung không trống. Kết quả: ✅ File hợp lệ (score/100) hoặc ❌ File không hợp lệ + chi tiết." },
          { title: "Vẽ chữ ký", desc: "Dùng chuột hoặc ngón tay (touch screen) vẽ vào khung canvas. Nút 🗑 Xóa để vẽ lại." },
          { title: "Ký & Xác Nhận", desc: "Nhấn ✍️ Ký File Đã Upload → Agent chèn chữ ký vào file (.txt: append / .pdf: merge signature page), tạo hash SHA256, gửi webhook thông báo cho AI Agent, trả về file đã ký." },
          { title: "Tải file đã ký", desc: "Nhấn ⬇ Tải xuống file đã ký → file về máy. Kết quả hiển thị: file đã ký (tên file), SHA256 hash, webhook payload (JSON), trạng thái: Đã ký số thành công." },
        ],
      },
      { type: "callout", variant: "info", title: "Gửi Zalo Bot", text: "Sau khi ký thành công, bấm 💬 Gửi Zalo Bot để gửi thông báo + PDF đã ký cho khách hàng qua Zalo. Nhập Zalo chat_id vào ô tương ứng (nhắn bot trước để lấy chat_id)." },
      { type: "nextSteps", items: [{ label: "Ký PDF tạo sẵn", href: "/user-guide/sign/generated" }] },
    ],
  },

  "sign/generated": {
    slug: "sign/generated",
    title: "Ký Số — Ký PDF tạo sẵn",
    description: "Ký PDF từ form không cần upload file",
    section: "Ký Số",
    icon: "✍️",
    blocks: [
      { type: "p", text: "Nếu không upload file, bạn có thể ký PDF tạo sẵn từ form:" },
      {
        type: "steps",
        items: [
          { title: "Chọn biểu mẫu + chứng thư số", desc: "Chọn 1 trong 9 mẫu MSB và chứng thư số" },
          { title: "Vẽ chữ ký", desc: "Dùng chuột hoặc ngón tay vẽ vào khung canvas" },
          { title: "Nhấn ✍️ Ký PDF Tạo Sẵn (từ form)", desc: "Agent tạo PDF 2 trang (trang 1: dữ liệu form, trang 2: chữ ký)" },
          { title: "Tải xuống PDF đã ký", desc: "Nhấn nút tải xuống → PDF về máy" },
        ],
      },
      { type: "nextSteps", items: [{ label: "Demo end-to-end", href: "/user-guide/demo" }] },
    ],
  },

  demo: {
    slug: "demo",
    title: "Demo end-to-end",
    description: "3 kịch bản demo hoàn chỉnh",
    section: "Demo & FAQ",
    icon: "🎯",
    blocks: [
      { type: "h2", text: "Kịch bản 1: Khách hàng FDI (song ngữ)", anchor: "fdi" },
      {
        type: "steps",
        items: [
          { title: "Mở trang web → nhấn \"FDI Alpha 🌐\"", desc: "Agent giải thích form MSB-EBANK-01-FDI bằng tiếng Anh" },
          { title: "Gõ: ready", desc: "Agent hỏi 7 trường thiếu (tiếng Anh)" },
          { title: "Nhập dữ liệu", desc: "Nguyen Thi Lan | 001098765432 | Ke toan | Maker | OTP | 0901234567 | lan@alphavietnam.vn" },
          { title: "→ READY", desc: "15 fields filled, bilingual output" },
          { title: "Nhấn SOẠN HỒ SƠ", desc: "Checklist + bản mềm + PDF" },
        ],
      },
      { type: "h2", text: "Kịch bản 2: Khách hàng trong nước", anchor: "domestic" },
      {
        type: "steps",
        items: [
          { title: "Nhấn \"CTCP X\"", desc: "Agent giải thích form MSB-EBANK-01 bằng tiếng Việt có dấu" },
          { title: "Gõ: sẵn sàng", desc: "Agent hỏi 7 trường thiếu (tiếng Việt)" },
          { title: "Nhập dữ liệu", desc: "Nguyễn Văn B | 001098765432 | Kế toán | Maker | OTP | 0901234567 | b@congtyx.vn" },
          { title: "→ READY → SOẠN HỒ SƠ", desc: "Tải Text + PDF" },
        ],
      },
      { type: "h2", text: "Kịch bản 3: Upload file + ký số", anchor: "sign-demo" },
      {
        type: "steps",
        items: [
          { title: "Vào trang ✍️ Ký Số", desc: "Chọn form MSB-DS-04 + chứng thư Viettel-CA" },
          { title: "Upload file .txt", desc: "Chứa nội dung form" },
          { title: "Nhấn 🤖 AI Kiểm Tra File", desc: "→ ✅ hợp lệ" },
          { title: "Vẽ chữ ký → ✍️ Ký File", desc: "Tải xuống file đã ký" },
        ],
      },
      { type: "nextSteps", items: [{ label: "Câu hỏi thường gặp", href: "/user-guide/faq" }] },
    ],
  },

  faq: {
    slug: "faq",
    title: "Câu hỏi thường gặp",
    description: "FAQ về sử dụng MSB SmartForm AI",
    section: "Demo & FAQ",
    icon: "❓",
    blocks: [
      {
        type: "faq",
        items: [
          { q: "Tôi muốn thử persona khác nhưng bị dính dữ liệu cũ?", a: "Mỗi persona dùng session riêng — nhấn persona khác sẽ tự reset. Hoặc nhấn nút \"↻ Xoá thông tin cũ, thực hiện lại\"." },
          { q: "Agent trả lời tiếng Việt không dấu?", a: "Không. Agent luôn trả lời tiếng Việt có dấu đầy đủ. Nếu khách hàng FDI nhập tiếng Anh, Agent tự chuyển sang tiếng Anh." },
          { q: "Tôi có thể nhập dữ liệu theo định dạng nào?", a: "3 cách: (1) giátrị1 | giátrị2 | giátrị3, (2) Nhãn: giá trị mỗi dòng, (3) chat tự nhiên." },
          { q: "AI Fill từ trang /forms có pre-fill dữ liệu demo không?", a: "Không. AI Fill yêu cầu khách hàng điền tất cả trường bắt buộc từ đầu." },
          { q: "File upload tối đa bao nhiêu?", a: "5MB. Định dạng: .txt hoặc .pdf." },
          { q: "Dữ liệu khách hàng có thật không?", a: "Không. 100% dữ liệu giả lập. Agent chỉ chuẩn bị hồ sơ — không phê duyệt. Không lưu PIN/OTP/private key." },
        ],
      },
      { type: "callout", variant: "danger", title: "Lưu ý", text: "Dữ liệu khách hàng 100% giả lập. Agent chỉ chuẩn bị hồ sơ — quyền phê duyệt thuộc MSB." },
    ],
  },
};

export function getPage(slug: string): GuidePage | null {
  return PAGES[slug] || null;
}

export function getAllSlugs(): string[] {
  return Object.keys(PAGES);
}

export function getAdjacent(slug: string): { prev?: { slug: string; title: string }; next?: { slug: string; title: string } } {
  const all = NAV.flatMap((s) => s.items);
  const idx = all.findIndex((i) => i.slug === slug);
  if (idx === -1) return {};
  return {
    prev: idx > 0 ? { slug: all[idx - 1].slug, title: all[idx - 1].title } : undefined,
    next: idx < all.length - 1 ? { slug: all[idx + 1].slug, title: all[idx + 1].title } : undefined,
  };
}
