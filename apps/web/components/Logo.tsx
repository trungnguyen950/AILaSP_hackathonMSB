export function Logo({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 200 200" role="img" aria-label="MSB SmartForm AI">
      <path d="M100 10 L190 100 L100 190 L10 100 Z" fill="#E30613" />
      <path d="M100 10 L190 100 L100 100 Z" fill="#FFFFFF" fillOpacity="0.12" />
      <path d="M100 28 L172 100 L100 172 L28 100 Z" fill="none" stroke="#FFFFFF" strokeOpacity="0.9" strokeWidth="3" />
      <g stroke="#FFFFFF" strokeWidth="5.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="100" cy="60" r="8" />
        <line x1="100" y1="68" x2="100" y2="132" />
        <line x1="83" y1="86" x2="117" y2="86" />
        <path d="M76 130 Q100 154 124 130" />
        <path d="M76 130 L71 119" />
        <path d="M124 130 L129 119" />
      </g>
    </svg>
  );
}

export function Wordmark({ light = false }: { light?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <Logo size={40} />
      <div className="leading-tight">
        <div className="text-lg font-extrabold">
          <span className={light ? "text-white" : "text-navy"}>MSB</span>{" "}
          <span className="brand-text">SmartForm</span>
        </div>
        <div className={`text-[10px] font-semibold tracking-wider ${light ? "text-white/60" : "text-ink-700"}`}>
          AI · TRỢ LÝ LẬP HỒ SƠ
        </div>
      </div>
    </div>
  );
}
