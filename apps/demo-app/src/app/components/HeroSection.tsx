import React, { useState, useEffect } from "react";
import { ArrowRight, Zap } from "lucide-react";
import { HeroAnimation } from "./HeroAnimation";

type Variant = "dark" | "light" | "aurora";

interface HeroSectionProps {
  variant: Variant;
  onTryDemo?: () => void;
}

// ── Static mock data for product preview ─────────────────────────────────────
const PREVIEW_FIELDS = [
  { key: "Document Type", value: "Invoice", badge: true },
  { key: "Vendor", value: "Acme Corp Ltd", badge: false },
  { key: "Total Amount", value: "$12,450.00", badge: false },
  { key: "Issue Date", value: "Mar 09, 2026", badge: false },
  { key: "Invoice No.", value: "INV-2026-0312", badge: false },
];

const RAW_LINES = [
  { w: "88%", opacity: 1 },
  { w: "72%", opacity: 0.75 },
  { w: "82%", opacity: 0.9 },
  { w: "58%", opacity: 0.65 },
  { w: "79%", opacity: 0.85 },
  { w: "91%", opacity: 1 },
  { w: "67%", opacity: 0.7 },
  { w: "84%", opacity: 0.9 },
  { w: "61%", opacity: 0.72 },
  { w: "76%", opacity: 0.82 },
  { w: "52%", opacity: 0.6 },
  { w: "88%", opacity: 0.95 },
];

// ── Per-variant theme tokens ──────────────────────────────────────────────────
function getTheme(variant: Variant) {
  const isAurora = variant === "aurora";
  const isDark = variant === "dark" || variant === "aurora";

  const accentGrd = isAurora
    ? "linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)"
    : "linear-gradient(135deg, #038E43 0%, #10b981 100%)";
  const accentColor = isAurora ? "#818CF8" : "#038E43";
  const accentGlow = isAurora
    ? "rgba(99,102,241,0.30)"
    : isDark
    ? "rgba(3,142,67,0.28)"
    : "rgba(3,142,67,0.18)";
  const accentGlowW = isAurora
    ? "rgba(99,102,241,0.12)"
    : "rgba(3,142,67,0.10)";

  return {
    isDark,
    isAurora,
    accentGrd,
    accentColor,
    accentGlow,
    accentGlowW,

    // Text
    headlineColor: isDark ? "#FFFFFF" : "var(--color-primary-black)",
    headlineAccent: accentColor,
    subColor: isDark ? "rgba(148,163,184,0.75)" : "#6b7280",
    statColor: isDark ? "#FFFFFF" : "var(--color-primary-black)",
    statLabel: isDark ? "rgba(148,163,184,0.60)" : "#9ca3af",

    // Badge pill
    badgeBg: isAurora
      ? "rgba(99,102,241,0.10)"
      : isDark
      ? "rgba(255,255,255,0.06)"
      : "rgba(0,0,0,0.04)",
    badgeBorder: isAurora
      ? "rgba(99,102,241,0.28)"
      : isDark
      ? "rgba(255,255,255,0.11)"
      : "rgba(0,0,0,0.08)",
    badgeColor: isAurora
      ? accentColor
      : isDark
      ? "rgba(226,232,240,0.72)"
      : "#71717A",

    // Buttons
    primaryShadow: `0 0 28px ${accentGlow}, 0 4px 16px rgba(0,0,0,0.20), inset 0 1px 0 rgba(255,255,255,0.14)`,
    primaryShadowH: `0 0 44px ${accentGlow}, 0 8px 24px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.18)`,
    secBg: isDark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.03)",
    secBgH: isDark ? "rgba(255,255,255,0.09)" : "rgba(0,0,0,0.06)",
    secBorder: isDark ? "rgba(255,255,255,0.12)" : "rgba(0,0,0,0.10)",
    secColor: isDark ? "rgba(226,232,240,0.82)" : "var(--color-primary-black)",

    // Preview innards
    divider: isDark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.07)",
    badgeBg2: isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.04)",
  } as const;
}

