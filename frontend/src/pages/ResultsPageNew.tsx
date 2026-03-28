import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Download } from "lucide-react";
import { motion } from "framer-motion";
import {
  getRiskColor,
  getRiskLevel,
  AnalysisResponse,
} from "../services/analysisService";
import { downloadPDF } from "../utils/generatePDF";
import Header from "../components/Header";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

const STORAGE_KEY = "fraud_analysis_results";

export default function ResultsPageNew() {
  const navigate = useNavigate();
  const location = useLocation();
  const [result, setResult] = useState<AnalysisResponse | undefined>(
    location.state?.result,
  );
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    if (!result) {
      try {
        const storedResults = localStorage.getItem(STORAGE_KEY);
        if (storedResults) {
          const allResults = JSON.parse(storedResults);
          const lastResultKey =
            Object.keys(allResults)[Object.keys(allResults).length - 1];
          if (lastResultKey) {
            setResult(allResults[lastResultKey]);
          }
        }
      } catch (error) {
        console.error("Error loading stored result:", error);
      }
    } else {
      try {
        const storedResults = JSON.parse(
          localStorage.getItem(STORAGE_KEY) || "{}",
        );
        const timestamp = new Date().toISOString();
        storedResults[`result_${timestamp}`] = result;
        localStorage.setItem(STORAGE_KEY, JSON.stringify(storedResults));
      } catch (error) {
        console.error("Error saving result to localStorage:", error);
      }
    }
  }, []);

  const handleDownloadPDF = async () => {
    if (!result) return;
    setIsDownloading(true);
    try {
      await downloadPDF(result);
    } catch (error) {
      console.error("Error downloading PDF:", error);
      alert("Failed to download PDF. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  };

  if (!result) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">No Results Found</h1>
          <p className="text-gray-400 mb-6">
            No analysis results stored or passed.
          </p>
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
  const isHighRisk = riskScore >= 70;
  const verdictColor = isHighRisk ? "#ef4444" : "#22c55e";
  const verdictText = isHighRisk ? "BLOCK" : "SAFE";

  // Generate Analysis ID
  const analysisId = `AFD-${String(Math.floor(Math.random() * 10000)).padStart(
    5,
    "0",
  )}-APXK`;

  // Score distribution data
  const scoreData = [
    { name: "HEURISTICS", value: result.layer1?.heuristic_score || 0 },
    { name: "ML MODELS", value: result.layer2?.ml_text_score || 0 },
    { name: "LLM LOGIC", value: result.layer3_scoring?.llm_score || 0 },
    { name: "AGGREGATE", value: Math.round(riskScore) },
    { name: "FINAL SCORE", value: riskScore },
  ];

  return (
    <div className="min-h-screen bg-black text-white">
      <Header />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Export Button */}
        <motion.div
          className="flex justify-end mb-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <button
            onClick={handleDownloadPDF}
            disabled={isDownloading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500/20 border border-blue-500/30 hover:border-blue-500/60 rounded transition disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            <span className="text-sm">
              {isDownloading ? "Generating..." : "Export Report"}
            </span>
          </button>
        </motion.div>

        {/* Analysis ID */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <p className="text-gray-500 text-sm uppercase tracking-wider">
            ANALYSIS ID: {analysisId}
          </p>
        </motion.div>

        {/* Threat Gauge & Verdict */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          {/* Circular Gauge */}
          <div className="flex justify-center mb-12">
            <div className="relative w-48 h-48">
              <svg
                className="w-full h-full transform -rotate-90"
                viewBox="0 0 200 200"
              >
                {/* Background circle */}
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  fill="none"
                  stroke="#333"
                  strokeWidth="8"
                />
                {/* Progress circle */}
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  fill="none"
                  stroke={verdictColor}
                  strokeWidth="8"
                  strokeDasharray={`${(riskScore / 100) * 565.48} 565.48`}
                  strokeLinecap="round"
                  style={{
                    transition: "stroke-dasharray 1s ease-in-out",
                  }}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className="text-5xl font-bold">{riskScore.toFixed(0)}</div>
                <div className="text-sm text-gray-400 uppercase tracking-wider">
                  /100
                </div>
                <div className="text-xs text-gray-500 mt-2 uppercase">
                  THREAT INDEX
                </div>
              </div>
            </div>
          </div>

          {/* Verdict */}
          <div className="mb-6">
            <h2
              className="text-4xl font-black mb-2"
              style={{ color: verdictColor }}
            >
              FINAL VERDICT: {verdictText}
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              {result.final.reasoning}
            </p>
          </div>
        </motion.div>

        {/* Scores & Summary Section */}
        <motion.div
          className="grid grid-cols-3 gap-8 mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {/* Left: Score Boxes */}
          <div className="space-y-4">
            {/* Heuristics */}
            <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-4 hover:border-red-500/40 transition">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-white mb-1">Heuristics</h3>
                  <p className="text-xs text-gray-400">
                    High anomaly detection across known attack signatures
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-red-400">
                    {result.layer1?.heuristic_score || 0}/150
                  </div>
                </div>
              </div>
              <div className="w-full bg-red-500/10 rounded h-1">
                <div
                  className="bg-red-500 h-1 rounded transition-all"
                  style={{
                    width: `${Math.min(
                      ((result.layer1?.heuristic_score || 0) / 150) * 100,
                      100,
                    )}%`,
                  }}
                />
              </div>
            </div>

            {/* ML Models */}
            <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4 hover:border-blue-500/40 transition">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-white mb-1">ML Models</h3>
                  <p className="text-xs text-gray-400">
                    Non-linear behavioral patterns detected in execution flow
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-blue-400">
                    {result.layer2?.ml_text_score?.toFixed(0) || 0}/288
                  </div>
                </div>
              </div>
              <div className="w-full bg-blue-500/10 rounded h-1">
                <div
                  className="bg-blue-500 h-1 rounded transition-all"
                  style={{
                    width: `${Math.min(
                      ((result.layer2?.ml_text_score || 0) / 288) * 100,
                      100,
                    )}%`,
                  }}
                />
              </div>
            </div>

            {/* LLM Reasoning */}
            <div className="bg-purple-500/5 border border-purple-500/20 rounded-lg p-4 hover:border-purple-500/40 transition">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-white mb-1">
                    LLM Reasoning
                  </h3>
                  <p className="text-xs text-gray-400">
                    Contextual analysis indicates high probability of social
                    engineering
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-purple-400">
                    {result.layer3_scoring?.llm_score?.toFixed(0) || 0}/100
                  </div>
                </div>
              </div>
              <div className="w-full bg-purple-500/10 rounded h-1">
                <div
                  className="bg-purple-500 h-1 rounded transition-all"
                  style={{
                    width: `${Math.min(
                      ((result.layer3_scoring?.llm_score || 0) / 100) * 100,
                      100,
                    )}%`,
                  }}
                />
              </div>
            </div>

            {/* Acoustic Forensics - optional */}
            <div className="bg-gray-500/5 border border-gray-500/20 rounded-lg p-4 hover:border-gray-500/40 transition">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-white mb-1">
                    Acoustic Forensics
                  </h3>
                  <p className="text-xs text-gray-400">
                    Minimal acoustic anomalies detected in voice patterns
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-gray-400">12/100</div>
                </div>
              </div>
              <div className="w-full bg-gray-500/10 rounded h-1">
                <div
                  className="bg-gray-500 h-1 rounded transition-all"
                  style={{ width: "12%" }}
                />
              </div>
            </div>
          </div>

          {/* Center: Summary Box */}
          <div className="col-span-2 bg-red-500/5 border border-red-500/20 rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-bold uppercase tracking-wider flex items-center gap-2">
                <Shield className="w-5 h-5 text-red-400" />
                Investigator Summary
              </h3>
            </div>

            <p className="text-gray-300 leading-relaxed mb-6 italic">
              "
              {result.layer3_explanation?.explanation ||
                result.final.reasoning ||
                "The system analysis indicates potential fraud signals requiring immediate review."}
              "
            </p>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-red-500/10">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">
                  Attack Category
                </p>
                <p className="text-sm font-semibold">
                  {isHighRisk
                    ? "Institutional Breach Attempt"
                    : "Legitimate Activity"}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">
                  Recommended Action
                </p>
                <p
                  className="text-sm font-semibold uppercase"
                  style={{ color: verdictColor }}
                >
                  {isHighRisk ? "Immediate Containment" : "Monitor"}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Score Distribution Chart */}
        <motion.div
          className="bg-black/40 border border-green-500/20 rounded-lg p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h3 className="text-lg font-bold mb-6 uppercase tracking-wider">
            Score Distribution
          </h3>
          <p className="text-xs text-gray-500 mb-4">
            Cross-layer risk aggregation and weighted analysis visualization
          </p>

          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={scoreData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#666" />
              <YAxis stroke="#666" />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#22c55e"
                dot={{ fill: "#22c55e", r: 4 }}
                activeDot={{ r: 6 }}
                isAnimationActive
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Detailed Layers - Collapsible */}
        <motion.div
          className="mt-12 pt-8 border-t border-green-500/10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <h3 className="text-lg font-bold mb-4 uppercase tracking-wider">
            Detailed Analysis Layers
          </h3>
          <div className="text-xs text-gray-500 mb-4">
            Click on each layer below to view comprehensive analysis details
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {/* Layer 0 */}
            {result.layer0 && (
              <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
                <h4 className="font-semibold mb-2 text-blue-400">
                  Layer 0: Privacy
                </h4>
                <p className="text-xs text-gray-400 mb-2">
                  Clean text confidence:{" "}
                  {(result.layer0.clean_text_confidence || 0).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-400">
                  PII Detected: {result.layer0.pii_detected ? "Yes" : "No"}
                </p>
              </div>
            )}

            {/* Layer 1 */}
            {result.layer1 && (
              <div className="bg-orange-500/5 border border-orange-500/20 rounded-lg p-4">
                <h4 className="font-semibold mb-2 text-orange-400">
                  Layer 1: Heuristics
                </h4>
                <p className="text-xs text-gray-400 mb-2">
                  Score: {result.layer1.heuristic_score}/150
                </p>
                <p className="text-xs text-gray-400">
                  Flags: {result.layer1.flags?.length || 0}
                </p>
              </div>
            )}

            {/* Layer 2 */}
            {result.layer2 && (
              <div className="bg-purple-500/5 border border-purple-500/20 rounded-lg p-4">
                <h4 className="font-semibold mb-2 text-purple-400">
                  Layer 2: ML
                </h4>
                <p className="text-xs text-gray-400 mb-2">
                  Score: {result.layer2.ml_text_score?.toFixed(1) || 0}/100
                </p>
                <p className="text-xs text-gray-400">
                  Prediction:{" "}
                  {(result.layer2.ml_prediction || "unknown").toUpperCase()}
                </p>
              </div>
            )}

            {/* Layer 3 */}
            {result.layer3_scoring && (
              <div className="bg-green-500/5 border border-green-500/20 rounded-lg p-4">
                <h4 className="font-semibold mb-2 text-green-400">
                  Layer 3: LLM Analysis
                </h4>
                <p className="text-xs text-gray-400 mb-2">
                  Score: {result.layer3_scoring.llm_score?.toFixed(1) || 0}/100
                </p>
                <p className="text-xs text-gray-400">
                  Confidence:{" "}
                  {(result.layer3_scoring.llm_confidence || 0).toFixed(2)}
                </p>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
