import React, { useState, useEffect } from "react";
import {
  FileDown,
  Search,
  Database,
  Zap,
  Layers,
  BrainCircuit,
  Code2,
  Cpu,
  Workflow as WorkflowIcon,
  ShieldCheck,
  ZapIcon,
  Repeat,
  Globe,
} from "lucide-react";
import Link from '@docusaurus/Link';
// Using the brand colors from your custom.css
const DocSections = [
  {
    title: "Quickstart",
    to: "/docs/getting-started/quickstart",
    icon: <Zap className="icon" />,
    description:
      "Get LeapX running in under 5 minutes with our step-by-step guide.",
  },
  {
    title: "Pipeline API",
    to: "/docs/concepts/pipeline-overview",
    icon: <Layers className="icon" />,
    description:
      "Detailed reference for OCR, Parser, and LLM extraction stages.",
  },
  {
    title: "Schema Definitions",
    to: "/docs/concepts/json-schema",
    icon: <BrainCircuit className="icon" />,
    description:
      "Learn how to use Pydantic models to define your extraction targets.",
  },
  {
    title: "Deployment",
    to: "/docs/getting-started/configuration",
    icon: <Cpu className="icon" />,
    description:
      "Production guides for Docker, Kubernetes, and Cloud providers.",
  },
];

const AdvancedCapabilities = [
  {
    title: "Multi-modal Support",
    icon: <Globe className="icon" />,
    description:
      "Process mixed-media documents including handwritten notes, complex charts, and nested tables.",
  },
  {
    title: "Enterprise Security",
    icon: <ShieldCheck className="icon" />,
    description:
      "PII redaction, SOC2 compliance modules, and local-first execution modes.",
  },
  {
    title: "Continuous Learning",
    icon: <Repeat className="icon" />,
    description:
      "Feedback loops that allow the system to learn from human-in-the-loop corrections.",
  },
];

const Integrations = [
  { name: "Pydantic", logo: "Py" },
  { name: "LangChain", logo: "LC" },
  { name: "OpenAI", logo: "AI" },
  { name: "Anthropic", logo: "An" },
  { name: "PostgreSQL", logo: "PS" },
  { name: "AWS S3", logo: "S3" },
];

const WorkflowStep = ({ icon: Icon, label, active }) => (
  <div className={`workflow-step ${active ? "active" : ""}`}>
    <div className={`step-circle ${active ? "active" : ""}`}>
      <Icon className={`step-icon ${active ? "active" : ""}`} />
    </div>
    <span className={`step-label ${active ? "active" : ""}`}>{label}</span>
    {active && <div className="step-glow" />}
  </div>
);

const DocCard = ({ title, icon, description, to = '#' }) => (
  <Link to={to} className="doc-card" aria-label={`Open ${title} documentation`}>
    <div className="doc-card-header">
      <div className="doc-card-icon">{icon}</div>
      <h3 className="doc-card-title">{title}</h3>
    </div>
    <p className="doc-card-desc">{description}</p>
    <div className="doc-card-cta">Read guide →</div>
  </Link>
);