export function HeroSection({ variant, onTryDemo }: HeroSectionProps) {
  const t = getTheme(variant);
  const [priHover, setPriHover] = useState(false);
  const [compactStats, setCompactStats] = useState<boolean>(
    typeof window !== "undefined" ? window.innerWidth <= 768 : false
  );

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(max-width: 768px)");
    const handler = (e: MediaQueryListEvent | MediaQueryList) =>
      setCompactStats(Boolean((e as any).matches ?? (e as any).matches));
    // initialize
    handler(mq as any);
    // attach listener (support both modern and older APIs)
    if ((mq as any).addEventListener) {
      (mq as any).addEventListener("change", handler);
    } else {
      (mq as any).addListener(handler);
    }
    return () => {
      if ((mq as any).removeEventListener) {
        (mq as any).removeEventListener("change", handler);
      } else {
        (mq as any).removeListener(handler);
      }
    };
  }, []);

  const stats = [
    { value: "Multi", label: "LLM / OCR / VLM Support" },
    { value: "20+", label: "Document Types" },
    { value: "0 Code", label: "Pipeline Builder" },
  ];

  return (
    <section
      style={{
        position: "relative",
        overflow: "visible",
        padding: "88px 40px 80px",
      }}
    >
      <div
        className="grid grid-cols-1 lg:grid-cols-2 items-center"
        style={{ maxWidth: "1200px", margin: "0 auto", gap: "64px" }}
      >
        {/* LEFT: Text content */}
        <div style={{ maxWidth: "540px" }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "6px 14px",
              borderRadius: "999px",
              backgroundColor: t.badgeBg,
              border: `1px solid ${t.badgeBorder}`,
              marginBottom: "28px",
              color: t.headlineColor,
              fontSize: "13px",
              fontWeight: 600,
            }}
          >
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: "18px",
                height: "18px",
                borderRadius: "50%",
                background: t.accentGrd,
                color: "white",
              }}
            >
              <Zap style={{ width: 12, height: 12 }} />
            </span>
            <span style={{ color: t.subColor }}>AI-Powered OCR Platform</span>
          </div>

          <h1
            style={{
              color: t.headlineColor,
              fontSize: "clamp(36px, 4.5vw, 54px)",
              fontWeight: 700,
              lineHeight: 1.07,
              letterSpacing: "-0.03em",
              marginBottom: "20px",
            }}
          >
            Turn Documents Into{' '}
            <span
              style={{
                background: t.accentGrd,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}
            >
              Structured Data
            </span>
            {' '}Instantly
          </h1>

          <p
            style={{
              color: t.subColor,
              fontSize: "17px",
              lineHeight: 1.65,
              marginBottom: "40px",
              maxWidth: "430px",
            }}
          >
            AI-powered document extraction for receipts, invoices, bank statements, and financial forms.
          </p>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              marginBottom: "52px",
              flexWrap: "wrap",
            }}
          >
            <button
              onClick={onTryDemo}
              onMouseEnter={() => setPriHover(true)}
              onMouseLeave={() => setPriHover(false)}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "12px 22px",
                borderRadius: "999px",
                background: t.accentGrd,
                border: "none",
                boxShadow: priHover ? t.primaryShadowH : t.primaryShadow,
                fontSize: "15px",
                fontWeight: 600,
                color: "#FFFFFF",
                cursor: "pointer",
                transition: "all 0.18s ease",
              }}
            >
              Try Interactive Demo
              <ArrowRight style={{ width: 15, height: 15 }} />
            </button>


          </div>

          {/* Stats row (disable left-border/padding on compact screens to prevent misalignment when items wrap) */}
          <div style={{ display: "flex", gap: "36px", flexWrap: "wrap" }}>
            {stats.map(({ value, label }, i) => (
              <div
                key={label}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "4px",
                  paddingLeft: !compactStats && i > 0 ? "36px" : 0,
                  borderLeft: !compactStats && i > 0 ? `1px solid ${t.divider}` : "none",
                }}
              >
                <span
                  style={{
                    fontSize: "20px",
                    fontWeight: 700,
                    color: t.statColor,
                    letterSpacing: "-0.03em",
                    lineHeight: 1,
                  }}
                >
                  {value}
                </span>
                <span
                  style={{ fontSize: "12px", color: t.statLabel, letterSpacing: "-0.01em" }}
                >
                  {label}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT: Floating product preview / animation */}
        <div
          style={{
            position: "relative",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <HeroAnimation variant={variant} />
        </div>
      </div>
    </section>
  );
}
