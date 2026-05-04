import React from "react";

export const accordionCard = (isOpen: boolean): React.CSSProperties => ({
  backgroundColor: isOpen
    ? "rgba(255,255,255,0.05)"
    : "rgba(255,255,255,0.03)",
  border: `1px solid ${
    isOpen ? "rgba(255,255,255,0.12)" : "rgba(255,255,255,0.07)"
  }`,
  backdropFilter: "blur(24px)",
  borderRadius: "var(--radius-lg, 14px)",
  overflow: "hidden",
  boxShadow: isOpen
    ? "0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06)"
    : "0 2px 10px rgba(0,0,0,0.20), inset 0 1px 0 rgba(255,255,255,0.03)",
  transition:
    "box-shadow 0.22s cubic-bezier(0.4,0,0.2,1), border-color 0.22s cubic-bezier(0.4,0,0.2,1), background-color 0.22s cubic-bezier(0.4,0,0.2,1)",
});

export const stepBadge: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  width: "20px",
  height: "20px",
  borderRadius: "6px",
  flexShrink: 0,
  backgroundColor: "rgba(255,255,255,0.08)",
  border: "1px solid rgba(255,255,255,0.10)",
  fontSize: "10px",
  fontWeight: 700,
  color: "rgba(148,163,184,0.80)",
};

export const accordionSep: React.CSSProperties = {
  height: "1px",
  backgroundColor: "rgba(255,255,255,0.07)",
  margin: "0 16px",
};

export const runBtn = (canRun: boolean): React.CSSProperties => ({
  width: "100%",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  gap: "8px",
  padding: "10px 0",
  borderRadius: "100px",
  fontSize: "13px",
  fontWeight: 500,
  letterSpacing: "-0.01em",
  cursor: canRun ? "pointer" : "not-allowed",
  transition: "all 0.22s cubic-bezier(0.4,0,0.2,1)",
  ...(canRun
    ? {
        background: "linear-gradient(135deg, #038E43 0%, #10b981 100%)",
        border: "1px solid rgba(74,222,128,0.22)",
        boxShadow:
          "0 4px 18px rgba(3,142,67,0.28), 0 1px 0 rgba(255,255,255,0.10) inset",
        color: "#FFFFFF",
      }
    : {
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.08)",
        boxShadow: "none",
        color: "rgba(255,255,255,0.22)",
      }),
});