export default function HomepageFeatures() {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 3);
    }, 2500);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="site-root">
      {/* Doc Hero */}
      <section className="hero">
        <div className="container hero-inner">
          <h1 className="hero-title">LeapX Documentation</h1>
          <p className="hero-sub">
            The developer platform for intelligent document understanding. Turn
            messy files into structured JSON in seconds.
          </p>
          <div className="hero-cta">
            <Link
              className="button button--secondary button--lg"
              to="/docs/getting-started/intro"
            >
              Read the Guides
            </Link>
          </div>
        </div>
        <div className="hero-glow" />
      </section>

      {/* Main Content Area */}
      <main className="main-content container">
        {/* Core Sections Grid */}
        <div className="grid core-sections">
          {DocSections.map((section, idx) => (
            <DocCard key={idx} {...section} />
          ))}
        </div>

        {/* Technical Architecture / Workflow */}
        <div className="architecture">
          <div className="architecture-inner">
            <div className="architecture-left">
              <div className="architecture-tag">
                <WorkflowIcon className="tag-icon" /> Core Architecture
              </div>
              <h2 className="architecture-title">The Processing Pipeline</h2>
              <p className="architecture-desc">
                LeapX uses a deterministic pipeline combined with LLM reasoning
                to ensure high-fidelity extraction from any file type.
              </p>
              <div className="architecture-list">
                <div className="architecture-item">
                  <div className="architecture-bullet">
                    <div className="architecture-dot" />
                  </div>
                  <p className="architecture-text">
                    <strong>Parsing:</strong> High-performance text extraction
                    for digital assets.
                  </p>
                </div>
                <div className="architecture-item">
                  <div className="architecture-bullet">
                    <div className="architecture-dot" />
                  </div>
                  <p className="architecture-text">
                    <strong>Inference:</strong> LLM-driven structured output
                    following strict Pydantic constraints.
                  </p>
                </div>
              </div>
            </div>

            <div className="architecture-visual">
              <div className="visual-panel">
                <div className="visual-inner">
                  <div className="visual-line" />
                  <WorkflowStep
                    icon={FileDown}
                    label="Ingest"
                    active={activeStep === 0}
                  />
                  <WorkflowStep
                    icon={Search}
                    label="Parse"
                    active={activeStep === 1}
                  />
                  <WorkflowStep
                    icon={Database}
                    label="Extract"
                    active={activeStep === 2}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Code Snippet & Advanced Capabilities */}
        <div className="grid two-column">
          <div className="code-column">
            <div className="code-header">
              <Code2 className="code-icon" />
              <h2 className="code-title">API Implementation</h2>
            </div>
            <div className="code-panel">
              <div className="code-panel-top">
                <span className="code-filename">main.py</span>
                <span className="code-meta">Py 3.9+</span>
              </div>
              <div className="code-body">
                <pre>
                  <code>
                    {`from leapx import Pipeline
from pydantic import BaseModel

# 1. Define your extraction target
class Identity(BaseModel):
    name: str
    id_number: str

# 2. Initialize the pipeline
lp = Pipeline(model="gemini-1.5-pro")

# 3. Extract structured data
result = lp.extract("passport_scan.jpg", schema=Identity)

print(result.name) # Returns "Jane Doe"`}
                  </code>
                </pre>
              </div>
            </div>
          </div>

          <div className="capabilities-column">
            <h2 className="capabilities-title">
              <ZapIcon className="capabilities-icon" /> Core Capabilities
            </h2>
            <div className="capabilities-list">
              {AdvancedCapabilities.map((cap, i) => (
                <div key={i} className="capability-card">
                  <div className="capability-header">
                    {cap.icon}
                    <h4 className="capability-title-item">{cap.title}</h4>
                  </div>
                  <p className="capability-desc">{cap.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Integrations Section */}
        <div className="integrations">
          <h2 className="integrations-title">Built for the AI Stack</h2>
          <div className="integrations-list">
            {Integrations.map((brand, i) => (
              <div key={i} className="integration-item">
                <div className="integration-logo">{brand.logo}</div>
                <span className="integration-name">{brand.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Community & Support */}
        <div className="support-card">
          <div className="support-inner">
            <h2 className="support-title">Need help building your pipeline?</h2>
            <p className="support-desc">
              Join our developer community to get help with custom schemas,
              share ideas, and stay updated.
            </p>
          </div>
          <div className="support-deco" />
        </div>
      </main>

      {/* Doc Footer */}
      <footer className="site-footer">
        <div className="container footer-inner">
          <div className="footer-grid">
            <div>
              <h4 className="footer-heading">Resources</h4>
              <ul className="footer-list">
                <li>
                  <a href="#" className="footer-link">
                    Guides
                  </a>
                </li>
                <li>
                  <a href="#" className="footer-link">
                    Release Notes
                  </a>
                </li>
                <li>
                  <a href="#" className="footer-link">
                    Troubleshooting
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="footer-heading">Community</h4>
              <ul className="footer-list">
                <li>
                  <a href="#" className="footer-link">
                    Discord Server
                  </a>
                </li>
                <li>
                  <a href="#" className="footer-link">
                    GitHub Issues
                  </a>
                </li>
                <li>
                  <a href="#" className="footer-link">
                    Discussions
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="footer-heading">Legal</h4>
              <ul className="footer-list">
                <li>
                  <a href="#" className="footer-link">
                    MIT License
                  </a>
                </li>
                <li>
                  <a href="#" className="footer-link">
                    Privacy Policy
                  </a>
                </li>
              </ul>
            </div>
            <div className="footer-brand">
              <div className="brand-small">L</div>
              <span className="brand-name">LeapX</span>
              <p className="brand-note">
                Built for the developer community. Documentation v2.4.0
              </p>
            </div>
          </div>
          <div className="footer-bottom">
            © 2024 LeapX Document Intelligence Engine
          </div>
        </div>
      </footer>
    </div>
  );
}
