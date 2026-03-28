const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface FileSegregation {
  filename: string;
  type: string;
  size: number;
  status: "pending" | "processing" | "success" | "error";
  results?: {
    input_type: string;
    detected_type: string;
    content_preview: string;
    metadata?: Record<string, any>;
  };
  error?: string;
}

export interface AnalysisResponse {
  input: {
    type: string;
    content: string;
    metadata: Record<string, any>;
  };
  layer0: Record<string, any>;
  layer1: Record<string, any>;
  layer1_reasoning?: {
    flag_analysis?: Record<string, string>;
    overall_assessment?: string;
  };
  layer2: Record<string, any>;
  layer2_reasoning?: {
    text_analysis?: string;
    ml_patterns_detected?: string[];
    comparison_with_heuristics?: string;
    risk_level?: string;
    model_confidence_assessment?: string;
  };
  layer3_scoring: Record<string, any>;
  layer3_explanation?: {
    explanation?: string;
  };
  final: {
    risk_score: number;
    risk_level: string;
    risk_color: string;
    decision: string;
    confidence: number;
    context_type: string;
    reasoning?: string;
  };
}

export async function analyzeFile(file: File): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/analyze-file`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export function detectFileType(filename: string): string {
  const ext = filename.toLowerCase().split(".").pop() || "";

  if (["jpg", "jpeg", "png", "gif", "bmp", "webp"].includes(ext)) {
    return "image";
  } else if (["mp4", "avi", "mov", "mkv", "webm"].includes(ext)) {
    return "video";
  } else if (["mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"].includes(ext)) {
    return "audio";
  } else if (ext === "pdf") {
    return "document_pdf";
  } else if (ext === "docx" || ext === "doc") {
    return "document_word";
  } else if (ext === "txt") {
    return "document_text";
  } else if (["json", "log", "csv", "pcap"].includes(ext)) {
    return "data_" + ext;
  }
  return "unknown";
}

export function getFileTypeDescription(type: string): string {
  const descriptions: Record<string, string> = {
    image: "Image (OCR extraction)",
    video: "Video file",
    audio: "Audio (Whisper transcription)",
    document_pdf: "PDF Document",
    document_word: "Word Document",
    document_text: "Text File",
    data_json: "JSON Data",
    data_log: "Log File",
    data_csv: "CSV Data",
    data_pcap: "Network Capture",
    unknown: "Unknown file type",
  };
  return descriptions[type] || `File (${type})`;
}

// Color mapping - received from backend
const colorMap: Record<string, string> = {
  red: "text-red-500",
  orange: "text-orange-500",
  green: "text-green-500"
};

export function getRiskColor(colorCode: string): string {
  return colorMap[colorCode] || "text-green-500";
}

export function getRiskLevel(level: string): string {
  return level; // Already computed on backend
}
