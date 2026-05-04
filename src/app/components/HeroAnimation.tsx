import { useEffect, useState, React } from "react";
import {
  FileText,
  Receipt,
  FileSpreadsheet,
  Check,
  ArrowRight,
} from "lucide-react";
interface Document {
  id: number;
  icon: typeof FileText;
  type: string;
  x: number;
  opacity: number;
  scale: number;
}

interface ExtractedField {
  id: number;
  label: string;
  value: string;
}

interface DataParticle {
  id: number;
  x: number;
  y: number;
  char: string;
}

type Variant = "dark" | "light" | "aurora";

interface HeroAnimationProps {
  variant?: Variant;
}

// ── Theme color tokens based on variant ──────────────────────────────────
function getTheme(variant: Variant) {
  const isAurora = variant === "aurora";
  const isDark = variant === "dark" || variant === "aurora";

  if (isAurora) {
    return {
      // Aurora: indigo/violet palette
      primary: "#6366F1",
      primaryLight: "#818CF8",
      primaryLighter: "#A5B4FC",
      secondary: "#8B5CF6",
      labelBase: "rgba(148,163,184,0.90)",
      labelActive: "#A5B4FC",
      ambientGlow: "rgba(99,102,241,0.20)",
      // RGBA color functions
      c: (opacity: number) => `rgba(99,102,241,${opacity})`,
      c2: (opacity: number) => `rgba(139,92,246,${opacity})`,
      cLight: (opacity: number) => `rgba(129,140,248,${opacity})`,
    };
  } else {
    // Dark/Light: brand green palette
    return {
      primary: isDark ? "#038E43" : "#038E43",
      primaryLight: "#10b981",
      primaryLighter: "#22c55e",
      secondary: "#059669",
      labelBase: isDark ? "rgba(148,163,184,0.90)" : "rgba(82,82,91,0.90)",
      labelActive: isDark ? "#22c55e" : "#038E43",
      ambientGlow: isDark ? "rgba(3,142,67,0.18)" : "rgba(16,185,129,0.12)",
      // RGBA color functions
      c: (opacity: number) =>
        isDark ? `rgba(3,142,67,${opacity})` : `rgba(16,185,129,${opacity})`,
      c2: (opacity: number) =>
        isDark ? `rgba(16,185,129,${opacity})` : `rgba(5,150,105,${opacity})`,
      cLight: (opacity: number) =>
        isDark ? `rgba(34,197,94,${opacity})` : `rgba(16,185,129,${opacity})`,
    };
  }
}

