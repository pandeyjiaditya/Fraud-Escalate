import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Clock, ChevronRight, Trash2 } from "lucide-react";
import { motion } from "framer-motion";
import { AnalysisResponse, getRiskColor } from "../services/analysisService";
import Header from "../components/Header";

const STORAGE_KEY = "fraud_analysis_results";

export default function ResultsHistory() {
  const navigate = useNavigate();
  const [results, setResults] = useState<
    { timestamp: string; data: AnalysisResponse }[]
  >([]);

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = () => {
    try {
      const storedResults = localStorage.getItem(STORAGE_KEY);
      if (storedResults) {
        const allResults = JSON.parse(storedResults);
        const resultsList = Object.entries(allResults)
          .map(([key, value]: [string, any]) => ({
            timestamp: key.replace("result_", ""),
            data: value,
          }))
          .reverse();
        setResults(resultsList);
      }
    } catch (error) {
      console.error("Error loading results:", error);
    }
  };

  const deleteResult = (timestamp: string) => {
    try {
      const storedResults = JSON.parse(
        localStorage.getItem(STORAGE_KEY) || "{}",
      );
      delete storedResults[`result_${timestamp}`];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(storedResults));
      loadResults();
    } catch (error) {
      console.error("Error deleting result:", error);
    }
  };

  const viewResult = (result: AnalysisResponse) => {
    navigate("/results", { state: { result } });
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <Header />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-6 h-6 text-green-500" />
            <h1 className="text-3xl font-bold">Results History</h1>
          </div>
          <p className="text-gray-400">
            View all previous fraud analysis results
          </p>
        </motion.div>

        {results.length === 0 ? (
          <motion.div
            className="text-center py-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">No analysis history yet</p>
            <p className="text-gray-500 text-sm mt-2">
              Analyze content to build your history
            </p>
            <button
              onClick={() => navigate("/upload-artifacts")}
              className="mt-6 px-6 py-2 bg-green-500/20 border border-green-500/30 hover:border-green-500/60 rounded transition text-green-500"
            >
              Analyze Content
            </button>
          </motion.div>
        ) : (
          <motion.div
            className="space-y-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {results.map((result, index) => {
              const score = result.data.final.risk_score;
              const riskColor = getRiskColor(result.data.final.risk_color);
              const decision = result.data.final.decision;
              const timestamp = new Date(result.timestamp);
              const formattedDate = timestamp.toLocaleDateString("en-US", {
                year: "numeric",
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              });

              return (
                <motion.div
                  key={result.timestamp}
                  className="bg-black/40 border border-green-500/20 hover:border-green-500/40 rounded-lg p-6 cursor-pointer transition"
                  onClick={() => viewResult(result.data)}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ borderColor: "#22c55e" }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <h3 className="font-semibold text-lg">
                          Analysis Result #{results.length - index}
                        </h3>
                        <span className={`text-2xl font-bold ${riskColor}`}>
                          {score.toFixed(1)}/100
                        </span>
                      </div>

                      <div className="grid grid-cols-4 gap-4 mb-2">
                        <div>
                          <p className="text-gray-500 text-xs mb-1">DECISION</p>
                          <p
                            className={`font-semibold ${
                              decision === "SAFE"
                                ? "text-green-400"
                                : "text-red-400"
                            }`}
                          >
                            {decision}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500 text-xs mb-1">
                            HEURISTICS
                          </p>
                          <p className="font-semibold">
                            {result.data.layer1?.heuristic_score || 0}/100
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500 text-xs mb-1">ML SCORE</p>
                          <p className="font-semibold">
                            {result.data.layer2?.ml_text_score?.toFixed(0) || 0}
                            /100
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500 text-xs mb-1">
                            LLM SCORE
                          </p>
                          <p className="font-semibold">
                            {result.data.layer3_scoring?.llm_score?.toFixed(
                              0,
                            ) || 0}
                            /100
                          </p>
                        </div>
                      </div>

                      <p className="text-gray-400 text-sm">{formattedDate}</p>
                    </div>

                    <div className="flex items-center gap-4">
                      <ChevronRight className="w-5 h-5 text-gray-500" />
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteResult(result.timestamp);
                        }}
                        className="p-2 hover:bg-red-500/10 rounded transition text-red-500/60 hover:text-red-500"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </div>
    </div>
  );
}
