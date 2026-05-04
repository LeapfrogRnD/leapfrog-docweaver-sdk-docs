import DemoPage from "./demo";
import React, { useEffect, useState } from "react";
import { PrivacyPolicyPage, TermsOfUsePage } from "./demo/components/PolicyPages";
import { ApiIntegrationGuide } from "./demo/IntegrationGuide/IntegrationGuide";
import { McpIntegrationGuide } from "./demo/IntegrationGuide/MCPIntegrationGuide";

export default function App() {
  const [path, setPath] = useState<string>(typeof window !== "undefined" ? window.location.pathname : "/");

  useEffect(() => {
    const handler = () => setPath(window.location.pathname);
    window.addEventListener("popstate", handler);
    return () => window.removeEventListener("popstate", handler);
  }, []);

  const navigateHome = () => {
    window.history.pushState({}, '', '/');
    setPath('/');
  };

  if (path === "/privacy") return <PrivacyPolicyPage />;
  if (path === "/terms") return <TermsOfUsePage />;

  if (path === "/integration-guide")
    return (
      <ApiIntegrationGuide variant="dark" onClose={navigateHome}/>
    );
  if (path === "/mcp-guide")
    return (
      <McpIntegrationGuide variant="dark" onClose={navigateHome}/>
    );
  return <DemoPage />;
}
