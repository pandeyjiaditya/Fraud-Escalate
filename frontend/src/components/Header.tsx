import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Shield } from "lucide-react";

export default function Header() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <header className="border-b border-green-500/20 sticky top-0 z-40 bg-black">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-green-500" />
            <span className="font-bold text-lg">NULLPOINT</span>
          </div>
          <div className="flex gap-6 ml-8">
            <button
              onClick={() => navigate("/mail-terminal")}
              className={`transition ${
                location.pathname === "/mail-terminal"
                  ? "text-green-400 border-b-2 border-green-500 pb-1"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Mail
            </button>
            <button
              onClick={() => navigate("/upload-artifacts")}
              className={`transition ${
                location.pathname === "/upload-artifacts"
                  ? "text-green-400 border-b-2 border-green-500 pb-1"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Upload
            </button>
            <button
              onClick={() => navigate("/results-history")}
              className={`transition ${
                location.pathname === "/results-history"
                  ? "text-green-400 border-b-2 border-green-500 pb-1"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Results History
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