export function HeroAnimation({ variant = "aurora" }: HeroAnimationProps) {
  const [animationPhase, setAnimationPhase] = useState<
    "idle" | "entering" | "scanning" | "extracting" | "complete"
  >("idle");
  const [documents, setDocuments] = useState<Document[]>([]);
  const [scanProgress, setScanProgress] = useState(0);
  const [extractedFields, setExtractedFields] = useState<ExtractedField[]>([]);
  const [dataParticles, setDataParticles] = useState<DataParticle[]>([]);
  const [showComplete, setShowComplete] = useState(false);

  const theme = getTheme(variant);

  useEffect(() => {
    const runAnimation = () => {
      // Reset all state
      setAnimationPhase("idle");
      setDocuments([]);
      setScanProgress(0);
      setExtractedFields([]);
      setDataParticles([]);
      setShowComplete(false);

      // Phase 1: Documents appear on left (200ms)
      setTimeout(() => {
        const docTypes = [
          { icon: FileText, type: "Invoice" },
          { icon: Receipt, type: "Receipt" },
          { icon: FileSpreadsheet, type: "Form" },
        ];

        docTypes.forEach((doc, i) => {
          setTimeout(() => {
            setDocuments((prev) => [
              ...prev,
              {
                id: i,
                icon: doc.icon,
                type: doc.type,
                x: -150,
                opacity: 0,
                scale: 0.9,
              },
            ]);

            setTimeout(() => {
              setDocuments((prev) =>
                prev.map((d) =>
                  d.id === i ? { ...d, opacity: 1, scale: 1, x: 0 } : d
                )
              );
            }, 50);
          }, i * 100);
        });
      }, 200);

      // Phase 2: Documents slide toward center (1200ms)
      setTimeout(() => {
        setAnimationPhase("entering");
        setDocuments((prev) => prev.map((d) => ({ ...d, x: 120 })));
      }, 1200);

      // Phase 3: Start scanning (1800ms)
      setTimeout(() => {
        setAnimationPhase("scanning");

        let progress = 0;
        const scanInterval = setInterval(() => {
          progress += 2;
          setScanProgress(progress);

          if (progress > 30 && progress < 95 && Math.random() > 0.65) {
            const chars = ["A", "B", "1", "2", "$", "#", "X"];
            setDataParticles((prev) => [
              ...prev.slice(-15),
              {
                id: Date.now() + Math.random(),
                x: 48,
                y: 45 + Math.random() * 10,
                char: chars[Math.floor(Math.random() * chars.length)],
              },
            ]);
          }

          if (progress >= 100) {
            clearInterval(scanInterval);
            setAnimationPhase("extracting");
          }
        }, 30);
      }, 1800);

      // Phase 4: Show extracted fields (3200ms)
      setTimeout(() => {
        const fields = [
          { label: "Invoice Number", value: "#INV-2026-0312" },
          { label: "Date", value: "Mar 12, 2026" },
          { label: "Vendor Name", value: "Acme Corp Ltd" },
          { label: "Total Amount", value: "$12,450.00" },
        ];

        fields.forEach((field, i) => {
          setTimeout(() => {
            setExtractedFields((prev) => [
              ...prev,
              {
                id: i,
                label: field.label,
                value: field.value,
              },
            ]);
          }, i * 150);
        });
      }, 3200);

      // Phase 5: Show complete state (3900ms)
      setTimeout(() => {
        setAnimationPhase("complete");
        setShowComplete(true);
      }, 3900);

      // Restart cycle (6000ms)
      setTimeout(() => {
        runAnimation();
      }, 6000);
    };

    runAnimation();
  }, []);

  const isActive =
    animationPhase === "scanning" || animationPhase === "extracting";
  const isComplete = animationPhase === "complete";

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        maxWidth: "720px",
        height: "420px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 24px",
      }}
    >
      {/* Background ambient glow */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "550px",
          height: "350px",
          background: `radial-gradient(ellipse at center, ${theme.ambientGlow} 0%, transparent 70%)`,
          filter: "blur(100px)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      {/* LEFT: Unstructured Documents */}
      <div
        style={{
          position: "relative",
          width: "170px",
          height: "100%",
          display: "flex",
          alignItems: "center",
          zIndex: 1,
        }}
      >
        <div style={{ position: "relative", width: "130px", height: "210px" }}>
          <div
            style={{
              position: "absolute",
              top: "-36px",
              left: "50%",
              transform: "translateX(-50%)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "6px",
              transition: "all 0.6s ease",
              opacity:
                documents.length > 0 &&
                animationPhase !== "entering" &&
                animationPhase !== "scanning" &&
                animationPhase !== "extracting" &&
                animationPhase !== "complete"
                  ? 1
                  : 0,
              zIndex: 20,
            }}
          >
            <div
              style={{
                fontSize: "10px",
                fontWeight: 600,
                color: theme.labelBase,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                whiteSpace: "nowrap",
                transition: "all 0.6s ease",
              }}
            >
              Unstructured
            </div>
            <div
              style={{
                width: "1px",
                height: "14px",
                backgroundColor: "rgba(148,163,184,0.35)",
                transition: "all 0.6s ease",
              }}
            />
          </div>

          {documents.map((doc, index) => {
            const Icon = doc.icon;
            const offset = index * 8;
            const rotation = (index - 1) * 4;

            return (
              <div
                key={doc.id}
                style={{
                  position: "absolute",
                  left: `${doc.x}px`,
                  top: "50%",
                  transform: `translateY(-50%) translateY(${offset}px) rotate(${rotation}deg) scale(${doc.scale})`,
                  width: "115px",
                  height: "150px",
                  backgroundColor: "rgba(255,255,255,0.08)",
                  border: "1px solid rgba(255,255,255,0.16)",
                  borderRadius: "11px",
                  backdropFilter: "blur(12px)",
                  boxShadow:
                    "0 10px 36px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.10)",
                  padding: "15px",
                  opacity: doc.opacity,
                  transition:
                    animationPhase === "entering"
                      ? "all 0.8s cubic-bezier(0.4, 0, 0.2, 1)"
                      : "all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)",
                  zIndex: 10 - index,
                }}
              >
                <div
                  style={{
                    width: "30px",
                    height: "30px",
                    borderRadius: "8px",
                    background: `linear-gradient(135deg, ${theme.c(
                      0.38
                    )} 0%, ${theme.c2(0.38)} 100%)`,
                    border: `1px solid ${theme.c(0.5)}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: "11px",
                  }}
                >
                  <Icon
                    style={{
                      width: "15px",
                      height: "15px",
                      color: theme.primaryLighter,
                    }}
                  />
                </div>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "5px",
                  }}
                >
                  {[72, 58, 68, 52, 78].map((width, i) => (
                    <div
                      key={i}
                      style={{
                        width: `${width}%`,
                        height: i === 0 ? "5px" : "3px",
                        backgroundColor: "rgba(255,255,255,0.16)",
                        borderRadius: "2px",
                      }}
                    />
                  ))}
                </div>
                <div
                  style={{
                    marginTop: "11px",
                    display: "grid",
                    gridTemplateColumns: "repeat(2, 1fr)",
                    gap: "4px",
                  }}
                >
                  {[...Array(4)].map((_, i) => (
                    <div
                      key={i}
                      style={{
                        height: "11px",
                        backgroundColor: "rgba(255,255,255,0.11)",
                        border: "1px solid rgba(255,255,255,0.14)",
                        borderRadius: "3px",
                      }}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
        {animationPhase === "entering" && (
          <div
            style={{
              position: "absolute",
              left: "140px",
              top: "50%",
              transform: "translateY(-50%)",
              width: "160px",
              height: "160px",
              borderRadius: "50%",
              border: `2px solid ${theme.c(0.45)}`,
              animation: "hero-ocr-pulse-ring 1.5s ease-out infinite",
            }}
          />
        )}
      </div>

      {/* CENTER: OCR Scanner */}
      <div
        style={{
          position: "relative",
          width: "200px",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          zIndex: 2,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: "-32px",
            top: "50%",
            transform: "translateY(-50%)",
            opacity:
              animationPhase === "entering" || isActive || isComplete ? 1 : 0.3,
            transition: "opacity 0.6s ease",
            zIndex: 1,
          }}
        >
          <ArrowRight
            style={{
              width: "22px",
              height: "22px",
              color: theme.c(0.65),
              filter: `drop-shadow(0 0 10px ${theme.c(0.45)})`,
            }}
          />
        </div>
        <div style={{ position: "relative" }}>
          <div
            style={{
              position: "absolute",
              top: "-36px",
              left: "50%",
              transform: "translateX(-50%)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "6px",
              zIndex: 5,
              transition: "all 0.6s ease",
              opacity: animationPhase === "idle" ? 0 : 1,
            }}
          >
            <div
              style={{
                fontSize: "10px",
                fontWeight: 600,
                color: isActive ? theme.labelActive : theme.labelBase,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                whiteSpace: "nowrap",
                transition: "all 0.6s ease",
                textShadow: isActive
                  ? `0 0 16px ${theme.c(0.8)}, 0 0 32px ${theme.c(0.4)}`
                  : "none",
                animation: isActive
                  ? "hero-ocr-label-glow 2s ease-in-out infinite"
                  : "none",
              }}
            >
              OCR Processing
            </div>
            <div
              style={{
                width: "1px",
                height: "14px",
                backgroundColor: isActive
                  ? theme.c(0.45)
                  : "rgba(148,163,184,0.25)",
                transition: "all 0.6s ease",
              }}
            />
          </div>
          <div
            style={{
              position: "relative",
              width: "170px",
              height: "190px",
              border: `2px solid ${isActive ? theme.c(0.65) : theme.c(0.38)}`,
              borderRadius: "16px",
              background: `linear-gradient(180deg, ${theme.c(
                0.11
              )} 0%, ${theme.c(0.04)} 100%)`,
              backdropFilter: "blur(20px)",
              boxShadow: isActive
                ? `0 0 45px ${theme.c(
                    0.4
                  )}, inset 0 1px 0 rgba(255,255,255,0.14)`
                : `0 0 32px ${theme.c(
                    0.2
                  )}, inset 0 1px 0 rgba(255,255,255,0.10)`,
              transition: "all 0.5s ease",
              overflow: "hidden",
            }}
          >
            {(animationPhase === "extracting" || isComplete) && (
              <div
                style={{
                  position: "absolute",
                  top: "50%",
                  left: "50%",
                  transform: "translate(-50%, -50%)",
                  width: "120px",
                  height: "145px",
                  backgroundColor: "rgba(255,255,255,0.10)",
                  border: "1px solid rgba(255,255,255,0.18)",
                  borderRadius: "10px",
                  padding: "14px",
                  backdropFilter: "blur(8px)",
                  boxShadow:
                    "0 8px 24px rgba(0,0,0,0.20), inset 0 1px 0 rgba(255,255,255,0.12)",
                  animation:
                    "hero-ocr-doc-preview-appear 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    marginBottom: "10px",
                    paddingBottom: "8px",
                    borderBottom: `1px solid ${theme.c(0.25)}`,
                  }}
                >
                  <div
                    style={{
                      width: "20px",
                      height: "20px",
                      borderRadius: "6px",
                      background: `linear-gradient(135deg, ${theme.c(
                        0.45
                      )} 0%, ${theme.c2(0.45)} 100%)`,
                      border: `1px solid ${theme.c(0.55)}`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <FileText
                      style={{
                        width: "11px",
                        height: "11px",
                        color: theme.primaryLighter,
                      }}
                    />
                  </div>
                  <div
                    style={{
                      fontSize: "8px",
                      fontWeight: 600,
                      color: `${theme.primaryLighter}cc`,
                      letterSpacing: "0.02em",
                    }}
                  >
                    Invoice.pdf
                  </div>
                </div>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "6px",
                  }}
                >
                  {[
                    { label: "Invoice #", width: 70, delay: 0 },
                    { label: "Date", width: 55, delay: 0.1 },
                    { label: "Vendor", width: 75, delay: 0.2 },
                    { label: "Amount", width: 60, delay: 0.3 },
                  ].map((item, i) => (
                    <div
                      key={i}
                      style={{
                        padding: "5px 7px",
                        backgroundColor: isComplete
                          ? theme.c(0.28)
                          : theme.c(0.2),
                        border: `1px solid ${
                          isComplete ? theme.c(0.55) : theme.c(0.4)
                        }`,
                        borderRadius: "5px",
                        width: `${item.width}%`,
                        animation: `hero-ocr-highlight-pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) ${item.delay}s both`,
                        transition: "all 0.4s ease",
                        boxShadow: isComplete
                          ? `0 0 12px ${theme.c(0.35)}`
                          : "none",
                      }}
                    >
                      <div
                        style={{
                          fontSize: "7px",
                          fontWeight: 600,
                          color: theme.primaryLighter,
                          letterSpacing: "0.03em",
                        }}
                      >
                        {item.label}
                      </div>
                    </div>
                  ))}
                </div>
                {isComplete && (
                  <div
                    style={{
                      position: "absolute",
                      top: "8px",
                      right: "8px",
                      width: "22px",
                      height: "22px",
                      borderRadius: "50%",
                      background: `linear-gradient(135deg, ${theme.primary} 0%, ${theme.secondary} 100%)`,
                      border: "1.5px solid rgba(255,255,255,0.25)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: `0 4px 14px ${theme.c(0.6)}`,
                      animation:
                        "hero-ocr-check-pop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.4s both",
                    }}
                  >
                    <Check
                      style={{
                        width: "12px",
                        height: "12px",
                        color: "#FFFFFF",
                        strokeWidth: 3,
                      }}
                    />
                  </div>
                )}
              </div>
            )}
            {isActive && (
              <>
                <div
                  style={{
                    position: "absolute",
                    top: `${scanProgress}%`,
                    left: "10px",
                    right: "10px",
                    height: "3px",
                    background: `linear-gradient(90deg, transparent 0%, ${theme.c(
                      0.95
                    )} 20%, ${theme.cLight(1)} 50%, ${theme.c(
                      0.95
                    )} 80%, transparent 100%)`,
                    boxShadow: `0 0 26px ${theme.c(0.95)}, 0 0 52px ${theme.c(
                      0.55
                    )}`,
                    transition: "top 0.03s linear",
                  }}
                />
                <div
                  style={{
                    position: "absolute",
                    top: `${scanProgress}%`,
                    left: 0,
                    right: 0,
                    height: "55px",
                    transform: "translateY(-27px)",
                    background: `linear-gradient(180deg, transparent 0%, ${theme.c(
                      0.2
                    )} 50%, transparent 100%)`,
                    pointerEvents: "none",
                  }}
                />
              </>
            )}
            {animationPhase === "scanning" && scanProgress > 25 && (
              <>
                {[
                  { top: 28, width: 58, height: 12 },
                  { top: 44, width: 48, height: 10 },
                  { top: 60, width: 54, height: 11 },
                  { top: 76, width: 50, height: 10 },
                ]
                  .filter((box) => scanProgress > box.top)
                  .map((box, i) => (
                    <div
                      key={i}
                      style={{
                        position: "absolute",
                        left: "18%",
                        top: `${box.top}%`,
                        width: `${box.width}%`,
                        height: `${box.height}%`,
                        backgroundColor: theme.c(0.22),
                        border: `1px solid ${theme.c(0.6)}`,
                        borderRadius: "4px",
                        animation: "hero-ocr-box-flash 0.6s ease-out",
                      }}
                    />
                  ))}
              </>
            )}
            {isActive && (
              <div
                style={{
                  position: "absolute",
                  bottom: "14px",
                  left: "50%",
                  transform: "translateX(-50%)",
                  display: "flex",
                  alignItems: "center",
                  gap: "7px",
                  padding: "5px 12px",
                  backgroundColor: theme.c(0.16),
                  border: `1px solid ${theme.c(0.38)}`,
                  borderRadius: "100px",
                }}
              >
                <div
                  style={{
                    width: "6px",
                    height: "6px",
                    backgroundColor: theme.primaryLight,
                    borderRadius: "50%",
                    boxShadow: `0 0 10px ${theme.cLight(0.85)}`,
                    animation: "hero-ocr-pulse-dot 1s ease-in-out infinite",
                  }}
                />
                <span
                  style={{
                    fontSize: "10px",
                    fontWeight: 600,
                    color: theme.primaryLighter,
                    letterSpacing: "0.04em",
                  }}
                >
                  Analyzing
                </span>
              </div>
            )}
          </div>
        </div>
        <div
          style={{
            position: "absolute",
            right: "-32px",
            top: "50%",
            transform: "translateY(-50%)",
            opacity: animationPhase === "extracting" || isComplete ? 1 : 0.3,
            transition: "opacity 0.6s ease",
            zIndex: 1,
          }}
        >
          <ArrowRight
            style={{
              width: "22px",
              height: "22px",
              color: theme.c(0.65),
              filter: `drop-shadow(0 0 10px ${theme.c(0.45)})`,
            }}
          />
        </div>
      </div>

      {dataParticles.map((particle) => (
        <div
          key={particle.id}
          style={{
            position: "absolute",
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            fontSize: "11px",
            fontWeight: 700,
            color: theme.primaryLight,
            textShadow: `0 0 12px ${theme.cLight(0.9)}`,
            animation:
              "hero-ocr-particle-flow 1.2s cubic-bezier(0.4, 0, 0.2, 1) forwards",
            zIndex: 3,
          }}
        >
          {particle.char}
        </div>
      ))}

      {/* RIGHT: Structured Data */}
      <div
        style={{
          position: "relative",
          width: "250px",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "flex-end",
          zIndex: 1,
        }}
      >
        <div
          style={{
            width: "100%",
            display: "flex",
            flexDirection: "column",
            gap: "11px",
            position: "relative",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: "-36px",
              left: "50%",
              transform: "translateX(-50%)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "6px",
              transition: "all 0.6s ease",
              opacity: extractedFields.length > 0 ? 1 : 0.4,
              zIndex: 20,
            }}
          >
            <div
              style={{
                fontSize: "10px",
                fontWeight: 600,
                color:
                  animationPhase === "extracting" || isComplete
                    ? theme.labelActive
                    : theme.labelBase,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                whiteSpace: "nowrap",
                transition: "all 0.6s ease",
                textShadow:
                  animationPhase === "extracting" || isComplete
                    ? `0 0 16px ${theme.c(0.8)}, 0 0 32px ${theme.c(0.4)}`
                    : "none",
                animation:
                  animationPhase === "extracting" || isComplete
                    ? "hero-ocr-label-glow 2s ease-in-out infinite"
                    : "none",
              }}
            >
              Structured Data
            </div>
            <div
              style={{
                width: "1px",
                height: "14px",
                backgroundColor:
                  animationPhase === "extracting" || isComplete
                    ? theme.c(0.45)
                    : "rgba(148,163,184,0.25)",
                transition: "all 0.6s ease",
              }}
            />
          </div>
          {extractedFields.map((field, index) => (
            <div
              key={field.id}
              style={{
                padding: "12px 15px",
                backgroundColor: isComplete ? theme.c(0.15) : theme.c(0.11),
                border: `1px solid ${
                  isComplete ? theme.c(0.42) : theme.c(0.32)
                }`,
                borderRadius: "11px",
                backdropFilter: "blur(18px)",
                boxShadow: isComplete
                  ? `0 4px 26px ${theme.c(0.3)}, 0 0 0 1px ${theme.c(
                      0.14
                    )}, inset 0 1px 0 rgba(255,255,255,0.10)`
                  : `0 4px 22px ${theme.c(
                      0.22
                    )}, inset 0 1px 0 rgba(255,255,255,0.08)`,
                animation: `hero-ocr-field-pop 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) ${
                  index * 150
                }ms both`,
                transition: "all 0.5s ease",
              }}
            >
              <div
                style={{
                  fontSize: "9px",
                  fontWeight: 600,
                  color: `${theme.primaryLighter}b8`,
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                  marginBottom: "6px",
                  lineHeight: "1.2",
                }}
              >
                {field.label}
              </div>
              <div
                style={{
                  fontSize: "13px",
                  fontWeight: 600,
                  color: "#E2E8F0",
                  letterSpacing: "-0.01em",
                  lineHeight: "1.35",
                }}
              >
                {field.value}
              </div>
            </div>
          ))}
          {isComplete && (
            <div
              style={{
                marginTop: "6px",
                padding: "13px",
                backgroundColor: theme.c(0.09),
                border: `1px solid ${theme.c(0.3)}`,
                borderRadius: "11px",
                backdropFilter: "blur(14px)",
                animation:
                  "hero-ocr-table-slide 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.6s both",
              }}
            >
              <div
                style={{
                  fontSize: "9px",
                  fontWeight: 600,
                  color: `${theme.primaryLighter}b8`,
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                  marginBottom: "9px",
                  lineHeight: "1.2",
                }}
              >
                Formatted Output
              </div>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, 1fr)",
                  gap: "7px",
                }}
              >
                {[...Array(4)].map((_, i) => (
                  <div
                    key={i}
                    style={{
                      height: "28px",
                      backgroundColor: theme.c(0.13),
                      border: `1px solid ${theme.c(0.28)}`,
                      borderRadius: "7px",
                      animation: `hero-ocr-cell-pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) ${
                        0.7 + i * 0.09
                      }s both`,
                    }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
        {isComplete && (
          <div
            style={{
              position: "absolute",
              right: "50%",
              top: "50%",
              transform: "translate(50%, -50%)",
              width: "300px",
              height: "300px",
              background: `radial-gradient(ellipse at center, ${theme.c(
                0.28
              )} 0%, transparent 65%)`,
              filter: "blur(70px)",
              pointerEvents: "none",
              animation: "hero-ocr-glow-pulse 2.2s ease-in-out infinite",
            }}
          />
        )}
      </div>

      {showComplete && (
        <div
          style={{
            position: "absolute",
            bottom: "24px",
            left: "50%",
            transform: "translateX(-50%)",
            display: "flex",
            alignItems: "center",
            gap: "9px",
            padding: "9px 20px",
            backgroundColor: "rgba(20,20,30,0.96)",
            border: `1px solid ${theme.c(0.48)}`,
            borderRadius: "100px",
            backdropFilter: "blur(22px)",
            boxShadow: `0 8px 28px rgba(0,0,0,0.42), 0 0 0 1px ${theme.c(
              0.22
            )}`,
            animation:
              "hero-ocr-badge-appear 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) both",
            zIndex: 10,
          }}
        >
          <div
            style={{
              width: "24px",
              height: "24px",
              borderRadius: "50%",
              background: `linear-gradient(135deg, ${theme.primary} 0%, ${theme.secondary} 100%)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: `0 4px 16px ${theme.c(0.65)}`,
            }}
          >
            <Check
              style={{
                width: "14px",
                height: "14px",
                color: "#FFFFFF",
                strokeWidth: 3,
              }}
            />
          </div>
          <span
            style={{
              fontSize: "13px",
              fontWeight: 600,
              color: "#E2E8F0",
              letterSpacing: "-0.01em",
            }}
          >
            Data Extracted Successfully
          </span>
        </div>
      )}

      <style>{`
        @keyframes hero-ocr-pulse-ring { 0% { transform: translateY(-50%) scale(1); opacity: 0.65; } 100% { transform: translateY(-50%) scale(1.5); opacity: 0; } }
        @keyframes hero-ocr-box-flash { 0% { opacity: 0; transform: scaleX(0.4); } 50% { opacity: 1; transform: scaleX(1); } 100% { opacity: 0.45; transform: scaleX(1); } }
        @keyframes hero-ocr-pulse-dot { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.55; transform: scale(1.45); } }
        @keyframes hero-ocr-particle-flow { 0% { opacity: 0; transform: translate(0, 0) scale(0.5); } 15% { opacity: 1; transform: translate(20%, -5%) scale(1); } 85% { opacity: 1; transform: translate(48%, -8%) scale(1); } 100% { opacity: 0; transform: translate(55%, -10%) scale(0.6); } }
        @keyframes hero-ocr-field-pop { 0% { opacity: 0; transform: translateX(-35px) scale(0.90); } 60% { transform: translateX(6px) scale(1.03); } 100% { opacity: 1; transform: translateX(0) scale(1); } }
        @keyframes hero-ocr-table-slide { 0% { opacity: 0; transform: translateY(18px) scale(0.94); } 100% { opacity: 1; transform: translateY(0) scale(1); } }
        @keyframes hero-ocr-cell-pop { 0% { opacity: 0; transform: scale(0.65); } 70% { transform: scale(1.06); } 100% { opacity: 1; transform: scale(1); } }
        @keyframes hero-ocr-badge-appear { 0% { opacity: 0; transform: translateX(-50%) translateY(18px) scale(0.88); } 100% { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); } }
        @keyframes hero-ocr-glow-pulse { 0%, 100% { opacity: 0.45; } 50% { opacity: 0.65; } }
        @keyframes hero-ocr-label-glow { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.85; transform: scale(1.05); } }
        @keyframes hero-ocr-doc-preview-appear { 0% { opacity: 0; transform: translate(-50%, -50%) scale(0.85); } 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); } }
        @keyframes hero-ocr-highlight-pop { 0% { opacity: 0; transform: scale(0.85); } 100% { opacity: 1; transform: scale(1); } }
        @keyframes hero-ocr-check-pop { 0% { opacity: 0; transform: scale(0.85); } 100% { opacity: 1; transform: scale(1); } }
      `}</style>
    </div>
  );
}
