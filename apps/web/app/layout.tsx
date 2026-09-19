import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MSB SmartForm AI — Trợ lý lập hồ sơ & biểu mẫu MSB",
  description: "Nói nhu cầu — Agent chọn đúng mẫu MSB, điền giúp, sinh checklist.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
