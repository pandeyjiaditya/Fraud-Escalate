import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Shield,
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  Download,
  Eye,
  EyeOff,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { AnalysisResponse, getRiskColor } from "../services/analysisService";
import Header from "../components/Header";

const STORAGE_KEY = "fraud_analysis_results";

export default function DetailedAnalysis() {
  const navigate = useNavigate();
  const location = useLocation();
  const [result, setResult] = useState<AnalysisResponse | undefined>(
    location.state?.result,
  );
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["overview", "layer0", "layer1", "layer2", "layer3", "decision"]),
  );
  const [showRawJson, setShowRawJson] = useState(false);

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
    }
  }, []);

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

  const toggleSection = (section: string) => {
    const newSet = new Set(expandedSections);
    if (newSet.has(section)) {
      newSet.delete(section);
    } else {
      newSet.add(section);
    }
    setExpandedSections(newSet);
  };

  const riskScore = result.final.risk_score;
  const riskLevel = result.final.risk_level;
  const riskColor = getRiskColor(result.final.risk_color);
  const decision = result.final.decision;
  const reasoning = result.final.reasoning;

  const ScoreBar = ({ score, max = 100 }: { score: number; max?: number }) => {
    const percentage = (score / max) * 100;
    return (
      <div className="w-full bg-black/40 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full transition-all ${
            percentage >= 70
              ? "bg-red-500"
              : percentage >= 40
                ? "bg-yellow-500"
                : "bg-green-500"
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    );
  };

  const SectionHeader = ({
    icon: Icon,
    title,
    section,
    badge,
  }: {
    icon: any;
    title: string;
    section: string;
    badge?: React.ReactNode;
  }) => (
    <button
      onClick={() => toggleSection(section)}
      className="w-full p-6 flex items-center justify-between hover:bg-green-500/5 transition group"
    >
      <div className="flex items-center gap-4 flex-1">
        <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
          <Icon className="w-6 h-6 text-green-500" />
        </div>
        <div className="text-left">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          {badge && <p className="text-xs text-gray-400 mt-1">{badge}</p>}
        </div>
      </div>
      <ChevronDown
        className={`w-5 h-5 text-green-500 transition-transform ${
          expandedSections.has(section) ? "rotate-180" : ""
        }`}
      />
    </button>
  );

  const DetailSection = ({
    title,
    children,
    section,
    icon: Icon,
    badge,
  }: {
    title: string;
    children: React.ReactNode;
    section: string;
    icon: any;
    badge?: React.ReactNode;
  }) => (
    <motion.div className="bg-black/40 border border-green-500/20 rounded-lg overflow-hidden mb-6">
      <SectionHeader
        icon={Icon}
        title={title}
        section={section}
        badge={badge}
      />
      <AnimatePresence>
        {expandedSections.has(section) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-green-500/10 px-6 py-4 bg-black/20 space-y-4"
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-black text-white">
      <Header />

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Overall Risk Summary */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="bg-gradient-to-r from-green-500/10 to-black border border-green-500/30 rounded-lg p-8">
            <div className="grid md:grid-cols-4 gap-8">
              {/* Risk Score */}
              <div className="text-center">
                <p className="text-gray-400 text-sm mb-2">RISK SCORE</p>
                <div className={`text-5xl font-black ${riskColor}`}>
                  {riskScore.toFixed(1)}
                </div>
                <p className="text-gray-400 text-xs mt-2">/100</p>
              </div>

              {/* Risk Level */}
              <div className="text-center">
                <p className="text-gray-400 text-sm mb-2">RISK LEVEL</p>
                <div className={`text-3xl font-black ${riskColor}`}>
                  {riskLevel}
                </div>
                {riskScore >= 70 && (
                  <AlertCircle
                    className={`w-6 h-6 mx-auto mt-2 ${riskColor}`}
                  />
                )}
                {riskScore < 40 && (
                  <CheckCircle2
                    className={`w-6 h-6 mx-auto mt-2 ${riskColor}`}
                  />
                )}
              </div>

              {/* Decision */}
              <div className="text-center">
                <p className="text-gray-400 text-sm mb-2">DECISION</p>
                <div className="text-2xl font-bold text-white">{decision}</div>
                <p className="text-gray-400 text-xs mt-2">
                  {decision === "SAFE"
                    ? "✓ Approved"
                    : decision === "REVIEW"
                      ? "⚠ Review"
                      : "🚨 Block"}
                </p>
              </div>

              {/* Confidence */}
              <div className="text-center">
                <p className="text-gray-400 text-sm mb-2">CONFIDENCE</p>
                <div className="text-3xl font-black text-blue-400">
                  {(result.final.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Executive Summary */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="bg-black/40 border border-green-500/20 rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4">
              Executive Summary
            </h2>
            <p className="text-gray-300 leading-relaxed text-lg">{reasoning}</p>
          </div>
        </motion.div>

        {/* Layer 0 - Privacy & Normalization */}
        <DetailSection
          title="Layer 0 - Privacy & Normalization"
          section="layer0"
          icon={Shield}
          badge="Text Cleaning & Feature Extraction"
        >
          <div className="grid md:grid-cols-3 gap-4 mb-4">
            <div className="bg-black/40 rounded p-4">
              <p className="text-gray-400 text-xs mb-2">
                Clean Text Confidence
              </p>
              <p className="text-white font-semibold text-lg">
                {(result.layer0?.clean_text_confidence || 0).toFixed(1)}%
              </p>
            </div>
            <div className="bg-black/40 rounded p-4">
              <p className="text-gray-400 text-xs mb-2">Words Analyzed</p>
              <p className="text-white font-semibold text-lg">
                {result.layer0?.word_count || 0}
              </p>
            </div>
            <div className="bg-black/40 rounded p-4">
              <p className="text-gray-400 text-xs mb-2">PII Detected</p>
              <p
                className={`font-semibold text-lg ${
                  result.layer0?.pii_detected
                    ? "text-red-400"
                    : "text-green-400"
                }`}
              >
                {result.layer0?.pii_detected ? "Yes" : "No"}
              </p>
            </div>
          </div>

          {/* Features */}
          <div className="bg-blue-500/5 border border-blue-500/20 rounded p-4">
            <p className="text-blue-400 text-sm font-semibold mb-3">
              DETECTED FEATURES
            </p>
            <div className="grid md:grid-cols-2 gap-2">
              {[
                { key: "has_url", label: "URL Detected" },
                { key: "has_urgent_words", label: "Urgent Words" },
                { key: "has_numbers", label: "Numbers Present" },
                { key: "has_sensitive_keywords", label: "Sensitive Keywords" },
              ].map((feature) => (
                <div
                  key={feature.key}
                  className={`p-3 rounded ${
                    result.layer0?.features?.[
                      feature.key as keyof typeof result.layer0.features
                    ]
                      ? "bg-red-500/10 border border-red-500/30"
                      : "bg-green-500/10 border border-green-500/30"
                  }`}
                >
                  <p
                    className={`text-xs font-semibold ${
                      result.layer0?.features?.[
                        feature.key as keyof typeof result.layer0.features
                      ]
                        ? "text-red-400"
                        : "text-green-400"
                    }`}
                  >
                    {feature.label}:{" "}
                    {result.layer0?.features?.[
                      feature.key as keyof typeof result.layer0.features
                    ]
                      ? "✓"
                      : "✗"}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </DetailSection>

        {/* Layer 1 - Heuristics */}
        <DetailSection
          title="Layer 1 - Heuristic Pattern Detection"
          section="layer1"
          icon={AlertCircle}
          badge={`Score: ${result.layer1?.heuristic_score || 0}/100 | Confidence: ${(
            result.layer1?.confidence || 0
          ).toFixed(2)}`}
        >
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-400 text-sm">Heuristic Score</span>
                <span className="text-white font-semibold">
                  {result.layer1?.heuristic_score || 0} / 100
                </span>
              </div>
              <ScoreBar score={result.layer1?.heuristic_score || 0} />
            </div>

            {/* Detected Flags */}
            {result.layer1?.flags && result.layer1.flags.length > 0 && (
              <div className="bg-red-500/10 border border-red-500/20 rounded p-4">
                <p className="text-red-400 text-sm font-semibold mb-3">
                  DETECTED FLAGS ({result.layer1.flags.length})
                </p>
                <div className="flex flex-wrap gap-2">
                  {result.layer1.flags.map((flag: string, idx: number) => (
                    <span
                      key={idx}
                      className="bg-red-500/20 border border-red-500/40 text-red-300 text-xs px-3 py-1 rounded"
                    >
                      {flag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Layer 1 Reasoning */}
            {result.layer1_reasoning && (
              <div className="bg-orange-500/5 border border-orange-500/20 rounded p-4">
                <p className="text-orange-400 text-sm font-semibold mb-3">
                  FLAG ANALYSIS
                </p>
                {result.layer1_reasoning.flag_analysis &&
                  Object.entries(result.layer1_reasoning.flag_analysis).map(
                    ([flag, explanation]) => (
                      <div key={flag} className="mb-3 p-3 bg-black/40 rounded">
                        <p className="text-orange-400 font-semibold capitalize text-sm">
                          {flag}
                        </p>
                        <p className="text-gray-300 text-xs mt-1">
                          {String(explanation)}
                        </p>
                      </div>
                    ),
                  )}
                {result.layer1_reasoning.overall_assessment && (
                  <div className="mt-4 p-3 bg-black/60 rounded border border-orange-500/10">
                    <p className="text-gray-400 text-xs font-semibold mb-1">
                      ASSESSMENT
                    </p>
                    <p className="text-gray-300 text-sm">
                      {result.layer1_reasoning.overall_assessment}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </DetailSection>

        {/* Layer 2 - ML Analysis */}
        <DetailSection
          title="Layer 2 - Machine Learning Classification"
          section="layer2"
          icon={Eye}
          badge={`Score: ${(result.layer2?.ml_text_score || 0).toFixed(1)}/100 | Prediction: ${
            result.layer2?.ml_prediction || "unknown"
          }`}
        >
          <div className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400 text-sm">ML Text Score</span>
                  <span className="text-white font-semibold">
                    {(result.layer2?.ml_text_score || 0).toFixed(1)} / 100
                  </span>
                </div>
                <ScoreBar score={result.layer2?.ml_text_score || 0} />
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400 text-sm">Confidence</span>
                  <span className="text-white font-semibold">
                    {(result.layer2?.ml_text_confidence || 0).toFixed(2)}
                  </span>
                </div>
                <ScoreBar
                  score={(result.layer2?.ml_text_confidence || 0) * 100}
                />
              </div>
            </div>

            <div className="bg-purple-500/10 border border-purple-500/20 rounded p-4">
              <p className="text-purple-400 text-sm font-semibold mb-2">
                PREDICTION
              </p>
              <p className="text-white text-lg font-bold">
                {result.layer2?.ml_prediction === "fraud"
                  ? "🚨 FRAUD"
                  : "✓ SAFE"}
              </p>
            </div>

            {/* Layer 2 Reasoning */}
            {result.layer2_reasoning && (
              <div className="bg-purple-500/5 border border-purple-500/20 rounded p-4">
                <p className="text-purple-400 text-sm font-semibold mb-3">
                  ML ANALYSIS
                </p>
                <div className="space-y-3">
                  {result.layer2_reasoning.text_analysis && (
                    <div className="p-3 bg-black/40 rounded">
                      <p className="text-gray-400 text-xs font-semibold mb-1">
                        TEXT ANALYSIS
                      </p>
                      <p className="text-gray-300 text-sm">
                        {result.layer2_reasoning.text_analysis}
                      </p>
                    </div>
                  )}
                  {result.layer2_reasoning.ml_patterns_detected &&
                    result.layer2_reasoning.ml_patterns_detected.length > 0 && (
                      <div className="p-3 bg-black/40 rounded">
                        <p className="text-gray-400 text-xs font-semibold mb-2">
                          PATTERNS DETECTED
                        </p>
                        <ul className="space-y-1">
                          {result.layer2_reasoning.ml_patterns_detected.map(
                            (pattern: string, idx: number) => (
                              <li key={idx} className="text-gray-300 text-sm">
                                • {pattern}
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                    )}
                  {result.layer2_reasoning.comparison_with_heuristics && (
                    <div className="p-3 bg-black/40 rounded">
                      <p className="text-gray-400 text-xs font-semibold mb-1">
                        COMPARISON WITH HEURISTICS
                      </p>
                      <p className="text-gray-300 text-sm">
                        {result.layer2_reasoning.comparison_with_heuristics}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </DetailSection>

        {/* Layer 3 - LLM Analysis */}
        <DetailSection
          title="Layer 3 - LLM Fraud Scoring & Explanation"
          section="layer3"
          icon={Shield}
          badge={`Score: ${(result.layer3_scoring?.llm_score || 0).toFixed(1)}/100`}
        >
          <div className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400 text-sm">LLM Score</span>
                  <span className="text-white font-semibold">
                    {(result.layer3_scoring?.llm_score || 0).toFixed(1)} / 100
                  </span>
                </div>
                <ScoreBar score={result.layer3_scoring?.llm_score || 0} />
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400 text-sm">LLM Confidence</span>
                  <span className="text-white font-semibold">
                    {(result.layer3_scoring?.llm_confidence || 0).toFixed(2)}
                  </span>
                </div>
                <ScoreBar
                  score={(result.layer3_scoring?.llm_confidence || 0) * 100}
                />
              </div>
            </div>

            {/* LLM Reasoning */}
            {result.layer3_scoring?.reasoning && (
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded p-4">
                <p className="text-yellow-400 text-sm font-semibold mb-2">
                  LLM REASONING
                </p>
                <p className="text-gray-300 text-sm">
                  {result.layer3_scoring.reasoning}
                </p>
              </div>
            )}

            {/* Final Explanation */}
            {result.layer3_explanation?.explanation && (
              <div className="bg-green-500/10 border border-green-500/20 rounded p-4">
                <p className="text-green-400 text-sm font-semibold mb-2">
                  FINAL EXPLANATION
                </p>
                <p className="text-gray-300 text-sm leading-relaxed">
                  {result.layer3_explanation.explanation}
                </p>
              </div>
            )}
          </div>
        </DetailSection>

        {/* Raw JSON Toggle */}
        <div className="mt-8 mb-4">
          <button
            onClick={() => setShowRawJson(!showRawJson)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-900 border border-gray-700 hover:border-gray-500 rounded text-gray-400 hover:text-white transition"
          >
            {showRawJson ? (
              <EyeOff className="w-4 h-4" />
            ) : (
              <Eye className="w-4 h-4" />
            )}
            {showRawJson ? "Hide Raw JSON" : "Show Raw JSON"}
          </button>
        </div>

        {/* Raw JSON Display */}
        <AnimatePresence>
          {showRawJson && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-black/60 border border-gray-700 rounded p-4 mb-8"
            >
              <pre className="text-gray-300 text-xs overflow-auto max-h-96">
                {JSON.stringify(result, null, 2)}
              </pre>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
