import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, Shield, AlertCircle, CheckCircle2, ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import {
  getRiskColor,
  getRiskLevel,
  AnalysisResponse,
} from "../services/analysisService";

const STORAGE_KEY = 'fraud_analysis_results';

export default function ResultsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [expandedLayers, setExpandedLayers] = useState<Set<string>>(new Set(['layer0', 'layer1', 'layer2', 'layer3']));
  const [result, setResult] = useState<AnalysisResponse | undefined>(location.state?.result);

  // Load from localStorage if not passed via navigation
  useEffect(() => {
    if (!result) {
      try {
        const storedResults = localStorage.getItem(STORAGE_KEY);
        if (storedResults) {
          const allResults = JSON.parse(storedResults);
          // Get the most recent result (last one in the object)
          const lastResultKey = Object.keys(allResults)[Object.keys(allResults).length - 1];
          if (lastResultKey) {
            setResult(allResults[lastResultKey]);
          }
        }
      } catch (error) {
        console.error('Error loading stored result:', error);
      }
    }
  }, []);

  if (!result) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">No Results Found</h1>
          <p className="text-gray-400 mb-6">No analysis results stored or passed.</p>
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

  const toggleLayer = (layer: string) => {
    const newSet = new Set(expandedLayers);
    if (newSet.has(layer)) {
      newSet.delete(layer);
    } else {
      newSet.add(layer);
    }
    setExpandedLayers(newSet);
  };

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
          <h2 className="text-xl font-bold text-white mb-4">Detailed Layer Analysis</h2>
          <div className="space-y-4">
            {/* Layer 0 - Privacy */}
            <motion.div
              className="bg-black/40 border border-green-500/20 rounded-lg overflow-hidden"
              whileHover={{ borderColor: "#22c55e" }}
            >
              <button
                onClick={() => toggleLayer('layer0')}
                className="w-full p-6 flex items-center justify-between hover:bg-green-500/5 transition"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                    <span className="text-blue-400 font-bold">0</span>
                  </div>
                  <div className="text-left">
                    <h3 className="text-lg font-semibold text-white">Layer 0 - Privacy & Normalization</h3>
                    <p className="text-sm text-gray-400">Content cleaning and text normalization</p>
                  </div>
                </div>
                <ChevronDown
                  className={`w-5 h-5 text-green-500 transition-transform ${
                    expandedLayers.has('layer0') ? 'rotate-180' : ''
                  }`}
                />
              </button>

              <AnimatePresence>
                {expandedLayers.has('layer0') && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-green-500/10 px-6 py-4 bg-black/20 space-y-4"
                  >
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Clean Text Confidence</p>
                        <p className="text-white font-semibold text-lg">
                          {(result.layer0?.clean_text_confidence || 0).toFixed(2)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Words Analyzed</p>
                        <p className="text-white font-semibold text-lg">{result.layer0?.word_count || 0}</p>
                      </div>
                    </div>
                    {result.layer0?.reasoning && (
                      <div className="bg-blue-500/5 border border-blue-500/20 rounded p-3">
                        <p className="text-gray-400 text-xs font-semibold mb-2">ANALYSIS REASONING</p>
                        <p className="text-gray-300 text-sm leading-relaxed">{result.layer0.reasoning}</p>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Layer 1 - Heuristics */}
            <motion.div
              className="bg-black/40 border border-green-500/20 rounded-lg overflow-hidden"
              whileHover={{ borderColor: "#22c55e" }}
            >
              <button
                onClick={() => toggleLayer('layer1')}
                className="w-full p-6 flex items-center justify-between hover:bg-green-500/5 transition"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center">
                    <span className="text-orange-400 font-bold">1</span>
                  </div>
                  <div className="text-left">
                    <h3 className="text-lg font-semibold text-white">Layer 1 - Heuristic Patterns</h3>
                    <p className="text-sm text-gray-400">Pattern detection and rule-based scoring</p>
                  </div>
                </div>
                <ChevronDown
                  className={`w-5 h-5 text-green-500 transition-transform ${
                    expandedLayers.has('layer1') ? 'rotate-180' : ''
                  }`}
                />
              </button>

              <AnimatePresence>
                {expandedLayers.has('layer1') && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-green-500/10 px-6 py-4 bg-black/20 space-y-4"
                  >
                    <div className="grid md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Heuristic Score</p>
                        <p className="text-white font-semibold text-lg">
                          {result.layer1?.heuristic_score || 0} / 150
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Confidence</p>
                        <p className="text-white font-semibold text-lg">
                          {(result.layer1?.confidence || 0).toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Flags Detected</p>
                        <p className="text-white font-semibold text-lg">
                          {result.layer1?.flags?.length || 0}
                        </p>
                      </div>
                    </div>

                    {result.layer1_reasoning && (
                      <div className="space-y-3">
                        {result.layer1_reasoning.flag_analysis && (
                          <div className="bg-orange-500/5 border border-orange-500/20 rounded p-4">
                            <p className="text-gray-400 text-xs font-semibold mb-3">FLAG ANALYSIS</p>
                            <div className="space-y-2 text-sm">
                              {Object.entries(result.layer1_reasoning.flag_analysis).map(([flag, explanation]) => (
                                <div key={flag} className="border-l-2 border-orange-500/30 pl-3">
                                  <p className="text-orange-400 font-semibold capitalize">{flag}</p>
                                  <p className="text-gray-300 text-xs mt-1">{String(explanation)}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        {result.layer1_reasoning.overall_assessment && (
                          <div className="bg-orange-500/5 border border-orange-500/20 rounded p-3">
                            <p className="text-gray-400 text-xs font-semibold mb-2">OVERALL ASSESSMENT</p>
                            <p className="text-gray-300 text-sm leading-relaxed">
                              {result.layer1_reasoning.overall_assessment}
                            </p>
                          </div>
                        )}
                      </div>
                    )}

                    {result.layer1?.flags && result.layer1.flags.length > 0 && (
                      <div className="bg-black/60 rounded p-3">
                        <p className="text-gray-400 text-xs font-semibold mb-2">DETECTED FLAGS</p>
                        <div className="flex flex-wrap gap-2">
                          {result.layer1.flags.map((flag, idx) => (
                            <span
                              key={idx}
                              className="bg-red-500/20 border border-red-500/30 text-red-400 text-xs px-2 py-1 rounded"
                            >
                              {flag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Layer 2 - ML Model */}
            <motion.div
              className="bg-black/40 border border-green-500/20 rounded-lg overflow-hidden"
              whileHover={{ borderColor: "#22c55e" }}
            >
              <button
                onClick={() => toggleLayer('layer2')}
                className="w-full p-6 flex items-center justify-between hover:bg-green-500/5 transition"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                    <span className="text-purple-400 font-bold">2</span>
                  </div>
                  <div className="text-left">
                    <h3 className="text-lg font-semibold text-white">Layer 2 - Machine Learning</h3>
                    <p className="text-sm text-gray-400">NLP-based fraud classification</p>
                  </div>
                </div>
                <ChevronDown
                  className={`w-5 h-5 text-green-500 transition-transform ${
                    expandedLayers.has('layer2') ? 'rotate-180' : ''
                  }`}
                />
              </button>

              <AnimatePresence>
                {expandedLayers.has('layer2') && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-green-500/10 px-6 py-4 bg-black/20 space-y-4"
                  >
                    <div className="grid md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-gray-400 text-sm mb-1">ML Score</p>
                        <p className="text-white font-semibold text-lg">
                          {result.layer2?.ml_text_score?.toFixed(1) || 0} / 100
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Confidence</p>
                        <p className="text-white font-semibold text-lg">
                          {(result.layer2?.ml_text_confidence || 0).toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Prediction</p>
                        <p className={`font-semibold text-lg ${
                          result.layer2?.ml_prediction === 'fraud' ? 'text-red-400' : 'text-green-400'
                        }`}>
                          {(result.layer2?.ml_prediction || 'unknown')?.toUpperCase()}
                        </p>
                      </div>
                    </div>

                    {result.layer2_reasoning && (
                      <div className="space-y-3">
                        {result.layer2?.reasoning && (
                          <div className="bg-purple-500/5 border border-purple-500/20 rounded p-4">
                            <p className="text-gray-400 text-xs font-semibold mb-2">ML SCORE REASONING</p>
                            <p className="text-gray-300 text-sm leading-relaxed">
                              {result.layer2.reasoning}
                            </p>
                          </div>
                        )}
                        {result.layer2_reasoning.text_analysis && (
                          <div className="bg-purple-500/5 border border-purple-500/20 rounded p-4">
                            <p className="text-gray-400 text-xs font-semibold mb-2">TEXT ANALYSIS</p>
                            <p className="text-gray-300 text-sm leading-relaxed">
                              {result.layer2_reasoning.text_analysis}
                            </p>
                          </div>
                        )}
                        {result.layer2_reasoning.ml_patterns_detected &&
                         Array.isArray(result.layer2_reasoning.ml_patterns_detected) &&
                         result.layer2_reasoning.ml_patterns_detected.length > 0 && (
                          <div className="bg-purple-500/5 border border-purple-500/20 rounded p-3">
                            <p className="text-gray-400 text-xs font-semibold mb-2">PATTERNS DETECTED</p>
                            <div className="flex flex-wrap gap-2">
                              {result.layer2_reasoning.ml_patterns_detected.map((pattern, idx) => (
                                <span
                                  key={idx}
                                  className="bg-purple-500/20 border border-purple-500/30 text-purple-400 text-xs px-2 py-1 rounded"
                                >
                                  {pattern}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {result.layer2_reasoning.comparison_with_heuristics && (
                          <div className="bg-purple-500/5 border border-purple-500/20 rounded p-3">
                            <p className="text-gray-400 text-xs font-semibold mb-2">VS HEURISTICS</p>
                            <p className="text-gray-300 text-sm leading-relaxed">
                              {result.layer2_reasoning.comparison_with_heuristics}
                            </p>
                          </div>
                        )}
                        {result.layer2_reasoning.risk_level && (
                          <div className="bg-purple-500/5 border border-purple-500/20 rounded p-3">
                            <p className="text-gray-400 text-xs font-semibold mb-2">RISK ASSESSMENT</p>
                            <p className="text-purple-400 font-semibold uppercase">{result.layer2_reasoning.risk_level}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Layer 3 - LLM Scoring */}
            <motion.div
              className="bg-black/40 border border-green-500/20 rounded-lg overflow-hidden"
              whileHover={{ borderColor: "#22c55e" }}
            >
              <button
                onClick={() => toggleLayer('layer3')}
                className="w-full p-6 flex items-center justify-between hover:bg-green-500/5 transition"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                    <span className="text-green-400 font-bold">3</span>
                  </div>
                  <div className="text-left">
                    <h3 className="text-lg font-semibold text-white">Layer 3 - LLM Scoring & Reasoning</h3>
                    <p className="text-sm text-gray-400">Large language model analysis</p>
                  </div>
                </div>
                <ChevronDown
                  className={`w-5 h-5 text-green-500 transition-transform ${
                    expandedLayers.has('layer3') ? 'rotate-180' : ''
                  }`}
                />
              </button>

              <AnimatePresence>
                {expandedLayers.has('layer3') && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-green-500/10 px-6 py-4 bg-black/20 space-y-4"
                  >
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-400 text-sm mb-1">LLM Score</p>
                        <p className="text-white font-semibold text-lg">
                          {result.layer3_scoring?.llm_score?.toFixed(1) || 0} / 100
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm mb-1">Confidence</p>
                        <p className="text-white font-semibold text-lg">
                          {(result.layer3_scoring?.llm_confidence || 0).toFixed(2)}
                        </p>
                      </div>
                    </div>

                    {result.layer3_scoring?.reasoning && (
                      <div className="bg-green-500/5 border border-green-500/20 rounded p-4">
                        <p className="text-gray-400 text-xs font-semibold mb-2">LLM REASONING</p>
                        <p className="text-gray-300 text-sm leading-relaxed">
                          {result.layer3_scoring.reasoning}
                        </p>
                      </div>
                    )}

                    {result.layer3_explanation?.explanation && (
                      <div className="bg-green-500/5 border border-green-500/20 rounded p-4">
                        <p className="text-gray-400 text-xs font-semibold mb-2">FINAL EXPLANATION</p>
                        <p className="text-gray-300 text-sm leading-relaxed">
                          {result.layer3_explanation.explanation}
                        </p>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
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
