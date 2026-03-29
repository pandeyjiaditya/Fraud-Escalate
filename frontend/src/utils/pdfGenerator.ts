import jsPDF from "jspdf";
import { AnalysisResponse } from "../services/analysisService";

export function generatePDFReport(
  analysis: AnalysisResponse,
  filename = "fraud_analysis_report.pdf",
) {
  const doc = new jsPDF();
  let yPosition = 15;
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 15;
  const contentWidth = pageWidth - 2 * margin;
  const lineHeight = 6;

  // Helper function to add text with wrapping
  const addWrappedText = (
    text: string,
    x: number,
    y: number,
    maxWidth: number,
    fontSize: number = 10,
  ) => {
    doc.setFontSize(fontSize);
    const lines = doc.splitTextToSize(text, maxWidth);
    doc.text(lines, x, y);
    return y + lines.length * lineHeight;
  };

  // Helper function to check page break
  const checkPageBreak = (spaceNeeded: number) => {
    if (yPosition + spaceNeeded > pageHeight - 10) {
      doc.addPage();
      yPosition = margin;
    }
  };

  // Header
  doc.setFontSize(20);
  doc.setFont(undefined, "bold");
  doc.text("FRAUD DETECTION ANALYSIS REPORT", margin, yPosition);
  yPosition += 12;

  doc.setFontSize(10);
  doc.setFont(undefined, "normal");
  const timestamp = new Date().toLocaleString();
  doc.text(`Generated: ${timestamp}`, margin, yPosition);
  yPosition += 8;

  // Separator line
  doc.setDrawColor(50, 205, 50);
  doc.line(margin, yPosition, pageWidth - margin, yPosition);
  yPosition += 8;

  // Risk Summary Section
  checkPageBreak(40);
  doc.setFontSize(13);
  doc.setFont(undefined, "bold");
  doc.text("RISK ASSESSMENT SUMMARY", margin, yPosition);
  yPosition += 8;

  doc.setFontSize(11);
  doc.setFont(undefined, "bold");
  const riskScore = analysis.final.risk_score.toFixed(1);
  doc.setTextColor(
    analysis.final.risk_color === "red"
      ? 255
      : analysis.final.risk_color === "orange"
        ? 255
        : 0,
    analysis.final.risk_color === "red"
      ? 0
      : analysis.final.risk_color === "orange"
        ? 165
        : 128,
    0,
  );
  doc.text(`Risk Score: ${riskScore}/100`, margin, yPosition);
  yPosition += 7;

  doc.setTextColor(0, 0, 0);
  doc.setFont(undefined, "normal");
  doc.text(`Risk Level: ${analysis.final.risk_level}`, margin, yPosition);
  yPosition += 7;
  doc.text(`Decision: ${analysis.final.decision}`, margin, yPosition);
  yPosition += 7;
  doc.text(
    `Confidence: ${(analysis.final.confidence * 100).toFixed(1)}%`,
    margin,
    yPosition,
  );
  yPosition += 10;

  // Layer Scores Section
  checkPageBreak(40);
  doc.setFontSize(12);
  doc.setFont(undefined, "bold");
  doc.text("LAYER SCORES", margin, yPosition);
  yPosition += 8;

  doc.setFontSize(10);
  doc.setFont(undefined, "normal");

  // Layer 1
  if (analysis.layer1) {
    doc.setFont(undefined, "bold");
    doc.text("Layer 1 - Heuristics", margin, yPosition);
    yPosition += 6;
    doc.setFont(undefined, "normal");
    doc.text(
      `Score: ${analysis.layer1.heuristic_score || 0}/100`,
      margin + 5,
      yPosition,
    );
    yPosition += 6;
    doc.text(
      `Confidence: ${((analysis.layer1.confidence || 0) * 100).toFixed(1)}%`,
      margin + 5,
      yPosition,
    );
    yPosition += 8;
  }

  // Layer 2
  if (analysis.layer2) {
    doc.setFont(undefined, "bold");
    doc.text("Layer 2 - Machine Learning", margin, yPosition);
    yPosition += 6;
    doc.setFont(undefined, "normal");
    doc.text(
      `Score: ${(analysis.layer2.ml_text_score || 0).toFixed(1)}/100`,
      margin + 5,
      yPosition,
    );
    yPosition += 6;
    doc.text(
      `Prediction: ${analysis.layer2.ml_prediction || "N/A"}`,
      margin + 5,
      yPosition,
    );
    yPosition += 6;
    doc.text(
      `Confidence: ${((analysis.layer2.ml_text_confidence || 0) * 100).toFixed(1)}%`,
      margin + 5,
      yPosition,
    );
    yPosition += 8;
  }

  // Layer 3
  if (analysis.layer3_scoring) {
    doc.setFont(undefined, "bold");
    doc.text("Layer 3 - LLM Analysis", margin, yPosition);
    yPosition += 6;
    doc.setFont(undefined, "normal");
    doc.text(
      `Score: ${(analysis.layer3_scoring.llm_score || 0).toFixed(1)}/100`,
      margin + 5,
      yPosition,
    );
    yPosition += 6;
    doc.text(
      `Confidence: ${((analysis.layer3_scoring.llm_confidence || 0) * 100).toFixed(1)}%`,
      margin + 5,
      yPosition,
    );
    yPosition += 8;
  }

  // Reasoning Section
  checkPageBreak(30);
  doc.setFontSize(12);
  doc.setFont(undefined, "bold");
  doc.text("ANALYSIS REASONING", margin, yPosition);
  yPosition += 8;

  doc.setFontSize(10);
  doc.setFont(undefined, "normal");
  if (analysis.layer3_scoring?.reasoning) {
    yPosition = addWrappedText(
      analysis.layer3_scoring.reasoning,
      margin,
      yPosition,
      contentWidth,
    );
    yPosition += 5;
  }

  // Final Summary
  checkPageBreak(30);
  doc.setFontSize(12);
  doc.setFont(undefined, "bold");
  doc.text("FINAL SUMMARY", margin, yPosition);
  yPosition += 8;

  doc.setFontSize(10);
  doc.setFont(undefined, "normal");
  if (analysis.final.reasoning) {
    yPosition = addWrappedText(
      analysis.final.reasoning,
      margin,
      yPosition,
      contentWidth,
    );
    yPosition += 5;
  }

  // Input Information
  checkPageBreak(30);
  doc.setFontSize(12);
  doc.setFont(undefined, "bold");
  doc.text("INPUT INFORMATION", margin, yPosition);
  yPosition += 8;

  doc.setFontSize(10);
  doc.setFont(undefined, "normal");
  doc.text(`Type: ${analysis.input.type || "N/A"}`, margin, yPosition);
  yPosition += 6;
  doc.text(
    `Context: ${analysis.final.context_type || "N/A"}`,
    margin,
    yPosition,
  );
  yPosition += 6;

  const contentPreview = analysis.input.content.substring(0, 200);
  yPosition = addWrappedText(
    `Content Preview: ${contentPreview}...`,
    margin,
    yPosition,
    contentWidth,
    9,
  );

  // Footer
  doc.setFontSize(8);
  doc.setTextColor(128, 128, 128);
  doc.text(
    `Report generated at ${new Date().toISOString()}`,
    margin,
    pageHeight - 10,
  );

  // Save the PDF
  doc.save(filename);
}

export function downloadAnalysisJSON(
  analysis: AnalysisResponse,
  filename = "fraud_analysis_data.json",
) {
  const dataStr = JSON.stringify(analysis, null, 2);
  const dataBlob = new Blob([dataStr], { type: "application/json" });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
