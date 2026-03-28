import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Shield } from "lucide-react";

export default function MailTerminal() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-green-500/20 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => navigate("/")}
            className="p-2 hover:bg-green-500/10 rounded transition"
          >
            <ArrowLeft className="w-6 h-6 text-green-500" />
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 border-2 border-green-500 rounded flex items-center justify-center">
              <Shield className="w-6 h-6 text-green-500" />
            </div>
            <div>
              <div className="text-sm font-bold text-white">NULLPOINT</div>
              <div className="text-xs text-green-500">Mail Terminal</div>
            </div>
          </div>
        </div>
      </header>

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
