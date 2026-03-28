import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, Shield, AlertCircle, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import {
  getRiskColor,
  getRiskLevel,
  AnalysisResponse,
} from "../services/analysisService";

export default function ResultsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const result = location.state?.result as AnalysisResponse | undefined;

  if (!result) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">No Results Found</h1>
          <button
            onClick={() => navigate("/upload-artifacts")}
            className="text-green-500 hover:text-green-400"
          >
            ← Back to Upload
          </button>
        </div>
      </div>
    );
  }

  const riskScore = result.final.risk_score;
  const decision = result.final.decision;
  const reasoning = result.final.reasoning;

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-green-500/20 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => navigate("/upload-artifacts")}
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
              <div className="text-xs text-green-500">Analysis Results</div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Risk Score Card */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="bg-black/40 border border-green-500/30 rounded-lg p-8">
            <div className="grid md:grid-cols-3 gap-8">
              {/* Risk Score */}
              <div className="text-center">
                <p className="text-gray-400 text-sm mb-4">RISK SCORE</p>
                <div
                  className={`text-6xl font-black ${getRiskColor(riskScore)}`}
                >
                  {riskScore.toFixed(1)}
                </div>
                <p className="text-gray-400 text-xs mt-2">/100</p>
              </div>

              {/* Risk Level */}
              <div className="text-center">
                <p className="text-gray-400 text-sm mb-4">RISK LEVEL</p>
                <div
                  className={`text-4xl font-black ${getRiskColor(riskScore)}`}
                >
                  {getRiskLevel(riskScore)}
                </div>
                {riskScore >= 70 && (
                  <AlertCircle
                    className={`w-8 h-8 mx-auto mt-4 ${getRiskColor(riskScore)}`}
                  />
                )}
                {riskScore < 40 && (
                  <CheckCircle2
                    className={`w-8 h-8 mx-auto mt-4 ${getRiskColor(riskScore)}`}
                  />
                )}
              </div>

              {/* Decision */}
              <div className="text-center">
                <p className="text-gray-400 text-sm mb-4">DECISION</p>
                <div className="text-2xl font-bold text-white">{decision}</div>
                <p className="text-gray-400 text-xs mt-2">
                  {decision === "SAFE" ? "✓ Approved" : "⚠ Review Required"}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Reasoning */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h2 className="text-xl font-bold text-white mb-4">
            Analysis Summary
          </h2>
          <div className="bg-black/40 border border-green-500/20 rounded-lg p-6">
            <p className="text-gray-300 leading-relaxed">{reasoning}</p>
          </div>
        </motion.div>

        {/* Layer Breakdown */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-xl font-bold text-white mb-4">Layer Analysis</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {/* Layer 0 */}
            <div className="bg-black/40 border border-green-500/20 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                Layer 0 - Privacy
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <p className="text-gray-400">Clean Text Confidence:</p>
                  <p className="text-white">
                    {(result.layer0?.clean_text_confidence || 0).toFixed(2)}
                  </p>
                </div>
                <div className="flex justify-between">
                  <p className="text-gray-400">Words Analyzed:</p>
                  <p className="text-white">{result.layer0?.word_count || 0}</p>
                </div>
              </div>
            </div>

            {/* Layer 1 */}
            <div className="bg-black/40 border border-green-500/20 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                Layer 1 - Heuristics
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <p className="text-gray-400">Heuristic Score:</p>
                  <p className="text-white">
                    {result.layer1?.heuristic_score || 0} / 150
                  </p>
                </div>
                <div className="flex justify-between">
                  <p className="text-gray-400">Flags Detected:</p>
                  <p className="text-white">
                    {result.layer1?.flags?.length || 0}
                  </p>
                </div>
              </div>
            </div>

            {/* Layer 2 */}
            <div className="bg-black/40 border border-green-500/20 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                Layer 2 - ML Model
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <p className="text-gray-400">ML Score:</p>
                  <p className="text-white">
                    {result.layer2?.ml_text_score?.toFixed(1) || 0} / 100
                  </p>
                </div>
                <div className="flex justify-between">
                  <p className="text-gray-400">Confidence:</p>
                  <p className="text-white">
                    {(result.layer2?.ml_text_confidence || 0).toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            {/* Layer 3 */}
            <div className="bg-black/40 border border-green-500/20 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                Layer 3 - LLM Scoring
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <p className="text-gray-400">LLM Score:</p>
                  <p className="text-white">
                    {result.layer3_scoring?.llm_score?.toFixed(1) || 0} / 100
                  </p>
                </div>
                <div className="flex justify-between">
                  <p className="text-gray-400">Confidence:</p>
                  <p className="text-white">
                    {(result.layer3_scoring?.llm_confidence || 0).toFixed(2)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Input Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-xl font-bold text-white mb-4">
            Input Information
          </h2>
          <div className="bg-black/40 border border-green-500/20 rounded-lg p-6">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p className="text-gray-400 text-sm mb-1">Input Type</p>
                <p className="text-white">{result.input?.type || "Unknown"}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Timestamp</p>
                <p className="text-white">
                  {result.input?.metadata?.timestamp || "N/A"}
                </p>
              </div>
              <div className="col-span-2">
                <p className="text-gray-400 text-sm mb-1">Content Preview</p>
                <p className="text-gray-300 text-sm line-clamp-3">
                  {result.input?.content?.substring(0, 300) || "N/A"}...
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
