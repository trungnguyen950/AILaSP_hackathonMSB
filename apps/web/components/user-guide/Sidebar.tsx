"use client";
import { useState, useMemo } from "react";
import Link from "next/link";
import { NAV, PAGES } from "@/lib/guide-content";

export function Sidebar({ activeSlug }: { activeSlug?: string }) {
  const [query, setQuery] = useState("");
  const [mobileOpen, setMobileOpen] = useState(false);

  const filteredNav = useMemo(() => {
    if (!query.trim()) return NAV;
    const q = query.toLowerCase();
    return NAV.map((sec) => ({
      ...sec,
      items: sec.items.filter((it) => {
        const page = PAGES[it.slug];
        return (
          it.title.toLowerCase().includes(q) ||
          sec.section.toLowerCase().includes(q) ||
          (page?.description.toLowerCase().includes(q) ?? false)
        );
      }),
    })).filter((sec) => sec.items.length > 0);
  }, [query]);

  const sidebarContent = (
    <nav className="flex h-full flex-col">
      <div className="p-4">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tìm hướng dẫn..."
            className="w-full rounded-btn border border-ink-200 bg-ink-50 py-2 pl-9 pr-3 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
            aria-label="Search"
          />
          <span className="absolute left-3 top-2.5 text-ink-500">🔍</span>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto px-2 pb-4">
        {filteredNav.map((sec) => {
          const sectionSlugs = sec.items.map((i) => i.slug);
          const activeInSection = activeSlug && sectionSlugs.includes(activeSlug);
          return (
            <div key={sec.section} className="mb-4">
              <div className={`mb-1 px-3 text-xs font-bold uppercase tracking-wide ${activeInSection ? "text-brand" : "text-ink-500"}`}>
                {sec.section}
              </div>
              <ul className="space-y-0.5">
                {sec.items.map((it) => {
                  const isActive = activeSlug === it.slug;
                  return (
                    <li key={it.slug}>
                      <Link
                        href={`/user-guide/${it.slug}`}
                        onClick={() => setMobileOpen(false)}
                        className={`flex items-center gap-2 rounded-btn px-3 py-2 text-sm transition ${
                          isActive
                            ? "bg-brand-50 font-semibold text-brand"
                            : "text-ink-700 hover:bg-ink-50 hover:text-ink-900"
                        }`}
                      >
                        <span className="text-xs">{it.icon}</span>
                        <span>{it.title}</span>
                        {isActive && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-brand" />}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
        {filteredNav.length === 0 && (
          <p className="px-3 py-4 text-sm text-ink-500">Không tìm thấy kết quả.</p>
        )}
      </div>
    </nav>
  );

  return (
    <>
      <button
        onClick={() => setMobileOpen(true)}
        className="fixed left-4 top-20 z-30 rounded-btn border border-ink-200 bg-white px-3 py-2 text-sm font-semibold text-ink-900 shadow-card lg:hidden"
        aria-label="Open navigation"
      >
        ☰ Mục lục
      </button>
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden" onClick={() => setMobileOpen(false)}>
          <div className="absolute inset-0 bg-black/30" />
          <div className="absolute left-0 top-0 h-full w-80 max-w-[85vw] bg-white shadow-xl" onClick={(e) => e.stopPropagation()}>
            {sidebarContent}
          </div>
        </div>
      )}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 border-r border-ink-200 bg-white lg:block">
        {sidebarContent}
      </aside>
    </>
  );
}
