import Link from "next/link";
import { Wordmark } from "./Logo";

export function Navbar({ active = "home" }: { active?: "home" | "forms" | "sign" }) {
  return (
    <header className="navy-bg text-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center">
          <Wordmark light />
        </Link>
        <nav className="flex items-center gap-1">
          <Link
            href="/"
            className={`rounded-btn px-3 py-1.5 text-xs font-semibold transition ${
              active === "home" ? "bg-white/15 text-white" : "text-white/60 hover:text-white hover:bg-white/10"
            }`}
          >
            💬 Chat
          </Link>
          <Link
            href="/forms/"
            className={`rounded-btn px-3 py-1.5 text-xs font-semibold transition ${
              active === "forms" ? "bg-white/15 text-white" : "text-white/60 hover:text-white hover:bg-white/10"
            }`}
          >
            📋 Mẫu Biểu Mẫu
          </Link>
          <Link
            href="/sign/"
            className={`rounded-btn px-3 py-1.5 text-xs font-semibold transition ${
              active === "sign" ? "bg-white/15 text-white" : "text-white/60 hover:text-white hover:bg-white/10"
            }`}
          >
            ✍️ Ký Số
          </Link>
          <span className="ml-2 hidden text-[11px] font-semibold tracking-wide text-white/40 sm:inline">
            AI FOR CUSTOMERS · MSB AI HACKATHON 2026
          </span>
        </nav>
      </div>
    </header>
  );
}
