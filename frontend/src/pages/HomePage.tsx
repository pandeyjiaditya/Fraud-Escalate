import React from "react";
import { useNavigate } from "react-router-dom";
import { Mail, Upload, User, Shield } from "lucide-react";
import { motion } from "framer-motion";
import Header from "../components/Header";

export default function HomePage() {
  const navigate = useNavigate();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 },
    },
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 },
    },
    hover: {
      y: -10,
      transition: { duration: 0.3 },
    },
  };

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      {/* Background pattern */}
      <div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage:
            "radial-gradient(circle at 20% 50%, #00FF88 0%, transparent 50%)",
        }}
      />
      <div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage:
            "radial-gradient(circle at 80% 80%, #00FFA3 0%, transparent 50%)",
        }}
      />

      <Header />

      {/* Main Content */}
      <motion.div
        className="relative z-10 min-h-[calc(100vh-80px)] flex flex-col items-center justify-center px-6 py-12"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Title Section */}
        <motion.div className="text-center mb-16" variants={itemVariants}>
          <h1 className="text-7xl font-black mb-4">
            <span className="text-white">FRAUD</span>
            <span className="text-green-500">ESCALATE</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Fraud Ends Here !!
          </p>
        </motion.div>

        {/* Cards Grid */}
        <motion.div
          className="grid md:grid-cols-2 gap-8 max-w-4xl w-full"
          variants={containerVariants}
        >
          {/* Mail Terminal Card */}
          <motion.div
            className="group relative"
            variants={cardVariants}
            whileHover="hover"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-transparent rounded-lg blur-xl opacity-0 group-hover:opacity-100 transition duration-500" />
            <div className="relative bg-black/40 border border-green-500/30 rounded-lg p-8 backdrop-blur-sm hover:border-green-500/60 transition duration-300">
              {/* Icon */}
              <div className="mb-6 flex justify-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-green-500/20 to-transparent border border-green-500/50 flex items-center justify-center">
                  <Mail className="w-8 h-8 text-green-500" />
                </div>
              </div>

              {/* Content */}
              <h2 className="text-2xl font-bold text-white mb-3 text-center">
                Mail Terminal
              </h2>
              <p className="text-gray-400 text-center mb-6 leading-relaxed">
                Monitor incoming communications and identify phishing attempts
                with glass-layer heuristics.
              </p>

              {/* Button */}
              <button
                onClick={() => navigate("/mail-terminal")}
                className="w-full group/btn relative py-3 px-4 font-semibold text-green-500 border border-green-500/50 rounded hover:border-green-500 transition duration-300 flex items-center justify-center gap-2 overflow-hidden"
              >
                <span className="absolute inset-0 bg-green-500/10 transform scale-x-0 group-hover/btn:scale-x-100 origin-left transition duration-300" />
                <span className="relative">ACCESS TERMINAL</span>
                <span className="relative">›</span>
              </button>
            </div>
          </motion.div>

          {/* Upload Artifacts Card */}
          <motion.div
            className="group relative"
            variants={cardVariants}
            whileHover="hover"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-transparent rounded-lg blur-xl opacity-0 group-hover:opacity-100 transition duration-500" />
            <div className="relative bg-black/40 border border-green-500/30 rounded-lg p-8 backdrop-blur-sm hover:border-green-500/60 transition duration-300">
              {/* Icon */}
              <div className="mb-6 flex justify-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-green-500/20 to-transparent border border-green-500/50 flex items-center justify-center">
                  <Upload className="w-8 h-8 text-green-500" />
                </div>
              </div>

              {/* Content */}
              <h2 className="text-2xl font-bold text-white mb-3 text-center">
                Upload Artifacts
              </h2>
              <p className="text-gray-400 text-center mb-6 leading-relaxed">
                Initialize deep scans for malicious behavioral patterns in PCAP,
                JSON, and System Logs.
              </p>

              {/* Button */}
              <button
                onClick={() => navigate("/upload-artifacts")}
                className="w-full group/btn relative py-3 px-4 font-semibold text-green-500 border border-green-500/50 rounded hover:border-green-500 transition duration-300 flex items-center justify-center gap-2 overflow-hidden"
              >
                <span className="absolute inset-0 bg-green-500/10 transform scale-x-0 group-hover/btn:scale-x-100 origin-left transition duration-300" />
                <span className="relative">INITIALIZE SCAN</span>
                <span className="relative">›</span>
              </button>
            </div>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  );
}
