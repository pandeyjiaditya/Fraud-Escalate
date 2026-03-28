import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, Upload, X, CheckCircle2, AlertCircle, Loader, FileText, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  analyzeFile,
  detectFileType,
  getFileTypeDescription,
  getRiskColor,
  FileSegregation,
  AnalysisResponse,
} from '../services/analysisService';

const STORAGE_KEY = 'fraud_analysis_results';
const STORAGE_FILES_KEY = 'fraud_analysis_files';

export default function UploadArtifacts() {
  const navigate = useNavigate();
  const [tab, setTab] = useState<'files' | 'text'>('files');
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<FileSegregation[]>([]);
  const [analyzing, setAnalyzing] = useState<Set<string>>(new Set());
  const [results, setResults] = useState<Record<string, AnalysisResponse>>({});
  const [currentLayer, setCurrentLayer] = useState<Record<string, number>>({}); // Track current layer per file
  const [textInput, setTextInput] = useState('');
  const [textAnalyzing, setTextAnalyzing] = useState(false);
  const [textResult, setTextResult] = useState<AnalysisResponse | null>(null);
  const [textCurrentLayer, setTextCurrentLayer] = useState(0);

  // Load stored results from localStorage on mount
  useEffect(() => {
    try {
      const storedResults = localStorage.getItem(STORAGE_KEY);
      const storedFiles = localStorage.getItem(STORAGE_FILES_KEY);

      if (storedResults) {
        setResults(JSON.parse(storedResults));
      }
      if (storedFiles) {
        setFiles(JSON.parse(storedFiles));
      }
    } catch (error) {
      console.error('Error loading stored data:', error);
    }
  }, []);

  // Save results to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(results));
      localStorage.setItem(STORAGE_FILES_KEY, JSON.stringify(files));
    } catch (error) {
      console.error('Error saving data:', error);
    }
  }, [results, files]);

  const clearAllData = () => {
    if (window.confirm('Are you sure you want to clear all analysis data?')) {
      setResults({});
      setFiles([]);
      setTextResult(null);
      setTextInput('');
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(STORAGE_FILES_KEY);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  };

  const addFiles = (newFiles: File[]) => {
    const segregatedFiles: FileSegregation[] = newFiles.map((file) => ({
      filename: file.name,
      type: detectFileType(file.name),
      size: file.size,
      status: 'pending',
    }));
    setFiles([...files, ...segregatedFiles]);
  };

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    setFiles(newFiles);
  };

  const handleAnalyzeFile = async (index: number) => {
    const fileItem = files[index];
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (!fileInput?.files) return;

    const file = Array.from(fileInput.files).find((f) => f.name === fileItem.filename);
    if (!file) return;

    const fileId = `${fileItem.filename}-${index}`;
    setAnalyzing((prev) => new Set([...prev, fileId]));
    setCurrentLayer((prev) => ({ ...prev, [fileId]: 0 }));
    files[index].status = 'processing';
    setFiles([...files]);

    // Simulate layer progression for visual feedback
    const layerProgression = [0, 1, 2, 3];
    const progressInterval = setInterval(() => {
      setCurrentLayer((prev) => {
        const current = (prev[fileId] || 0) + 1;
        return { ...prev, [fileId]: current };
      });
    }, 800);

    try {
      const response = await analyzeFile(file);
      clearInterval(progressInterval);
      setCurrentLayer((prev) => ({ ...prev, [fileId]: 4 })); // Complete state

      console.log('Analysis response:', response);

      files[index].status = 'success';
      files[index].results = {
        input_type: response.input.type,
        detected_type: fileItem.type,
        content_preview: response.input.content.substring(0, 200),
        metadata: response.input.metadata,
      };

      // Store in localStorage with unique key
      setResults((prev) => {
        const updated = { ...prev, [fileId]: response };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
        return updated;
      });
    } catch (error) {
      clearInterval(progressInterval);
      console.error('Analysis error:', error);
      files[index].status = 'error';
      files[index].error = error instanceof Error ? error.message : 'Analysis failed';
    } finally {
      setAnalyzing((prev) => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
      setFiles([...files]);
    }
  };

  const handleViewResults = (index: number) => {
    const fileId = `${files[index].filename}-${index}`;
    const result = results[fileId];
    if (result) {
      navigate('/results', { state: { result } });
    }
  };

  const handleAnalyzeText = async () => {
    if (!textInput.trim()) return;

    setTextAnalyzing(true);
    setTextCurrentLayer(0);

    // Simulate layer progression for visual feedback
    const progressInterval = setInterval(() => {
      setTextCurrentLayer((prev) => prev + 1);
    }, 800);

    try {
      const formData = new FormData();
      const blob = new Blob([textInput], { type: 'text/plain' });
      const file = new File([blob], 'text_input.txt', { type: 'text/plain' });
      formData.append('file', file);

      const response = await analyzeFile(file);
      clearInterval(progressInterval);
      setTextCurrentLayer(4); // Complete state

      console.log('Text analysis response:', response);
      setTextResult(response);

      // Store in localStorage
      const storedResults = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      storedResults['text_input'] = response;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(storedResults));
    } catch (error) {
      clearInterval(progressInterval);
      console.error('Text analysis error:', error);
      alert(error instanceof Error ? error.message : 'Analysis failed');
    } finally {
      setTextAnalyzing(false);
    }
  };

  const handleViewTextResults = () => {
    if (textResult) {
      navigate('/results', { state: { result: textResult } });
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-green-500/20 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="p-2 hover:bg-green-500/10 rounded transition"
            >
              <ArrowLeft className="w-6 h-6 text-green-500" />
            </button>
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-3 hover:opacity-80 transition"
            >
              <div className="w-10 h-10 border-2 border-green-500 rounded flex items-center justify-center">
                <Shield className="w-6 h-6 text-green-500" />
              </div>
              <div>
                <div className="text-sm font-bold text-white">NULLPOINT</div>
                <div className="text-xs text-green-500">Upload Artifacts</div>
              </div>
            </button>
          </div>
          {(files.length > 0 || textResult) && (
            <button
              onClick={clearAllData}
              className="p-2 hover:bg-red-500/10 text-red-500 rounded transition flex items-center gap-2"
              title="Clear all analysis data"
            >
              <Trash2 className="w-5 h-5" />
              <span className="text-sm font-semibold">Clear All</span>
            </button>
          )}
        </div>
      </header>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Upload Artifacts</h1>
          <p className="text-gray-400 mb-8">
            Initialize deep scans for malicious behavioral patterns in PCAP, JSON, and System Logs.
            Files will be automatically segregated and analyzed.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex gap-4 mb-8 border-b border-green-500/20">
          <button
            onClick={() => setTab('files')}
            className={`pb-4 px-2 font-semibold transition ${
              tab === 'files'
                ? 'text-green-500 border-b-2 border-green-500'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Upload Files
            </div>
          </button>
          <button
            onClick={() => setTab('text')}
            className={`pb-4 px-2 font-semibold transition ${
              tab === 'text'
                ? 'text-green-500 border-b-2 border-green-500'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Direct Text Input
            </div>
          </button>
        </div>

        {/* FILE UPLOAD TAB */}
        {tab === 'files' && (
          <>
            {/* Previous Results Section */}
            {Object.keys(results).length > 0 && (
              <motion.div
                className="mb-8 p-6 bg-blue-500/5 border border-blue-500/20 rounded-lg"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-blue-400">
                    📊 Previous Analysis Results ({Object.keys(results).length})
                  </h3>
                </div>
                <div className="space-y-2">
                  {Object.entries(results).map(([resultId, resultData]) => (
                    <motion.div
                      key={resultId}
                      className="bg-black/40 rounded p-3 flex items-center justify-between hover:bg-black/60 transition"
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className="flex-1">
                        <p className="text-white font-semibold text-sm">{resultId}</p>
                        <p className="text-xs text-gray-400">
                          Score: {resultData.final.risk_score.toFixed(1)}/100 | {resultData.final.risk_level}
                        </p>
                      </div>
                      <button
                        onClick={() => navigate('/results', { state: { result: resultData } })}
                        className="ml-4 px-3 py-1 bg-blue-500/20 border border-blue-500 text-blue-400 rounded text-xs font-semibold hover:bg-blue-500/30 transition"
                      >
                        View
                      </button>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
        {/* Upload Zone */}
        <motion.div
          className={`border-2 border-dashed rounded-lg p-12 text-center transition duration-300 mb-8 ${
            isDragging
              ? 'border-green-500 bg-green-500/10'
              : 'border-green-500/30 bg-black/40'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          whileHover={{ scale: 1.02 }}
        >
          <Upload className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Drop files here</h2>
          <p className="text-gray-400 mb-4">or</p>
          <label>
            <span className="text-green-500 hover:text-green-400 cursor-pointer font-semibold">
              click to browse
            </span>
            <input
              type="file"
              multiple
              onChange={handleFileInput}
              className="hidden"
              accept=".pcap,.json,.log,.txt,.csv,.pdf,.docx,.mp3,.wav,.jpg,.png,.mp4"
            />
          </label>
          <p className="text-xs text-gray-500 mt-4">
            Supported: Images, Audio, Video, PDF, Word, Text, JSON, Logs, CSV, PCAP
          </p>
        </motion.div>

        {/* File List */}
        {files.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h3 className="text-lg font-semibold text-white mb-4">
              Uploaded Files ({files.length})
            </h3>

            <AnimatePresence>
              <div className="space-y-3">
                {files.map((file, index) => {
                  const fileId = `${file.filename}-${index}`;
                  const isAnalyzing = analyzing.has(fileId);
                  const hasResult = fileId in results;

                  return (
                    <motion.div
                      key={fileId}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      className="bg-black/40 border border-green-500/20 rounded-lg p-4 hover:border-green-500/40 transition"
                    >
                      {/* File Header */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="text-white font-semibold">{file.filename}</p>
                            <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">
                              {getFileTypeDescription(file.type)}
                            </span>
                            {file.status === 'success' && (
                              <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded flex items-center gap-1">
                                <CheckCircle2 className="w-3 h-3" /> Analyzed
                              </span>
                            )}
                            {file.status === 'error' && (
                              <span className="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded flex items-center gap-1">
                                <AlertCircle className="w-3 h-3" /> Error
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-500">
                            {(file.size / 1024).toFixed(2)} KB
                          </p>
                        </div>

                        {!isAnalyzing && file.status !== 'processing' && (
                          <button
                            onClick={() => removeFile(index)}
                            className="p-2 hover:bg-red-500/10 text-red-500 rounded transition"
                            title="Remove file"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        )}
                      </div>

                      {/* Error Message */}
                      {file.error && (
                        <div className="mb-3 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded p-2">
                          {file.error}
                        </div>
                      )}

                      {/* Analysis Progress Visualization */}
                      {isAnalyzing && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="mb-3 bg-blue-500/5 border border-blue-500/20 rounded p-4"
                        >
                          <div className="grid grid-cols-4 gap-2">
                            {['Layer 0', 'Layer 1', 'Layer 2', 'Layer 3'].map((layer, idx) => {
                              const layerNum = currentLayer[fileId] || 0;
                              const isActive = idx === layerNum;
                              const isComplete = idx < layerNum;
                              return (
                                <div key={idx} className="flex flex-col items-center gap-1">
                                  <div
                                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all ${
                                      isComplete
                                        ? 'bg-green-500 text-black'
                                        : isActive
                                        ? 'bg-blue-500 text-white animate-pulse'
                                        : 'bg-gray-700 text-gray-400'
                                    }`}
                                  >
                                    {isComplete ? '✓' : idx + 1}
                                  </div>
                                  <p className={`text-xs font-semibold ${
                                    isActive || isComplete ? 'text-white' : 'text-gray-400'
                                  }`}>
                                    {layer}
                                  </p>
                                </div>
                              );
                            })}
                          </div>
                          <p className="text-xs text-gray-400 mt-3 text-center">
                            {currentLayer[fileId] === 0 && 'Starting analysis...'}
                            {currentLayer[fileId] === 1 && 'Analyzing Layer 0 (Privacy)...'}
                            {currentLayer[fileId] === 2 && 'Analyzing Layer 1 (Heuristics)...'}
                            {currentLayer[fileId] === 3 && 'Analyzing Layer 2 (ML)...'}
                            {currentLayer[fileId] === 4 && 'Processing Layer 3 (LLM)...'}
                          </p>
                        </motion.div>
                      )}

                      {/* Results Preview */}
                      {hasResult && results[fileId] && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="mb-3 bg-green-500/5 border border-green-500/20 rounded p-3 text-sm space-y-3"
                        >
                          {/* Risk Score and Level */}
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <p className="text-gray-400 text-xs">Risk Score</p>
                              <p className={`text-lg font-bold ${getRiskColor(results[fileId].final.risk_color)}`}>
                                {results[fileId].final.risk_score.toFixed(1)}/100
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-400 text-xs">Risk Level</p>
                              <p className={`text-lg font-bold ${getRiskColor(results[fileId].final.risk_color)}`}>
                                {results[fileId].final.risk_level}
                              </p>
                            </div>
                          </div>

                          {/* Layer 3 Explanation */}
                          <div className="bg-black/40 rounded p-3 border border-green-500/10">
                            <p className="text-gray-400 text-xs font-semibold mb-1">Layer 3 (LLM) Analysis</p>
                            <p className="text-gray-300 text-xs leading-relaxed">
                              {results[fileId].layer3_scoring?.reasoning || results[fileId].final.reasoning}
                            </p>
                          </div>

                          {/* Decision */}
                          <div>
                            <p className="text-gray-400 text-xs">Decision</p>
                            <p className="text-white text-sm font-semibold">{results[fileId].final.decision}</p>
                          </div>
                        </motion.div>
                      )}

                      {/* Action Buttons */}
                      <div className="flex gap-2">
                        {file.status === 'pending' && (
                          <button
                            onClick={() => handleAnalyzeFile(index)}
                            className="flex-1 py-2 px-3 bg-green-500/20 border border-green-500 text-green-500 rounded font-semibold hover:bg-green-500/30 transition text-sm"
                          >
                            Analyze File
                          </button>
                        )}

                        {isAnalyzing && (
                          <button
                            disabled
                            className="flex-1 py-2 px-3 bg-green-500/10 border border-green-500/50 text-green-500/50 rounded font-semibold text-sm flex items-center justify-center gap-2"
                          >
                            <Loader className="w-4 h-4 animate-spin" />
                            Analyzing...
                          </button>
                        )}

                        {hasResult && (
                          <button
                            onClick={() => handleViewResults(index)}
                            className="flex-1 py-2 px-3 bg-green-500/20 border border-green-500 text-green-500 rounded font-semibold hover:bg-green-500/30 transition text-sm"
                          >
                            View Full Results
                          </button>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </AnimatePresence>

            {/* Summary Stats */}
            <motion.div
              className="mt-8 grid grid-cols-4 gap-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="bg-black/40 border border-green-500/20 rounded p-4 text-center">
                <p className="text-gray-400 text-xs mb-1">Total Files</p>
                <p className="text-2xl font-bold text-white">{files.length}</p>
              </div>
              <div className="bg-black/40 border border-green-500/20 rounded p-4 text-center">
                <p className="text-gray-400 text-xs mb-1">Analyzed</p>
                <p className="text-2xl font-bold text-green-500">
                  {files.filter((f) => f.status === 'success').length}
                </p>
              </div>
              <div className="bg-black/40 border border-green-500/20 rounded p-4 text-center">
                <p className="text-gray-400 text-xs mb-1">Processing</p>
                <p className="text-2xl font-bold text-orange-500">
                  {files.filter((f) => f.status === 'processing').length +
                    Array.from(analyzing).length}
                </p>
              </div>
              <div className="bg-black/40 border border-green-500/20 rounded p-4 text-center">
                <p className="text-gray-400 text-xs mb-1">Errors</p>
                <p className="text-2xl font-bold text-red-500">
                  {files.filter((f) => f.status === 'error').length}
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
          </>
        )}

        {/* DIRECT TEXT INPUT TAB */}
        {tab === 'text' && (
          <>
            {/* Previous Text Results */}
            {results['text_input'] && (
              <motion.div
                className="mb-8 p-6 bg-blue-500/5 border border-blue-500/20 rounded-lg"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <h3 className="text-lg font-semibold text-blue-400 mb-4">
                  📄 Previous Text Analysis
                </h3>
                <div className="bg-black/40 rounded p-4 space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-gray-400 text-xs">Risk Score</p>
                      <p
                        className={`text-lg font-bold ${getRiskColor(
                          results['text_input'].final.risk_color
                        )}`}
                      >
                        {results['text_input'].final.risk_score.toFixed(1)}/100
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">Risk Level</p>
                      <p
                        className={`text-lg font-bold ${getRiskColor(
                          results['text_input'].final.risk_color
                        )}`}
                      >
                        {results['text_input'].final.risk_level}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate('/results', { state: { result: results['text_input'] } })}
                      className="flex-1 py-2 px-3 bg-blue-500/20 border border-blue-500 text-blue-400 rounded font-semibold hover:bg-blue-500/30 transition text-sm"
                    >
                      View Full Report
                    </button>
                    <button
                      onClick={() => {
                        setTextResult(null);
                        const updated = { ...results };
                        delete updated['text_input'];
                        setResults(updated);
                      }}
                      className="py-2 px-3 bg-red-500/20 border border-red-500 text-red-400 rounded font-semibold hover:bg-red-500/30 transition text-sm"
                    >
                      Clear
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
            <div className="space-y-4">
              {/* Text Input Area */}
              <div>
                <label className="block text-sm font-semibold text-green-400 mb-2">
                  Paste Text Content
                </label>
                <textarea
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Paste email content, message, URL, or any suspicious text here..."
                  className="w-full h-48 bg-black/40 border border-green-500/30 rounded-lg p-4 text-white placeholder-gray-600 focus:border-green-500 focus:outline-none resize-vertical"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Supports: Plain text, email content, URLs, messages, logs, code snippets
                </p>
              </div>

              {/* Analyze Button */}
              <button
                onClick={handleAnalyzeText}
                disabled={!textInput.trim() || textAnalyzing}
                className={`w-full py-3 px-4 rounded font-semibold transition ${
                  textAnalyzing || !textInput.trim()
                    ? 'bg-green-500/10 border border-green-500/30 text-green-500/50 cursor-not-allowed'
                    : 'bg-green-500/20 border border-green-500 text-green-500 hover:bg-green-500/30'
                }`}
              >
                {textAnalyzing ? (
                  <div className="flex items-center justify-center gap-2">
                    <Loader className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </div>
                ) : (
                  'Analyze Text'
                )}
              </button>

              {/* Analysis Progress */}
              {textAnalyzing && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4"
                >
                  <div className="grid grid-cols-4 gap-2 mb-3">
                    {['Layer 0', 'Layer 1', 'Layer 2', 'Layer 3'].map((layer, idx) => {
                      const isActive = idx === textCurrentLayer;
                      const isComplete = idx < textCurrentLayer;
                      return (
                        <div key={idx} className="flex flex-col items-center gap-1">
                          <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all ${
                              isComplete
                                ? 'bg-green-500 text-black'
                                : isActive
                                ? 'bg-blue-500 text-white animate-pulse'
                                : 'bg-gray-700 text-gray-400'
                            }`}
                          >
                            {isComplete ? '✓' : idx + 1}
                          </div>
                          <p
                            className={`text-xs font-semibold ${
                              isActive || isComplete ? 'text-white' : 'text-gray-400'
                            }`}
                          >
                            {layer}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                  <p className="text-xs text-gray-400 text-center">
                    {textCurrentLayer === 0 && 'Starting analysis...'}
                    {textCurrentLayer === 1 && 'Analyzing Layer 0 (Privacy)...'}
                    {textCurrentLayer === 2 && 'Analyzing Layer 1 (Heuristics)...'}
                    {textCurrentLayer === 3 && 'Analyzing Layer 2 (ML)...'}
                    {textCurrentLayer === 4 && 'Processing Layer 3 (LLM)...'}
                  </p>
                </motion.div>
              )}

              {/* Results Preview */}
              {textResult && !textAnalyzing && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="bg-green-500/5 border border-green-500/20 rounded-lg p-4 space-y-3"
                >
                  {/* Risk Score and Level */}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-gray-400 text-xs">Risk Score</p>
                      <p
                        className={`text-lg font-bold ${getRiskColor(
                          textResult.final.risk_color
                        )}`}
                      >
                        {textResult.final.risk_score.toFixed(1)}/100
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">Risk Level</p>
                      <p
                        className={`text-lg font-bold ${getRiskColor(
                          textResult.final.risk_color
                        )}`}
                      >
                        {textResult.final.risk_level}
                      </p>
                    </div>
                  </div>

                  {/* Layer 3 Explanation */}
                  <div className="bg-black/40 rounded p-3 border border-green-500/10">
                    <p className="text-gray-400 text-xs font-semibold mb-1">
                      Layer 3 (LLM) Analysis
                    </p>
                    <p className="text-gray-300 text-xs leading-relaxed">
                      {textResult.layer3_scoring?.reasoning ||
                        textResult.final.reasoning}
                    </p>
                  </div>

                  {/* Decision */}
                  <div>
                    <p className="text-gray-400 text-xs">Decision</p>
                    <p className="text-white text-sm font-semibold">
                      {textResult.final.decision}
                    </p>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setTextInput('');
                        setTextResult(null);
                      }}
                      className="flex-1 py-2 px-3 bg-gray-500/20 border border-gray-500 text-gray-400 rounded font-semibold hover:bg-gray-500/30 transition text-sm"
                    >
                      Clear
                    </button>
                    <button
                      onClick={handleViewTextResults}
                      className="flex-1 py-2 px-3 bg-green-500/20 border border-green-500 text-green-500 rounded font-semibold hover:bg-green-500/30 transition text-sm"
                    >
                      View Full Analysis
                    </button>
                  </div>
                </motion.div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
