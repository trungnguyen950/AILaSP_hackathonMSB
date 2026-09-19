"use client";
import { useEffect, useState } from "react";

export function BackToTop() {
  const [show, setShow] = useState(false);
  useEffect(() => {
    const onScroll = () => setShow(window.scrollY > 400);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  if (!show) return null;
  return (
    <button
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      className="fixed bottom-6 right-6 z-30 flex h-11 w-11 items-center justify-center rounded-full bg-navy-900 text-white shadow-hover transition hover:bg-navy-500"
      aria-label="Back to top"
    >
      ↑
    </button>
  );
}
