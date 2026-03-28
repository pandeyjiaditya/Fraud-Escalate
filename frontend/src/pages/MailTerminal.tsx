import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";

export default function MailTerminal() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black text-white">
      <Header />

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="bg-black/40 border border-green-500/30 rounded-lg p-8">
          <h1 className="text-3xl font-bold text-white mb-4">Mail Terminal</h1>
          <p className="text-gray-400 mb-6">
            Monitor incoming communications and identify phishing attempts with
            glass-layer heuristics.
          </p>

          <div className="bg-green-500/5 border border-green-500/20 rounded p-4">
            <p className="text-green-400 font-mono text-sm">
              // Gmail integration via n8n workflow (Coming soon)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
