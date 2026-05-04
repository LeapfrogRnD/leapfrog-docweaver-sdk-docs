import { useState, useEffect, useRef } from 'react';
import * as Icons from "lucide-react"
import { 
  Copy, 
  Check, 
  FileCode,
  X, 
  BookOpen, 
  Lock, 
  AlertTriangle, 
  Sparkles,
  ChevronDown,
  ChevronRight,
  History
} from 'lucide-react';
import "@/styles/api-guide.css";
import docContent from "@/app/data/api.json";
import { PROJECTNAME } from '@/app/constants/name';
import { OCR_API_URL } from '@/app/constants/api';
import TopBar from '@/app/components/TopBar';
import { Footer } from "../components/Footer";

interface ApiIntegrationGuideProps {
  variant: 'dark' | 'light';
  onClose: () => void;
}

export function ApiIntegrationGuide({ variant, onClose }: ApiIntegrationGuideProps) {
  const [copiedBlock, setCopiedBlock] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<string>('getting-started');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['overview', 'endpoints', 'reference']));
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const isDark = variant === 'dark';

  const getIcon = (name: string) => {
    const Icon = (Icons as any)[name];
    return Icon || Icons.HelpCircle;
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedBlock(id);
    setTimeout(() => setCopiedBlock(null), 2000);
  };

  const scrollToSection = (sectionId: string) => {
    setActiveSection(sectionId);
    const container = scrollContainerRef.current;
    const element = document.getElementById(sectionId);
    if (container && element) {
      const containerTop = container.getBoundingClientRect().top;
      const elementTop = element.getBoundingClientRect().top;
      const offset = elementTop - containerTop + container.scrollTop - 100;
      container.scrollTo({ top: offset, behavior: 'smooth' });
    }
  };

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => {
      const next = new Set(prev);
      if (next.has(groupId)) {
        next.delete(groupId);
      } else {
        next.add(groupId);
      }
      return next;
    });
  };

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const sections = container.querySelectorAll<HTMLElement>('[data-section]');
      const threshold = container.getBoundingClientRect().top + 140;
      let current = '';
      sections.forEach((section) => {
        if (section.getBoundingClientRect().top <= threshold) {
          current = section.id;
        }
      });
      if (current) setActiveSection(current);
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  const CodeBlock = ({ code, id, language = 'bash' }: { code: string; id: string; language?: string }) => (
    <div className="api-code-block" style={{
      backgroundColor: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)',
      borderColor: isDark ? 'rgba(255,255,255,0.10)' : 'rgba(0,0,0,0.08)',
    }}>
      <button
        onClick={() => handleCopy(code, id)}
        className="api-copy-button"
        style={{
          backgroundColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)',
          borderColor: isDark ? 'rgba(255,255,255,0.10)' : 'rgba(0,0,0,0.08)',
          color: isDark ? 'rgba(226,232,240,0.85)' : '#27272A',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = isDark ? 'rgba(255,255,255,0.10)' : 'rgba(0,0,0,0.07)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)';
        }}
      >
        {copiedBlock === id ? (
          <>
            <Check className="api-icon-sm" />
            Copied
          </>
        ) : (
          <>
            <Copy className="api-icon-sm" />
            Copy
          </>
        )}
      </button>
      <pre className="api-code-pre" style={{ 
        color: isDark ? '#E2E8F0' : '#18181B'
      }}>
        <code>{code}</code>
      </pre>
    </div>
  );

  const InlineCode = ({ children }: { children: string }) => (
    <code className="api-inline-code" style={{
      backgroundColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)',
      borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
      color: isDark ? '#4ADE80' : 'var(--color-brand-600)',
    }}>
      {children}
    </code>
  );

  const SectionHeader = ({ icon: Icon, title, subtitle }: { icon: any; title: string; subtitle?: string }) => (
    <div className="api-section-header">
      <div className="api-section-header-row">
        <div className="api-icon-badge" style={{
          backgroundColor: isDark ? 'rgba(3,142,67,0.12)' : 'rgba(3,142,67,0.08)',
          borderColor: isDark ? 'rgba(74,222,128,0.22)' : 'rgba(3,142,67,0.20)',
        }}>
          <Icon className="api-icon-md" style={{ color: isDark ? '#4ADE80' : 'var(--primary)' }} />
        </div>
        <h2 className="api-section-title" style={{ 
          color: isDark ? '#E2E8F0' : 'var(--color-primary-black)'
        }}>
          {title}
        </h2>
      </div>
      {subtitle && (
        <p className="api-section-subtitle" style={{ 
          color: isDark ? 'rgba(148,163,184,0.55)' : '#71717A'
        }}>
          {subtitle}
        </p>
      )}
    </div>
  );

  const Section = ({ children, id }: { children: React.ReactNode; id: string }) => (
    <div 
      id={id} 
      data-section 
      className="api-section" 
      style={{
        backgroundColor: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(255,255,255,0.70)',
        borderColor: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.06)',
        boxShadow: isDark ? '0 2px 12px rgba(0,0,0,0.25)' : '0 2px 12px rgba(0,0,0,0.04)',
        scrollMarginTop: '100px',
      }}
    >
      {children}
    </div>
  );

  const Table = ({ headers, rows }: { headers: string[]; rows: string[][] }) => (
    <div className="api-table-wrapper" style={{ 
      borderColor: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.06)'
    }}>
      <table className="api-table">
        <thead>
          <tr style={{ backgroundColor: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.02)' }}>
            {headers.map((header, i) => (
              <th key={i} className="api-table-header" style={{
                borderColor: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.06)',
                color: isDark ? '#E2E8F0' : '#18181B',
              }}>
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="api-table-row"
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = isDark ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.01)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}>
              {row.map((cell, j) => (
                <td key={j} className="api-table-cell" style={{
                  borderColor: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.06)',
                  color: j === 0 ? (isDark ? '#E2E8F0' : '#18181B') : (isDark ? 'rgba(148,163,184,0.85)' : '#3F3F46'),
                  borderBottom: i < rows.length - 1 ? `1px solid ${isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.06)'}` : 'none',
                }}>
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
  const sampleErrorResponse = `{
    "error": {
      "code": "UNAUTHORIZED",
      "message": "Invalid or missing API key",
      "request_id": "req_12345",
      "details": null
    }
  }`;
  
    const errorRows = [
      ["400", "Bad Request", "Malformed request or invalid parameters"],
      ["401", "Unauthorized", "Missing or invalid API key"],
      ["403", "Forbidden", "Access denied for this API key or resource"],
      ["404", "Not Found", "Requested resource does not exist"],
      ["409", "Conflict", "Resource already exists or state conflict"],
      ["422", "Unprocessable Entity", "Validation failed for request payload"],
      ["429", "Too Many Requests", "Rate limit exceeded - retry with backoff"],
      ["500", "Internal Server Error", "Unexpected server error"],
      [
        "502/503",
        "Bad Gateway / Service Unavailable",
        "Transient upstream or maintenance - retry later",
      ],
    ];
  const navSections = [
    {
      id: "overview",
      label: "Overview",
      items: [
        { id: "getting-started", label: "Getting Started", icon: Sparkles },
        { id: "authentication", label: "Authentication", icon: Lock },
      ],
    },
    {
      id: "endpoints",
      label: "Endpoints",
      items: docContent.endpoints.map((ep) => ({
        id: ep.id,
        label: ep.title,
        icon: getIcon(ep.icon),
      })),
    },
    {
      id: "reference",
      label: "Reference",
      items: [
        { id: "error-handling", label: "Error Handling", icon: AlertTriangle },
        { id: "changelog", label: "Changelog", icon: History },
      ],
    },
  ];

  return (
    <div ref={scrollContainerRef} className={`api-guide-overlay ${isDark ? 'dark' : ''}`} style={{ 
      background: isDark ? 'var(--color-primary-black)' : 'linear-gradient(135deg, #FAF8F6 0%, #F0FAF4 50%, #F5FFF8 100%)'
    }}>
      {/* Header */}
      <TopBar
        title={`${PROJECTNAME} API Guide`}
        subtitle="Complete documentation for integrating LeapX OCR API"
        variant={variant}
        onClose={onClose}
        externalLinks={[
          {
            href: `${OCR_API_URL}/openapi.json`,
            label: "Open API Docs",
            icon: <FileCode className="w-3 h-3" />,
            external: true
          }
        ]}
      />

      {/* Page Title */}
      <div className="api-page-hero">
        <h1
          className="api-page-hero-title"
          style={{ color: isDark ? '#F1F5F9' : 'var(--color-primary-black)' }}
        >
          API Integration Guide
        </h1>
        <p
          className="api-page-hero-subtitle"
          style={{ color: isDark ? 'rgba(148,163,184,0.70)' : '#52525B' }}
        >
          Complete documentation for integrating LeapX OCR API
        </p>
        <hr
          className="api-page-hero-divider"
          style={{ borderColor: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)' }}
        />
      </div>

      {/* Layout with Sidebar */}
      <div className="api-guide-layout">
        {/* Sidebar Navigation */}
        <aside className="api-guide-sidebar" style={{
          backgroundColor: isDark ? 'rgba(255,255,255,0.02)' : 'rgba(255,255,255,0.50)',
          borderColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
        }}>
          <nav className="api-guide-nav">
            {navSections.map((group) => (
              <div key={group.id} className="api-nav-group">
                <button
                  onClick={() => toggleGroup(group.id)}
                  className="api-nav-group-header"
                  style={{
                    color: isDark ? 'rgba(226,232,240,0.60)' : '#71717A',
                  }}
                >
                  {expandedGroups.has(group.id) ? (
                    <ChevronDown className="api-nav-chevron" />
                  ) : (
                    <ChevronRight className="api-nav-chevron" />
                  )}
                  <span>{group.label}</span>
                </button>
                
                {expandedGroups.has(group.id) && (
                  <div className="api-nav-items">
                    {group.items.map((item) => {
                      const ItemIcon = item.icon;
                      const isActive = activeSection === item.id;
                      return (
                        <button
                          key={item.id}
                          onClick={() => scrollToSection(item.id)}
                          className="api-nav-item"
                          style={{
                            backgroundColor: isActive 
                              ? (isDark ? 'rgba(3,142,67,0.12)' : 'rgba(3,142,67,0.08)')
                              : 'transparent',
                            borderColor: isActive 
                              ? (isDark ? 'rgba(74,222,128,0.25)' : 'rgba(3,142,67,0.22)')
                              : 'transparent',
                            color: isActive 
                              ? (isDark ? '#4ADE80' : 'var(--primary)')
                              : (isDark ? 'rgba(148,163,184,0.70)' : '#52525B'),
                          }}
                        >
                          <ItemIcon className="api-nav-icon" />
                          <span>{item.label}</span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="api-guide-content">
          {/* Getting Started */}
          <Section id="getting-started">
            <SectionHeader
              icon={Sparkles}
              title="Getting Started"
            />
            <p style={{ color: "rgba(148,163,184,0.85)" }}>
              Base URL:{" "}
              <code style={{ color: "#4ADE80" }}><InlineCode>{docContent.baseUrl}</InlineCode></code>
              &nbsp;Replace your with the actual host of your deployment.
            </p>
            {docContent.description && (
              <p style={{ color: "rgba(148,163,184,0.85)", marginTop: 8 }}>
                Information: {docContent.description}
              </p>
            )}
          </Section>

          {/* Authentication */}
          <Section id="authentication">
            <SectionHeader
              icon={Lock}
              title="Authentication"
            />
            
             <div
              className="api-text-content"
              style={{ color: "rgba(148,163,184,0.85)" }}
            >
              <p>
                <strong>Auth scheme:</strong> API key (injected in the API via
                ValidateApiKeyDep).
              </p>
              <p>Typical header (adapt to your implementation):</p>
              <CodeBlock
                id={`auth-example`}
                code={`curl -H "x-api-key: YOUR_API_KEY" "${docContent.baseUrl}/"`}
              />
              <p>All endpoints below require a valid API key.</p>
            </div>
          </Section>

      {/* DYNAMIC SECTIONS FROM JSON */}
      {docContent.endpoints.map((ep) => {
            const Icon = getIcon(ep.icon);
            return (
              <Section key={ep.id} id={ep.id}>
                <SectionHeader
                  icon={Icon}
                  title={ep.title}
                  subtitle={ep.subtitle}
                />
                <div
                  className="api-text-content"
                  style={{ color: "rgba(148,163,184,0.85)" }}
                >
                  <p>
                    <strong>Path:</strong>{" "}
                    <code style={{ color: "#4ADE80" }}>
                      {ep.method} {ep.path}
                    </code>
                  </p>
                  <p>{ep.description}</p>
                  <p
                    className="api-subsection-title"
                    style={{ color: "white" }}
                  >
                    Parameters
                  </p>
                  <Table
                    headers={["Name", "Type", "Description"]}
                    rows={ep.params}
                  />
                  <p
                    className="api-subsection-title"
                    style={{ color: "white" }}
                  >
                    Example Request
                  </p>
                  <CodeBlock id={`${ep.id}-example`} code={ep.exampleRequest} />
                </div>
              </Section>
            );
          })}


          {/* Error Handling */}
          <Section id="error-handling">
            <SectionHeader
              icon={AlertTriangle}
              title="Error Handling"
              subtitle="Understand and handle API errors effectively."
            />
            
            <div
              className="api-text-content"
              style={{ color: "rgba(148,163,184,0.85)" }}
            >
              <p>
                The API uses standard HTTP status codes. Below are common codes
                you may encounter and guidance on how to handle them.
              </p>

              <p className="api-subsection-title" style={{ color: "white" }}>
                Common Error Codes
              </p>
              <Table
                headers={["Code", "Name", "When you get it"]}
                rows={errorRows}
              />

              <p className="api-subsection-title" style={{ color: "white" }}>
                Retry and Idempotency Guidance
              </p>
              <ul style={{ color: "rgba(148,163,184,0.85)" }}>
                <li>
                  Treat 502/503/500 and network timeouts as potentially
                  transient — retry with exponential backoff.
                </li>
                <li>
                  Do not automatically retry 4xx errors
                  (400/401/403/404/422/409) unless you have logic to correct the
                  request.
                </li>
                <li>
                  For non-idempotent operations (POST creating resources),
                  implement client-side idempotency keys where possible to avoid
                  duplicate processing.
                </li>
                <li>
                  Include retries with capped backoff and jitter to avoid
                  thundering herd effects.
                </li>
              </ul>

              <p className="api-subsection-title" style={{ color: "white" }}>
                Debugging
              </p>
              <p style={{ color: "rgba(148,163,184,0.85)" }}>
                Error responses include a request_id when available — provide
                this to support when investigating server-side issues.
              </p>

              <p className="api-subsection-title" style={{ color: "white" }}>
                Sample Error Response
              </p>
              <CodeBlock id={`sample-error`} code={sampleErrorResponse} />
            </div>
          </Section>

          {/* Changelog */}
          <Section id="changelog">
            <SectionHeader
              icon={History}
              title="Changelog"
              subtitle="Recent updates and changes to the API."
            />
            
            <div className="api-text-content" style={{ 
              color: isDark ? 'rgba(148,163,184,0.85)' : '#3F3F46'
            }}>
              <div className="api-changelog-entry">
              <p>
                We follow semantic versioning for API changes. Major versions
                may introduce breaking changes; minor/patch releases are
                backward compatible.
              </p>
                <p className="api-subsection-title" style={{ color: isDark ? '#E2E8F0' : '#18181B' }}>
                  v1.2.0 - March 2026
                </p>
                
                <ul className="api-list">
                <li>
                  v1.2.0 - Added support for additional OCR providers and
                  improved PDF handling.
                </li>
                <li>
                  v1.1.1 - Bugfix: Fixed edge-case with multipart upload
                  parsing.
                </li>
                <li>
                  v1.1.0 - Added integrations endpoint for async processing
                  jobs.
                </li>
                </ul>
                <p style={{ color: "rgba(148,163,184,0.85)" }}>
                Subscribe to release notes or check the README for the full
                history.
              </p>
              </div>
            </div>
          </Section>
        </main>
      </div>
      <Footer />
    </div>
  );
}
