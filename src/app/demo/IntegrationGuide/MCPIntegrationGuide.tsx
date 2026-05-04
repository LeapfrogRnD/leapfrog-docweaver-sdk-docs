import { useState, useEffect, useRef } from 'react';
import * as Icons from 'lucide-react';
import {
  Copy,
  Check,
  X,
  Lock,
  AlertTriangle,
  Sparkles,
  ChevronDown,
  ChevronRight,
  History,
  Wrench,
  Network,
  Server,
  Users,
  BookOpen,
  ShieldCheck,
} from 'lucide-react';
import '@/styles/api-guide.css';
import mcpContent from '@/app/data/mcp.json';
import { PROJECTNAME } from '@/app/constants/name';
import TopBar from '@/app/components/TopBar';
import { Footer } from '../components/Footer';
import architectureDiagram from '@/assets/diagrams/docweaver_architecture_diagram.svg';
import oauthSequenceDiagram from '@/assets/diagrams/docweaver_oauth_sequence_diagram.svg';
import toolLifecycleDiagram from '@/assets/diagrams/docweaver_tool_call_lifecycle.svg';

interface McpIntegrationGuideProps {
  variant: 'dark' | 'light';
  onClose: () => void;
}

export function McpIntegrationGuide({ variant, onClose }: McpIntegrationGuideProps) {
  const [copiedBlock, setCopiedBlock] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<string>('overview');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(
    new Set(['setup', 'connect', 'reference'])
  );
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const isDark = variant === 'dark';

  const getIcon = (name: string) => {
    const Icon = (Icons as Record<string, unknown>)[name];
    return (Icon as React.ElementType) || Icons.HelpCircle;
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
    setExpandedGroups((prev) => {
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

  // ─── Shared sub-components ──────────────────────────────────────────────────

  const CodeBlock = ({
    code,
    id,
  }: {
    code: string;
    id: string;
  }) => (
    <div
      className="api-code-block"
      style={{
        backgroundColor: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)',
        borderColor: isDark ? 'rgba(255,255,255,0.10)' : 'rgba(0,0,0,0.08)',
      }}
    >
      <button
        onClick={() => handleCopy(code, id)}
        className="api-copy-button"
        style={{
          backgroundColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)',
          borderColor: isDark ? 'rgba(255,255,255,0.10)' : 'rgba(0,0,0,0.08)',
          color: isDark ? 'rgba(226,232,240,0.85)' : '#27272A',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = isDark
            ? 'rgba(255,255,255,0.10)'
            : 'rgba(0,0,0,0.07)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = isDark
            ? 'rgba(255,255,255,0.06)'
            : 'rgba(0,0,0,0.04)';
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
      <pre
        className="api-code-pre"
        style={{ color: isDark ? '#E2E8F0' : '#18181B' }}
      >
        <code>{code}</code>
      </pre>
    </div>
  );

  const InlineCode = ({ children }: { children: string }) => (
    <code
      className="api-inline-code"
      style={{
        backgroundColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)',
        borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
        color: isDark ? '#4ADE80' : 'var(--color-brand-600)',
      }}
    >
      {children}
    </code>
  );

  const SectionHeader = ({
    icon: Icon,
    title,
    subtitle,
  }: {
    icon: React.ElementType;
    title: string;
    subtitle?: string;
  }) => (
    <div className="api-section-header">
      <div className="api-section-header-row">
        <div
          className="api-icon-badge"
          style={{
            backgroundColor: isDark
              ? 'rgba(3,142,67,0.12)'
              : 'rgba(3,142,67,0.08)',
            borderColor: isDark
              ? 'rgba(74,222,128,0.22)'
              : 'rgba(3,142,67,0.20)',
          }}
        >
          <Icon
            className="api-icon-md"
            style={{ color: isDark ? '#4ADE80' : 'var(--primary)' }}
          />
        </div>
        <h2
          className="api-section-title"
          style={{ color: isDark ? '#E2E8F0' : 'var(--color-primary-black)' }}
        >
          {title}
        </h2>
      </div>
      {subtitle && (
        <p
          className="api-section-subtitle"
          style={{
            color: isDark ? 'rgba(148,163,184,0.55)' : '#71717A',
          }}
        >
          {subtitle}
        </p>
      )}
    </div>
  );

  const Section = ({
    children,
    id,
  }: {
    children: React.ReactNode;
    id: string;
  }) => (
    <div
      id={id}
      data-section
      className="api-section"
      style={{
        backgroundColor: isDark
          ? 'rgba(255,255,255,0.03)'
          : 'rgba(255,255,255,0.70)',
        borderColor: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.06)',
        boxShadow: isDark
          ? '0 2px 12px rgba(0,0,0,0.25)'
          : '0 2px 12px rgba(0,0,0,0.04)',
        scrollMarginTop: '100px',
      }}
    >
      {children}
    </div>
  );

  const Table = ({
    headers,
    rows,
  }: {
    headers: string[];
    rows: string[][];
  }) => (
    <div
      className="api-table-wrapper"
      style={{
        borderColor: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.06)',
      }}
    >
      <table className="api-table">
        <thead>
          <tr
            style={{
              backgroundColor: isDark
                ? 'rgba(255,255,255,0.04)'
                : 'rgba(0,0,0,0.02)',
            }}
          >
            {headers.map((header, i) => (
              <th
                key={i}
                className="api-table-header"
                style={{
                  borderColor: isDark
                    ? 'rgba(255,255,255,0.07)'
                    : 'rgba(0,0,0,0.06)',
                  color: isDark ? '#E2E8F0' : '#18181B',
                }}
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              className="api-table-row"
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = isDark
                  ? 'rgba(255,255,255,0.02)'
                  : 'rgba(0,0,0,0.01)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              {row.map((cell, j) => (
                <td
                  key={j}
                  className="api-table-cell"
                  style={{
                    borderColor: isDark
                      ? 'rgba(255,255,255,0.07)'
                      : 'rgba(0,0,0,0.06)',
                    color:
                      j === 0
                        ? isDark
                          ? '#E2E8F0'
                          : '#18181B'
                        : isDark
                        ? 'rgba(148,163,184,0.85)'
                        : '#3F3F46',
                    borderBottom:
                      i < rows.length - 1
                        ? `1px solid ${
                            isDark
                              ? 'rgba(255,255,255,0.07)'
                              : 'rgba(0,0,0,0.06)'
                          }`
                        : 'none',
                  }}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  // ─── Nav structure ───────────────────────────────────────────────────────────

  const navSections = [
    {
      id: 'setup',
      label: 'Setup',
      items: [
        { id: 'overview', label: 'Overview', icon: Sparkles },
        { id: 'authentication', label: 'Authentication', icon: Lock },
        { id: 'backend-setup', label: 'Backend Setup', icon: Server },
        { id: 'mcp-server', label: 'MCP Server', icon: Network },
      ],
    },
    {
      id: 'connect',
      label: 'Connect',
      items: mcpContent.clients.map((c) => ({
        id: `client-${c.id}`,
        label: c.name,
        icon: getIcon(c.icon),
      })),
    },
    {
      id: 'reference',
      label: 'Reference',
      items: [
        { id: 'oauth-flow', label: 'OAuth 2.0 Full Flow', icon: ShieldCheck },
        { id: 'tools', label: 'Available Tools', icon: Wrench },
        { id: 'tool-lifecycle', label: 'Tool Lifecycle', icon: BookOpen },
        { id: 'troubleshooting', label: 'Troubleshooting', icon: AlertTriangle },
        { id: 'changelog', label: 'Changelog', icon: History },
      ],
    },
  ];

  const textColor = isDark ? 'rgba(148,163,184,0.85)' : '#3F3F46';
  const headingColor = isDark ? '#E2E8F0' : '#18181B';

  // ─── Render ──────────────────────────────────────────────────────────────────

  return (
    <div
      ref={scrollContainerRef}
      className={`api-guide-overlay ${isDark ? 'dark' : ''}`}
      style={{
        background: isDark
          ? 'var(--color-primary-black)'
          : 'linear-gradient(135deg, #FAF8F6 0%, #F0FAF4 50%, #F5FFF8 100%)',
      }}
    >
      {/* Header */}
      <TopBar
        title={`${PROJECTNAME} MCP Guide`}
        subtitle="End-to-end integration guide for the Model Context Protocol server"
        variant={variant}
        onClose={onClose}
      />

      {/* Page Title */}
      <div className="api-page-hero">
        <h1
          className="api-page-hero-title"
          style={{ color: isDark ? '#F1F5F9' : 'var(--color-primary-black)' }}
        >
          MCP Integration Guide
        </h1>
        <p
          className="api-page-hero-subtitle"
          style={{ color: isDark ? 'rgba(148,163,184,0.70)' : '#52525B' }}
        >
          End-to-end integration guide for the Model Context Protocol server
        </p>
        <hr
          className="api-page-hero-divider"
          style={{ borderColor: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)' }}
        />
      </div>

      {/* Layout */}
      <div className="api-guide-layout">
        {/* Sidebar */}
        <aside
          className="api-guide-sidebar"
          style={{
            backgroundColor: isDark
              ? 'rgba(255,255,255,0.02)'
              : 'rgba(255,255,255,0.50)',
            borderColor: isDark
              ? 'rgba(255,255,255,0.06)'
              : 'rgba(0,0,0,0.06)',
          }}
        >
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
                              ? isDark
                                ? 'rgba(3,142,67,0.12)'
                                : 'rgba(3,142,67,0.08)'
                              : 'transparent',
                            borderColor: isActive
                              ? isDark
                                ? 'rgba(74,222,128,0.25)'
                                : 'rgba(3,142,67,0.22)'
                              : 'transparent',
                            color: isActive
                              ? isDark
                                ? '#4ADE80'
                                : 'var(--primary)'
                              : isDark
                              ? 'rgba(148,163,184,0.70)'
                              : '#52525B',
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

          {/* Overview */}
          <Section id="overview">
            <SectionHeader
              icon={Sparkles}
              title="Overview"
              subtitle={mcpContent.description}
            />
            <div className="api-text-content" style={{ color: textColor }}>
              <p>{mcpContent.architecture.summary}</p>
              <p className="api-subsection-title" style={{ color: headingColor }}>
                Architecture
              </p>
              <img
                src={architectureDiagram}
                alt="DocWeaver architecture diagram"
                style={{ width: '80%', borderRadius: 8, display: 'block', margin: '0 auto' }}
              />
              <p style={{ marginTop: 12 }}>
                The MCP server is a <strong>thin bridge</strong>: it receives tool
                calls from AI clients, translates them into backend API requests
                (workflow creation + job polling), and streams results back.
              </p>
              <p style={{ marginTop: 8 }}>
                MCP endpoint:{' '}
                <InlineCode>{mcpContent.mcpEndpoint}</InlineCode>
              </p>
            </div>
          </Section>

          {/* Authentication */}
          <Section id="authentication">
            <SectionHeader
              icon={Lock}
              title="Authentication"
              subtitle="Choose the auth strategy that fits your use case."
            />
            <div className="api-text-content" style={{ color: textColor }}>
              <Table
                headers={['Mode', 'Use Case', 'Setup Complexity']}
                rows={mcpContent.authModes.map((a) => [
                  a.mode,
                  a.useCase,
                  a.complexity,
                ])}
              />
              <p style={{ marginTop: 12 }}>
                For production end-user clients (Claude, Cursor, VS Code), use{' '}
                <InlineCode>oauth2</InlineCode>. For local dev or CI pipelines,{' '}
                <InlineCode>static</InlineCode> is the fastest path.
              </p>
            </div>
          </Section>

          {/* Backend Setup */}
          <Section id="backend-setup">
            <SectionHeader
              icon={Server}
              title="Backend Setup"
              subtitle="Prepare the DocWeaver backend before starting the MCP server."
            />
            <div className="api-text-content" style={{ color: textColor }}>
              <p className="api-subsection-title" style={{ color: headingColor }}>
                Obtain an API Key
              </p>
              <p>
                Every request from the MCP server to the backend carries an{' '}
                <InlineCode>X-API-Key</InlineCode> header. Obtain this from your
                backend administrator or generate one in the admin UI.
              </p>

              <p className="api-subsection-title" style={{ color: headingColor }}>
                Dynamic OAuth Client Registration (RFC 7591)
              </p>
              <CodeBlock
                code={mcpContent.oauthRegistration.dynamicRegistration}
                id="oauth-register"
              />
              <p className="api-subsection-title" style={{ color: headingColor }}>
                Registration Response
              </p>
              <CodeBlock
                code={mcpContent.oauthRegistration.registrationResponse}
                id="oauth-register-response"
              />
              <p style={{ marginTop: 8 }}>
                Save the <InlineCode>client_id</InlineCode>. DocWeaver uses public
                clients secured by PKCE (RFC 7636).
              </p>

              <p className="api-subsection-title" style={{ color: headingColor }}>
                Admin Client Management
              </p>
              <Table
                headers={['Action', 'Request']}
                rows={mcpContent.oauthRegistration.adminActions}
              />
            </div>
          </Section>

          {/* MCP Server */}
          <Section id="mcp-server">
            <SectionHeader
              icon={Network}
              title="MCP Server Configuration"
              subtitle="Install, configure, and start the MCP server."
            />
            <div className="api-text-content" style={{ color: textColor }}>
              <p className="api-subsection-title" style={{ color: headingColor }}>
                Install &amp; Start
              </p>
              <CodeBlock code={mcpContent.installation} id="install" />

              <p className="api-subsection-title" style={{ color: headingColor }}>
                Environment Variables (.env)
              </p>
              <CodeBlock code={mcpContent.envConfig} id="env-config" />
            </div>
          </Section>

          {/* Client Configs — dynamic from data */}
          {mcpContent.clients.map((client) => {
            const ClientIcon = getIcon(client.icon);
            return (
              <Section key={client.id} id={`client-${client.id}`}>
                <SectionHeader
                  icon={ClientIcon}
                  title={client.name}
                  subtitle={client.description}
                />
                <div className="api-text-content" style={{ color: textColor }}>
                  <CodeBlock
                    code={client.config}
                    id={`client-config-${client.id}`}
                  />
                  {client.note && (
                    <p style={{ marginTop: 8 }}>{client.note}</p>
                  )}
                </div>
              </Section>
            );
          })}

          {/* OAuth 2.0 Full Flow */}
          <Section id="oauth-flow">
            <SectionHeader
              icon={ShieldCheck}
              title="OAuth 2.0 Full Flow (End-User Login)"
              subtitle={mcpContent.oauthFlow.description}
            />
            <div className="api-text-content" style={{ color: textColor }}>
              <img
                src={oauthSequenceDiagram}
                alt="OAuth 2.0 sequence diagram"
                style={{ width: '100%', borderRadius: 8, marginTop: 8 }}
              />
              <p className="api-subsection-title" style={{ color: headingColor, marginTop: 16 }}>
                Key Points
              </p>
              <ul className="api-list">
                {mcpContent.oauthFlow.keyPoints.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>
          </Section>

          {/* Available Tools */}
          <Section id="tools">
            <SectionHeader
              icon={Wrench}
              title="Available Tools"
              subtitle="Tools exposed by the MCP server to AI clients."
            />
            <div className="api-text-content" style={{ color: textColor }}>
              <Table
                headers={['Tool', 'What it does', 'Needs a document?']}
                rows={mcpContent.tools}
              />
              <p style={{ marginTop: 12 }}>
                <strong>Recommended starting sequence:</strong>{' '}
                <InlineCode>get_configs</InlineCode> → pick providers → call a
                processing tool → <InlineCode>check_job_status</InlineCode> if the
                job is still running.
              </p>
              <p style={{ marginTop: 8 }}>
                Documents can be supplied as <InlineCode>base64_data</InlineCode>{' '}
                (files in memory) or <InlineCode>s3_url</InlineCode> (e.g.{' '}
                <InlineCode>s3://my-bucket/docs/invoice.pdf</InlineCode>).
              </p>
            </div>
          </Section>

          {/* Tool Lifecycle */}
          <Section id="tool-lifecycle">
            <SectionHeader
              icon={BookOpen}
              title="Tool Lifecycle"
              subtitle="What happens internally when an AI client calls a tool."
            />
            <div className="api-text-content" style={{ color: textColor }}>
              <img
                src={toolLifecycleDiagram}
                alt="Tool call lifecycle diagram"
                style={{ width: '75%', borderRadius: 8, display: 'block', margin: '0 auto' }}
              />
            </div>
          </Section>

          {/* Troubleshooting */}
          <Section id="troubleshooting">
            <SectionHeader
              icon={AlertTriangle}
              title="Troubleshooting"
              subtitle="Common symptoms, causes, and fixes."
            />
            <div className="api-text-content" style={{ color: textColor }}>
              <Table
                headers={['Symptom', 'Likely Cause', 'Fix']}
                rows={mcpContent.troubleshooting}
              />
            </div>
          </Section>

          {/* Changelog */}
          <Section id="changelog">
            <SectionHeader
              icon={History}
              title="Changelog"
              subtitle="MCP server release history."
            />
            <div className="api-text-content" style={{ color: textColor }}>
              {mcpContent.changelog.map((entry) => (
                <div key={entry.version} className="api-changelog-entry">
                  <p
                    className="api-subsection-title"
                    style={{ color: headingColor }}
                  >
                    {entry.version} — {entry.date}
                  </p>
                  <ul className="api-list">
                    {entry.changes.map((change, i) => (
                      <li key={i}>{change}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </Section>

        </main>
      </div>
      <Footer />
    </div>
  );
}
