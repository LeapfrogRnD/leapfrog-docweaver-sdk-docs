import React from "react";
import type { Workflow, DocumentSample } from "../types";
import clsx from "clsx";

interface Props {
  workflow: Workflow;
  selectedDocument: DocumentSample | null;
  uploadedFile: File | null;
  isProcessing: boolean;
  onSelect: (doc: DocumentSample) => void;
}

export default function DocumentPills({
  workflow,
  selectedDocument,
  uploadedFile,
  isProcessing,
  onSelect,
}: Props) {
  return (
    <div className="space-y-3">
      {/* Workflow header */}
      <div className="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wider">
        {workflow.title}
        <div className="flex-1 h-px bg-white/10" />
      </div>

      {/* Document pills */}
      <div className="flex flex-wrap gap-2">
        {workflow.documents.map((doc) => {
          const Icon = doc.icon as React.ComponentType<
            React.SVGProps<SVGSVGElement>
          >;
          const selected = selectedDocument?.id === doc.id && !uploadedFile;

          return (
            <button
              key={doc.id}
              onClick={() => onSelect(doc)}
              disabled={isProcessing}
              className={clsx(
                "flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm transition",
                selected
                  ? "bg-green-600/20 border-green-500 text-green-300 shadow"
                  : "bg-white/5 border-white/10 text-gray-300 hover:bg-white/10 hover:border-white/20",
                isProcessing &&
                  "disabled:opacity-40 disabled:cursor-not-allowed"
              )}
            >
              <div
                className={clsx(
                  "flex items-center justify-center w-4 h-4 rounded",
                  selected
                    ? "bg-green-500/30 text-green-300"
                    : "bg-white/10 text-gray-400"
                )}
              >
                <Icon className="w-3 h-3" />
              </div>

              {doc.type}
            </button>
          );
        })}
      </div>
    </div>
  );
}
