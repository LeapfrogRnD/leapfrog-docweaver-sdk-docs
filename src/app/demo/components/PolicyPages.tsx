import React from "react";
import PageHeader from "../../components/PageHeader";
import { ShieldCheck, FileText, FileCode } from "lucide-react";
import { PROJECT_SUBTITLE, PROJECTNAME } from "../../constants/name";
import { Footer } from "./Footer";
import TopBar from "../../components/TopBar";
import mcp from '@/assets/mcp.png';


function BackLink() {
  const goBack = (e: React.MouseEvent) => {
    e.preventDefault();
    if (window.location.pathname !== "/") {
      window.history.pushState({}, "", "/");
      window.dispatchEvent(new PopStateEvent("popstate"));
    }
  };
  return (
    <a
      href="/"
      onClick={goBack}
      className="text-primary hover:underline text-sm"
      style={{ display: "inline-block" }}
    >
      ← Back to demo
    </a>
  );
}

export function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-gray-200 flex flex-col">
      <TopBar
        title={`${PROJECTNAME} - Privacy Policy`}
        subtitle="How this demo handles uploaded files and extracted data"
        variant="dark"
        backLabel="Back to demo"
           externalLinks={[
          {
            href: "/integration-guide",
            label: "Integration Guide",
            icon: <FileCode className="w-3.5 h-3.5" />,
            onClick: (e) => {
              e.preventDefault();
              window.history.pushState({}, "", "/integration-guide");
              window.dispatchEvent(new PopStateEvent("popstate"));
            },
          },
          {
            href: "/mcp-guide",
            label: "MCP Guide",
            icon: <img src={mcp} alt="MCP Guide" className="w-3.5 h-3.5" />,
            onClick: (e) => {
              e.preventDefault();
              window.history.pushState({}, "", "/mcp-guide");
              window.dispatchEvent(new PopStateEvent("popstate"));
            },
          },
        ]}
      />

      <PageHeader
        icon={ShieldCheck}
        title="Privacy Policy"
        description="How this demo handles uploaded files and extracted data"
      />

      <main className="flex-1 max-w-7xl mx-auto px-6 pb-12 pt-8 w-full">

<div className="mb-6">
          <BackLink />
        </div>

        <div className="bg-zinc-900/60 border border-white/10 rounded-lg p-6 text-sm text-gray-300">
          <p className="text-gray-100 mb-4">
            This demo is provided for evaluation and testing purposes only. We
            respect your privacy and describe below how data is handled when you
            use the demo.
          </p>

          <h3 className="text-gray-100 font-medium mt-4 mb-2">
            Data we collect
          </h3>
          <p className="mb-3">
            When you upload a document or use a sample workflow, the demo may
            temporarily process the file to produce OCR results. Uploaded files,
            previews, and extracted text may be transmitted to the demo backend
            or third-party services required to run the OCR pipeline.
          </p>

          <h3 className="text-gray-100 font-medium mt-4 mb-2">
            How we use data
          </h3>
          <p className="mb-3">
            Data is used solely to provide the demonstration: to generate
            previews, run OCR, and display extraction results. The demo does not
            use uploaded data for profiling or advertising.
          </p>

          <h3 className="text-gray-100 font-medium mt-4 mb-2">
            Sharing and retention
          </h3>
          <p className="mb-3">
            Uploaded files or extraction outputs may be sent to services that
            perform OCR or file previewing. For the purposes of this demo, data
            retention is minimal; files and results are retained only as
            required by the demo backend. Do not upload sensitive personal data
            when using the public demo.
          </p>

          <h3 className="text-gray-100 font-medium mt-4 mb-2">Security</h3>
          <p className="mb-3">
            Reasonable measures are taken to protect data in transit and at
            rest, but no demo environment can guarantee end-to-end security.
            Treat this demo as a non-production environment and avoid uploading
            confidential information.
          </p>

          <h3 className="text-gray-100 font-medium mt-4 mb-2">Contact</h3>
          <p>
            For questions about privacy for this demo, contact the demo owner at{" "}
            <a className="text-primary" href="mailto:ai@lftechnology.com">
              ai@lftechnology.com
            </a>{" "}
          </p>
        </div>

      </main>

      <Footer />
    </div>
  );
}

export function TermsOfUsePage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-gray-200 flex flex-col">
      <TopBar
        title={`${PROJECTNAME} - Terms of Use`}
        subtitle="Rules and disclaimers for using the OCR demo"
        variant="dark"
        backLabel="Back to demo"
        externalLinks={[
          {
            href: "/integration-guide",
            label: "Integration Guide",
            icon: <FileCode className="w-3.5 h-3.5" />,
            onClick: (e) => {
              e.preventDefault();
              window.history.pushState({}, "", "/integration-guide");
              window.dispatchEvent(new PopStateEvent("popstate"));
            },
          },
          {
            href: "/mcp-guide",
            label: "MCP Guide",
            icon: <img src={mcp} alt="MCP Guide" className="w-3.5 h-3.5" />,
            onClick: (e) => {
              e.preventDefault();
              window.history.pushState({}, "", "/mcp-guide");
              window.dispatchEvent(new PopStateEvent("popstate"));
            },
          },
        ]}
      />

      <PageHeader
        icon={FileText}
        title="Terms of Use"
        description="Rules and disclaimers for using the OCR demo"
      />

      <main className="flex-1 max-w-7xl mx-auto px-6 pb-12 pt-8 w-full">
<div className="mb-6">
          <BackLink />
        </div>

        <div className="bg-zinc-900/60 border border-white/10 rounded-lg p-6 text-sm text-gray-300">
          <p className="text-gray-100 mb-4">
            By using this demo you agree to use it for evaluation and testing
            purposes only. The demo is provided "as is" without warranties.
          </p>

          <h3 className="text-gray-100 font-medium mt-4 mb-2">Permitted use</h3>
          <p className="mb-3">
            You may interact with the demo to explore OCR features. You may not
            use the demo to upload, transmit, or distribute material that
            violates applicable laws or third-party rights.
          </p>

          <h3 className="text-gray-100 font-medium mt-4 mb-2">
            Intellectual property
          </h3>
          <p className="mb-3">
            All demo UI, sample data, and code are the property of their
            respective owners. The outputs produced by the OCR pipeline are made
            available for your review and evaluation only.
          </p>

          <h3 className="text-gray-100 font-medium mt-4 mb-2">Disclaimer</h3>
          <p className="mb-3">
            The demo is not intended for production use. The demo owner is not
            responsible for any loss or damage resulting from use of the demo or
            its outputs.
          </p>

          <h3 className="text-gray-100 font-medium mt-4 mb-2">Governing law</h3>
          <p>
            These terms are governed by the laws of the owner's jurisdiction as
            applicable. If you have questions about the terms, contact the demo
            owner via the Contact link.
          </p>
        </div>

      </main>

      <Footer />
    </div>
  );
}
