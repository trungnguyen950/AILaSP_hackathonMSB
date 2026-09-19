import Link from "next/link";
import { Wordmark } from "@/components/Logo";
import { Sidebar } from "@/components/user-guide/Sidebar";
import { BackToTop } from "@/components/user-guide/BackToTop";

export default function UserGuideLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-ink-50">
      <header className="navy-bg text-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <Link href="/" className="flex items-center">
            <Wordmark light />
          </Link>
          <nav className="flex items-center gap-3">
            <Link href="/user-guide" className="rounded-btn bg-white/15 px-3 py-1.5 text-xs font-semibold text-white">
              📖 Hướng dẫn
            </Link>
            <a
              href="mailto:support@msb.com.vn"
              className="rounded-btn border border-white/20 px-3 py-1.5 text-xs font-semibold text-white/80 transition hover:bg-white/10 hover:text-white"
            >
              Liên hệ hỗ trợ
            </a>
          </nav>
        </div>
      </header>
      <div className="mx-auto flex max-w-6xl">
        <Sidebar />
        <main className="min-w-0 flex-1 px-4 py-6 lg:px-8 lg:py-8">
          {children}
        </main>
      </div>
      <BackToTop />
    </div>
  );
}
