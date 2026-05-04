import { ZoomIn, ZoomOut, Copy, Check, Loader2, ScanLine } from "lucide-react";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { ProcessingWorkspace } from "../../components/ProcessingWorkspace";
import type { DocumentSample } from "../types";
import React, { useMemo } from "react";
import { Document, Page, pdfjs } from "react-pdf";

pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface ResultsWorkspaceProps {
  selectedDocument: DocumentSample | null;
  isProcessing: boolean;
  previewUrl: string | null;
  previewMime: string | null;
  zoomLevel: number;
  copiedField: string | null;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onCopyField: (key: string, value: string) => void;
}

export function ResultsWorkspace({
  selectedDocument,
  isProcessing,
  previewUrl,
  previewMime,
  zoomLevel,
  copiedField,
  onZoomIn,
  onZoomOut,
  onCopyField,
}: ResultsWorkspaceProps) {
  if (!selectedDocument && !isProcessing && !previewUrl) {
    return (
      <div
        style={{
          height: "100%",
          minHeight: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "rgba(255,255,255,0.025)",
          border: "1px dashed rgba(255,255,255,0.10)",
          borderRadius: "var(--radius-lg, 14px)",
          backdropFilter: "blur(20px)",
          position: "relative",
        }}
      >
        <div
          style={{
            position: "absolute",
            width: "320px",
            height: "200px",
            background:
              "radial-gradient(ellipse at center, rgba(3,142,67,0.07) 0%, transparent 70%)",
            filter: "blur(40px)",
            pointerEvents: "none",
          }}
        />
        <div
          style={{
            width: "52px",
            height: "52px",
            borderRadius: "14px",
            backgroundColor: "rgba(255,255,255,0.05)",
            border: "1px solid rgba(255,255,255,0.09)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: "18px",
            boxShadow: "0 4px 16px rgba(0,0,0,0.30)",
          }}
        >
          <ScanLine
            style={{
              width: "24px",
              height: "24px",
              color: "rgba(148,163,184,0.40)",
            }}
          />
        </div>
        <p
          style={{
            fontWeight: 500,
            fontSize: "15px",
            letterSpacing: "-0.01em",
            marginBottom: "8px",
            color: "rgba(226,232,240,0.55)",
          }}
        >
          Workflow Results will appear here
        </p>
        <p
          style={{
            fontSize: "13px",
            textAlign: "center",
            maxWidth: "260px",
            lineHeight: 1.6,
            color: "rgba(148,163,184,0.35)",
          }}
        >
          Select a workflow or upload a document, then click Run Workflow
          Analysis
        </p>
      </div>
    );
  }

  const [pdfNumPages, setPdfNumPages] = React.useState<number>(0);

  // Reset page count when the PDF source changes
  React.useEffect(() => {
    setPdfNumPages(0);
  }, [
    selectedDocument?.preview,
    previewUrl,
    previewMime,
    selectedDocument?.mimeType,
  ]);

  const pdfScale = useMemo(() => {
    return Math.max(0.25, Math.min(zoomLevel / 100, 3));
  }, [zoomLevel]);

  const renderPdf = (src: string, dimmed?: boolean) => (
    <div
      style={{
        width: "100%",
        height: "100%",
        opacity: dimmed ? 0.45 : 1,
      }}
    >
      <Document
        file={src}
        onLoadSuccess={(p) => setPdfNumPages(p.numPages)}
        onLoadError={() => setPdfNumPages(0)}
        loading={
          <div
            style={{
              padding: "8px",
              color: "rgba(148,163,184,0.75)",
              fontSize: "13px",
            }}
          >
            Loading PDF…
          </div>
        }
        error={
          <div
            style={{
              padding: "8px",
              color: "rgba(148,163,184,0.75)",
              fontSize: "13px",
            }}
          >
            PDF preview failed.{" "}
            <a
              href={src}
              target="_blank"
              rel="noreferrer"
              style={{ color: "#4ADE80", textDecoration: "underline" }}
            >
              Open PDF in a new tab
            </a>
            .
          </div>
        }
        noData={
          <div
            style={{
              padding: "8px",
              color: "rgba(148,163,184,0.75)",
              fontSize: "13px",
            }}
          >
            No PDF selected.
          </div>
        }
      >
        <div
          style={{
            padding: "6px 8px",
            color: "rgba(148,163,184,0.70)",
            fontSize: "12px",
          }}
        >
          {pdfNumPages
            ? `${pdfNumPages} page${pdfNumPages === 1 ? "" : "s"}`
            : ""}
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            padding: "0 8px 8px",
          }}
        >
          {Array.from({ length: pdfNumPages || 0 }, (_, i) => (
            <div
              key={i}
              style={{
                borderRadius: "8px",
                overflow: "hidden",
                backgroundColor: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.08)",
              }}
            >
              <Page
                pageNumber={i + 1}
                scale={pdfScale}
                renderTextLayer={false}
                renderAnnotationLayer={false}
                loading={
                  <div
                    style={{
                      padding: "8px",
                      color: "rgba(148,163,184,0.75)",
                      fontSize: "13px",
                    }}
                  >
                    Rendering page {i + 1}…
                  </div>
                }
              />
            </div>
          ))}
        </div>
      </Document>
    </div>
  );

  return (
    <div
      style={{
        height: "100%",
        minHeight: 0,
        overflow: "hidden",
        animation: "fadeSlideIn 0.32s cubic-bezier(0.4,0,0.2,1)",
      }}
    >
      <ProcessingWorkspace
        variant="dark"
        leftPanel={
          <div
            style={{ display: "flex", flexDirection: "column", height: "100%" }}
          >
            <div className="flex items-center justify-between mb-4 flex-shrink-0">
              <h3
                style={{
                  fontWeight: 600,
                  fontSize: "13px",
                  letterSpacing: "-0.01em",
                  color: "#FFFFFF",
                }}
              >
                Document Preview
              </h3>
              <div
                className="flex items-center rounded-[var(--radius)]"
                style={{
                  backgroundColor: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.08)",
                }}
              >
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onZoomOut}
                  disabled={zoomLevel <= 50 || isProcessing}
                  className="h-4 w-4 p-0 rounded-[calc(var(--radius)-4px)]"
                >
                  <ZoomOut className="h-3 w-3" />
                </Button>
                <span
                  className="w-10 text-center"
                  style={{
                    fontSize: "12px",
                    fontWeight: 500,
                    color: "rgba(148,163,184,0.70)",
                  }}
                >
                  {zoomLevel}%
                </span>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onZoomIn}
                  disabled={zoomLevel >= 200 || isProcessing}
                  className="h-8 w-8 p-0 rounded-[calc(var(--radius)-4px)]"
                >
                  <ZoomIn className="h-3 w-3" />
                </Button>
              </div>
            </div>

            <div
              className="border border-white/10 rounded-[var(--radius)] flex-1 min-h-0 overflow-auto"
              style={{
                backgroundColor: "rgba(0,0,0,0.40)",
                position: "relative",
              }}
            >
              {isProcessing ? (
                <>
                  {previewUrl && (
                    <div
                      style={{ width: "100%", height: "100%", padding: "8px" }}
                    >
                      {previewMime === "application/pdf" ? (
                        renderPdf(previewUrl, true)
                      ) : (
                        <img
                          src={previewUrl}
                          alt="Preview"
                          style={{
                            maxWidth: "100%",
                            maxHeight: "500px",
                            display: "block",
                            margin: "0 auto",
                            borderRadius: "8px",
                            opacity: 0.45,
                          }}
                        />
                      )}
                    </div>
                  )}
                  <div
                    style={{
                      position: previewUrl ? "absolute" : "relative",
                      inset: 0,
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "12px",
                      padding: "16px",
                      pointerEvents: "none",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        padding: "8px 16px",
                        borderRadius: "100px",
                        backgroundColor: "rgba(3,142,67,0.18)",
                        border: "1px solid rgba(74,222,128,0.30)",
                        backdropFilter: "blur(8px)",
                      }}
                    >
                      <Loader2
                        className="animate-spin"
                        style={{
                          width: "14px",
                          height: "14px",
                          color: "#4ADE80",
                        }}
                      />
                      <span
                        style={{
                          color: "#4ADE80",
                          fontSize: "13px",
                          fontWeight: 500,
                        }}
                      >
                        Analysing document…
                      </span>
                    </div>
                  </div>
                </>
              ) : selectedDocument ? (
                <div
                  style={{
                    padding: "8px",
                    height: "100%",
                    transform: `scale(${zoomLevel / 100})`,
                    transformOrigin: "top center",
                  }}
                >
                  {selectedDocument.mimeType ? (
                    selectedDocument.mimeType === "application/pdf" ? (
                      renderPdf(selectedDocument.preview)
                    ) : (
                      <img
                        src={selectedDocument.preview}
                        alt={selectedDocument.name}
                        style={{
                          maxWidth: "100%",
                          maxHeight: "500px",
                          display: "block",
                          margin: "0 auto",
                          borderRadius: "8px",
                        }}
                      />
                    )
                  ) : (
                    (() => {
                      const rawText = (selectedDocument.result as any)?.rawText;
                      if (rawText) {
                        return (
                          <div
                            style={{
                              padding: "16px",
                              height: "100%",
                              minHeight: "300px",
                              overflow: "auto",
                              backgroundColor: "rgba(0,0,0,0.02)",
                              borderRadius: "8px",
                              border: "1px solid rgba(255,255,255,0.04)",
                            }}
                          >
                            <div
                              style={{
                                marginBottom: "12px",
                                color: "rgba(148,163,184,0.70)",
                                fontSize: "13px",
                              }}
                            >
                              {selectedDocument.name}
                            </div>
                            <pre
                              style={{
                                whiteSpace: "pre-wrap",
                                wordBreak: "break-word",
                                fontFamily:
                                  "ui-monospace, SFMono-Regular, Menlo, Monaco, 'Roboto Mono', monospace",
                                fontSize: "13px",
                                lineHeight: 1.45,
                                color: "#e6eef8",
                                margin: 0,
                              }}
                            >
                              {rawText}
                            </pre>
                          </div>
                        );
                      }

                      return (
                        <div
                          style={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "16px",
                            height: "100%",
                            minHeight: "300px",
                            padding: "24px",
                          }}
                        >
                          <div
                            style={{
                              width: "64px",
                              height: "64px",
                              borderRadius: "16px",
                              background:
                                "linear-gradient(135deg, #038E43 0%, #10b981 100%)",
                              boxShadow: "0 6px 20px rgba(3,142,67,0.35)",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              flexShrink: 0,
                            }}
                          >
                            {(() => {
                              const Icon = selectedDocument.icon;
                              return (
                                <Icon
                                  style={{
                                    width: "28px",
                                    height: "28px",
                                    color: "#fff",
                                  }}
                                />
                              );
                            })()}
                          </div>
                          <div style={{ textAlign: "center" }}>
                            <div
                              style={{
                                fontWeight: 600,
                                fontSize: "16px",
                                color: "#FFFFFF",
                                marginBottom: "6px",
                                letterSpacing: "-0.01em",
                              }}
                            >
                              {selectedDocument.name}
                            </div>
                            <div
                              style={{
                                fontSize: "13px",
                                color: "rgba(148,163,184,0.60)",
                              }}
                            >
                              {selectedDocument.type}
                            </div>
                          </div>
                          <div
                            style={{
                              display: "flex",
                              flexDirection: "column",
                              gap: "6px",
                              width: "100%",
                              maxWidth: "280px",
                              marginTop: "8px",
                            }}
                          >
                            {[100, 85, 92, 70, 88, 60, 78].map((w, i) => (
                              <div
                                key={i}
                                style={{
                                  height: "8px",
                                  borderRadius: "4px",
                                  width: `${w}%`,
                                  backgroundColor: "rgba(255,255,255,0.07)",
                                }}
                              />
                            ))}
                          </div>
                        </div>
                      );
                    })()
                  )}
                </div>
              ) : previewUrl ? (
                <div
                  style={{
                    padding: "8px",
                    height: "100%",
                    transform: `scale(${zoomLevel / 100})`,
                    transformOrigin: "top center",
                  }}
                >
                  {previewMime === "application/pdf" ? (
                    renderPdf(previewUrl)
                  ) : (
                    <img
                      src={previewUrl}
                      alt="Preview"
                      style={{
                        maxWidth: "100%",
                        maxHeight: "500px",
                        display: "block",
                        margin: "0 auto",
                        borderRadius: "8px",
                      }}
                    />
                  )}
                </div>
              ) : null}
            </div>
          </div>
        }
        rightPanel={
          <div
            style={{ display: "flex", flexDirection: "column", height: "100%" }}
          >
            <h3
              className="flex-shrink-0"
              style={{
                fontWeight: 600,
                fontSize: "13px",
                letterSpacing: "-0.01em",
                marginBottom: "16px",
                color: "#FFFFFF",
              }}
            >
              Result
            </h3>
            {isProcessing ? (
              <div className="flex-1 min-h-0 overflow-auto">
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "10px",
                  }}
                >
                  <div
                    style={{
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: "var(--radius)",
                      padding: "16px",
                      backgroundColor: "rgba(0,0,0,0.35)",
                      display: "flex",
                      flexDirection: "column",
                      gap: "12px",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <div
                        className="skeleton-shimmer"
                        style={{
                          width: "36%",
                          height: "13px",
                          borderRadius: "5px",
                        }}
                      />
                      <div
                        className="skeleton-shimmer"
                        style={{
                          width: "22%",
                          height: "22px",
                          borderRadius: "100px",
                        }}
                      />
                    </div>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <div
                        className="skeleton-shimmer"
                        style={{
                          width: "30%",
                          height: "13px",
                          borderRadius: "5px",
                        }}
                      />
                      <div
                        className="skeleton-shimmer"
                        style={{
                          width: "18%",
                          height: "13px",
                          borderRadius: "5px",
                        }}
                      />
                    </div>
                  </div>
                  {[
                    ["45%", "70%"],
                    ["38%", "55%"],
                    ["50%", "80%"],
                    ["42%", "60%"],
                    ["48%", "75%"],
                    ["35%", "65%"],
                  ].map(([kw, vw], i) => (
                    <div
                      key={i}
                      style={{
                        border: "1px solid rgba(255,255,255,0.08)",
                        borderRadius: "var(--radius)",
                        padding: "16px",
                        backgroundColor: "rgba(0,0,0,0.30)",
                        display: "flex",
                        flexDirection: "column",
                        gap: "8px",
                      }}
                    >
                      <div
                        className="skeleton-shimmer"
                        style={{
                          width: kw,
                          height: "11px",
                          borderRadius: "5px",
                        }}
                      />
                      <div
                        className="skeleton-shimmer"
                        style={{
                          width: vw,
                          height: "14px",
                          borderRadius: "5px",
                        }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            ) : selectedDocument ? (
              <div className="flex-1 min-h-0 overflow-auto mt-4">
                <div className="space-y-3">
                  <div
                    className="border border-white/10 p-4 rounded-[var(--radius)] hover:border-primary/30 transition-all duration-300"
                    style={{ backgroundColor: "rgba(0,0,0,0.35)" }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span
                        style={{
                          fontWeight: 500,
                          fontSize: "14px",
                          color: "#FFFFFF",
                        }}
                      >
                        Document Type
                      </span>
                      <Badge
                        variant="secondary"
                        className="text-white bg-primary border-0"
                        style={{ fontSize: "13px", fontWeight: 500 }}
                      >
                        {selectedDocument.type}
                      </Badge>
                    </div>
                  </div>
                  {selectedDocument.result.structuredFields.map(
                    (field, index) => (
                      <div
                        key={index}
                        className="border border-white/10 rounded-[var(--radius)] p-4 hover:border-primary/40 transition-all duration-300 group"
                        style={{ backgroundColor: "rgba(0,0,0,0.30)" }}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <div
                              className="mb-1"
                              style={{
                                fontSize: "13px",
                                fontWeight: 500,
                                color: "rgba(148,163,184,0.70)",
                              }}
                            >
                              {field.key}
                            </div>
                            <div
                              className="break-words"
                              style={{
                                fontSize: "15px",
                                fontWeight: 500,
                                letterSpacing: "-0.01em",
                                color: "#FFFFFF",
                              }}
                            >
                              {field.value}
                            </div>
                          </div>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => onCopyField(field.key, field.value)}
                            className="opacity-0 group-hover:opacity-100 transition-all duration-300 flex-shrink-0 h-8 w-8 p-0"
                          >
                            {copiedField === field.key ? (
                              <Check className="h-4 w-4 text-primary" />
                            ) : (
                              <Copy className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            ) : null}
          </div>
        }
      />
    </div>
  );
}
