/** @type {import('tailwindcss').Config} */
export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#E30613",
          50: "#FCE8EA",
          100: "#FD5F73",
          500: "#E30613",
          600: "#C90510",
          700: "#A3040D",
        },
        navy: {
          DEFAULT: "#0B1F3A",
          50: "#EAF2FF",
          100: "#B9D6FF",
          500: "#1757A6",
          900: "#0B1F3A",
        },
        ink: {
          900: "#111827",
          700: "#667085",
          500: "#98A2B3",
          200: "#E5E7EB",
          100: "#EAECF0",
          50: "#F8FAFC",
        },
        status: {
          ready: "#00A676",
          readyBg: "#E7F7F1",
          missing: "#F59E0B",
          missingBg: "#FFF7ED",
          review: "#1757A6",
          reviewBg: "#EAF2FF",
          danger: "#E30613",
          dangerBg: "#FCE8EA",
        },
      },
      fontFamily: {
        sans: ["Inter", "Be Vietnam Pro", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        card: "0 1px 3px rgba(11,31,58,.08)",
        hover: "0 8px 24px rgba(11,31,58,.12)",
      },
      borderRadius: { card: "16px", btn: "10px" },
    },
  },
  plugins: [],
};
