import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Mail, ChevronRight, AlertCircle, CheckCircle, AlertTriangle } from "lucide-react";
import Header from "../components/Header";
import { motion } from "framer-motion";

interface Email {
  id: number;
  subject: string;
  body: string;
}

export default function MailTerminal() {
  const navigate = useNavigate();
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  // Fetch emails on mount
  useEffect(() => {
    fetchEmails();
  }, []);

  const fetchEmails = async () => {
    try {
      const response = await fetch("http://localhost:8000/emails");
      const data = await response.json();
      setEmails(data.emails);
    } catch (error) {
      console.error("Error fetching emails:", error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeEmail = async (email: Email) => {
    setSelectedEmail(email);
    setAnalyzing(true);

    try {
      const response = await fetch(`http://localhost:8000/emails/${email.id}/analyze`, {
        method: "POST",
      });
      const result = await response.json();

      // Navigate to results page with the analysis
      navigate("/results", { state: { result: result } });
    } catch (error) {
      console.error("Error analyzing email:", error);
      alert("Failed to analyze email. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <Header />

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Header */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-4xl font-bold text-white mb-2">Mail Terminal</h1>
          <p className="text-gray-400">
            Select an email to analyze for fraud signals
          </p>
        </motion.div>

        {/* Emails List */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-400">Loading emails...</div>
          </div>
        ) : (
          <motion.div
            className="space-y-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ staggerChildren: 0.1 }}
          >
            {emails.map((email) => (
              <motion.div
                key={email.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                whileHover={{ x: 4 }}
                className="bg-black/40 border border-green-500/30 rounded-lg p-4 cursor-pointer hover:border-green-500/60 hover:bg-black/50 transition duration-300 group"
                onClick={() => analyzeEmail(email)}
              >
                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div className="pt-1">
                    <Mail className="w-5 h-5 text-green-500 group-hover:text-green-400" />
                  </div>

                  {/* Email Content */}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-white truncate group-hover:text-green-400 transition">
                      {email.subject}
                    </h3>
                    <p className="text-gray-400 text-sm truncate line-clamp-2">
                      {email.body}
                    </p>
                  </div>

                  {/* Arrow */}
                  <ChevronRight className="w-5 h-5 text-gray-500 group-hover:text-green-500 group-hover:translate-x-1 transition" />
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Empty State */}
        {!loading && emails.length === 0 && (
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">No emails found. Please check back later.</p>
          </div>
        )}
      </div>

      {/* Analysis Status */}
      {analyzing && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-black border border-green-500/30 rounded-lg p-8">
            <div className="flex items-center gap-3">
              <div className="animate-spin">
                <Mail className="w-6 h-6 text-green-500" />
              </div>
              <p className="text-white">Analyzing email...</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
