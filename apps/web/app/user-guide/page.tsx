import Link from "next/link";
import { NAV, PAGES } from "@/lib/guide-content";

export default function UserGuideIndex() {
  const allPages = NAV.flatMap((sec) =>
    sec.items.map((it) => ({ ...it, section: sec.section, page: PAGES[it.slug] }))
  );

  return (
    <div>
      <div className="mb-8">
        <nav className="mb-3 text-xs text-ink-500">
          <Link href="/" className="hover:text-ink-900">Trang chủ</Link>
          <span className="mx-1">/</span>
          <span className="text-ink-900">Hướng dẫn</span>
        </nav>
        <h1 className="text-3xl font-extrabold text-ink-900">Hướng dẫn sử dụng</h1>
        <p className="mt-2 text-sm text-ink-700">
          MSB SmartForm AI — Trợ lý lập hồ sơ & biểu mẫu MSB. One request. The right form. Ready to sign.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {allPages.map((pg) => (
          <Link
            key={pg.slug}
            href={`/user-guide/${pg.slug}`}
            className="group rounded-card border border-ink-200 bg-white p-5 shadow-card transition hover:border-brand/40 hover:shadow-hover"
          >
            <div className="mb-2 flex items-center gap-2">
              <span className="text-2xl">{pg.icon}</span>
              <span className="rounded bg-ink-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-ink-500">
                {pg.section}
              </span>
            </div>
            <h2 className="text-sm font-bold text-ink-900 group-hover:text-brand">{pg.title}</h2>
            <p className="mt-1 text-xs text-ink-700">{pg.page?.description}</p>
          </Link>
        ))}
      </div>

      <div className="mt-8 rounded-card border border-navy-100 bg-navy-50 p-5">
        <h2 className="text-sm font-bold text-navy-900">💡 Mẹo nhanh</h2>
        <p className="mt-1 text-sm text-navy-900/80">
          Dùng ô tìm kiếm ở thanh bên trái để tìm nhanh hướng dẫn. Mỗi bài viết có liên kết
          "Bước tiếp theo" ở cuối để điều hướng tiếp.
        </p>
      </div>
    </div>
  );
}
