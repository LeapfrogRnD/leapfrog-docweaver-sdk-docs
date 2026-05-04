import React from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./app/App.tsx";
import "./styles/index.css";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);
import { useState, useRef, useEffect, useCallback } from "react";

type Variant = "dark" | "light" | "aurora";

interface ProcessingWorkspaceProps {
  leftPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  variant?: Variant;
}

// ── Theme tokens ─────────────────────────────────────────────────────────────
const THEMES = {
  dark: {
    container: {
      backgroundColor: "rgba(255,255,255,0.04)",
      border: "1px solid rgba(255,255,255,0.10)",
      backdropFilter: "blur(24px)",
      boxShadow:
        "0 4px 24px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.04)",
    },
    labelColor: "rgba(148,163,184,0.40)",
    labelAccent: "#4ADE80",
    dividerLine: "rgba(255,255,255,0.07)",
    dividerLineHover: "rgba(3,142,67,0.55)",
    handleBg: "rgba(255,255,255,0.05)",
    handleBgHover: "rgba(3,142,67,0.16)",
    handleBorder: "rgba(255,255,255,0.10)",
    handleBorderHover: "rgba(3,142,67,0.40)",
    dotColor: "rgba(148,163,184,0.38)",
    dotColorHover: "rgba(74,222,128,0.90)",
  },
  light: {
    container: {
      backgroundColor: "rgba(255,255,255,0.90)",
      border: "1px solid rgba(0,0,0,0.06)",
      backdropFilter: "blur(40px)",
      boxShadow:
        "0 20px 72px rgba(0,0,0,0.09), inset 0 1px 0 rgba(255,255,255,0.65)",
    },
    labelColor: "rgba(39,39,42,0.35)",
    labelAccent: "#038E43",
    dividerLine: "rgba(0,0,0,0.07)",
    dividerLineHover: "rgba(3,142,67,0.45)",
    handleBg: "rgba(0,0,0,0.04)",
    handleBgHover: "rgba(3,142,67,0.08)",
    handleBorder: "rgba(0,0,0,0.08)",
    handleBorderHover: "rgba(3,142,67,0.30)",
    dotColor: "rgba(82,82,91,0.38)",
    dotColorHover: "rgba(3,142,67,0.85)",
  },
  aurora: {
    container: {
      backgroundColor: "rgba(255,255,255,0.06)",
      border: "1px solid rgba(255,255,255,0.08)",
      backdropFilter: "blur(20px)",
      boxShadow:
        "0 10px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06)",
    },
    labelColor: "rgba(148,163,184,0.38)",
    labelAccent: "#818CF8",
    dividerLine: "rgba(255,255,255,0.07)",
    dividerLineHover: "rgba(99,102,241,0.60)",
    handleBg: "rgba(255,255,255,0.05)",
    handleBgHover: "rgba(99,102,241,0.22)",
    handleBorder: "rgba(255,255,255,0.08)",
    handleBorderHover: "rgba(99,102,241,0.45)",
    dotColor: "rgba(148,163,184,0.34)",
    dotColorHover: "rgba(165,180,252,0.92)",
  },
} as const;

// ── Component ───────────────────────────────────────────────────────────────
export function ProcessingWorkspace({
  leftPanel,
  rightPanel,
  variant = "dark",
}: ProcessingWorkspaceProps) {
  const [split, setSplit] = useState(50); // percentage width of left panel
  const [hoveringDivider, setHoveringDivider] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  // ── Mouse move & up handlers ──────────────────────────────────────────────
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!dragging.current || !containerRef.current) return;
    const { left, width } = containerRef.current.getBoundingClientRect();
    const pct = Math.max(25, Math.min(75, ((e.clientX - left) / width) * 100));
    setSplit(pct);
  }, []);

  const handleMouseUp = useCallback(() => {
    if (dragging.current) {
      dragging.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    }
  }, []);

  useEffect(() => {
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  const startDrag = (e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  };

  const t = THEMES[variant];
  const dividerActive = hoveringDivider || dragging.current;

  return (
    <div
      style={{
        ...t.container,
        borderRadius: "24px",
        padding: "20px 24px 24px",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          marginBottom: "14px",
        }}
      >
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: "50%",
            backgroundColor: t.labelAccent,
            boxShadow: `0 0 6px ${t.labelAccent}`,
          }}
        />
        <span
          style={{
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: "0.07em",
            textTransform: "uppercase",
            color: t.labelColor,
          }}
        >
          Processing Workspace
        </span>
        <div style={{ flex: 1, height: 1, backgroundColor: t.dividerLine }} />
        <span
          style={{
            fontSize: 11,
            color: t.labelColor,
            letterSpacing: "-0.01em",
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {Math.round(split)} / {Math.round(100 - split)}
        </span>
      </div>

      {/* ── Panels ──────────────────────────────────────────────────────────── */}
      <div
        ref={containerRef}
        style={{
          display: "flex",
          height: 600,
          overflow: "hidden",
          position: "relative",
        }}
      >
        {/* Left Panel */}
        <div
          style={{
            width: `${split}%`,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            paddingRight: 10,
          }}
        >
          {leftPanel}
        </div>

        {/* Divider */}
        <div
          onMouseDown={startDrag}
          onMouseEnter={() => setHoveringDivider(true)}
          onMouseLeave={() => setHoveringDivider(false)}
          style={{
            width: 16,
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
            cursor: "col-resize",
            zIndex: 10,
          }}
        >
          <div
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              left: "50%",
              transform: "translateX(-50%)",
              width: dividerActive ? 2 : 1,
              backgroundColor: dividerActive
                ? t.dividerLineHover
                : t.dividerLine,
              borderRadius: 2,
              transition: "all 0.18s ease",
            }}
          />
          <div
            style={{
              position: "relative",
              zIndex: 1,
              width: 20,
              height: 36,
              borderRadius: 8,
              backgroundColor: dividerActive ? t.handleBgHover : t.handleBg,
              border: `1px solid ${
                dividerActive ? t.handleBorderHover : t.handleBorder
              }`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.18s ease",
              boxShadow: dividerActive ? `0 0 14px ${t.handleBgHover}` : "none",
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 3,
              }}
            >
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  style={{
                    width: 3,
                    height: 3,
                    borderRadius: "50%",
                    backgroundColor: dividerActive
                      ? t.dotColorHover
                      : t.dotColor,
                    transition: "background-color 0.18s ease",
                  }}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            paddingLeft: 10,
          }}
        >
          {rightPanel}
        </div>
      </div>
    </div>
  );
}
