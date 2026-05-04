/**
 * Footer.tsx
 *
 * Simple, clean footer component for demo pages.
 * Uses design system CSS variables for maintainability.
 */

import { Github } from "lucide-react";
import React from "react";
import "./footer.css";
import { PROJECT_SUBTITLE, PROJECTNAME } from "@/app/constants/name";

interface FooterProps {
  onIntegrationGuideClick?: () => void;
}


const ApplicationGuide =
  (import.meta as unknown as { env?: Record<string, string | undefined> }).env
    ?.VITE_APP_GUIDE_URL ?? "https://leapx-marketplace-cf-template.s3.us-east-1.amazonaws.com/Leapfrog+DocWeaver+User+Manual.pdf";

const OnBoardingGuide =
  (import.meta as unknown as { env?: Record<string, string | undefined> }).env
    ?.VITE_ONBOARDING_GUIDE_URL ?? "https://leapx-marketplace-cf-template.s3.us-east-1.amazonaws.com/Leapfrog+DocWeaver+Deployment+Guide.pdf";

    export function Footer({ onIntegrationGuideClick }: FooterProps) {
  const handleLinkClick = (
    e: React.MouseEvent<HTMLAnchorElement>,
    path?: string,
  ) => {
    e.preventDefault();
    if (path) {
      window.history.pushState({}, "", path);
      window.dispatchEvent(new PopStateEvent("popstate"));
    }
  };

  return (
    <footer className="footer-container bg-zinc-950">
      <div className="footer-content">
        <div className="footer-main-row">
          <div className="footer-brand">
            <h3 className="footer-brand-name">{PROJECTNAME}</h3>
            <p className="footer-brand-description">{PROJECT_SUBTITLE}</p>
          </div>

          <nav className="footer-nav">
            <div className="flex gap-8">
              <div className="flex flex-col">
                <a
                  href={ApplicationGuide}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="footer-link"
                >
                  Application Guide
                </a>
                <a
                  href={OnBoardingGuide}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="footer-link"
                >
                  Aws Marketplace Deployment Guide
                </a>
                <a
                  href="/integration-guide"
                  onClick={(e) => handleLinkClick(e, "/integration-guide")}
                  className="footer-link"
                >
                  Integration Guide
                </a>
              </div>
              <div className="flex flex-col">
                <a
                  href="/privacy"
                  onClick={(e) => handleLinkClick(e, "/privacy")}
                  className="footer-link"
                >
                  Privacy Policy
                </a>
                <a
                  href="/terms"
                  onClick={(e) => handleLinkClick(e, "/terms")}
                  className="footer-link"
                >
                  Terms of Use
                </a>
              </div>
            </div>
          </nav>
        </div>

        <div className="footer-bottom-row">
          <p className="footer-copyright w-full text-center">
            Copyright {new Date().getFullYear()}, Leapfrog Technology Inc.
          </p>

          {/* <div className="footer-social">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="footer-social-link"
              aria-label="GitHub"
            >
              <Github className="footer-icon" />
            </a>
          </div> */}
        </div>
      </div>
    </footer>
  );
}
