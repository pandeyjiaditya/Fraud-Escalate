import jsPDF from "jspdf";
import { AnalysisResponse } from "../services/analysisService";

export const generateAnalysisPDF = async (result: AnalysisResponse) => {
  try {
    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "mm",
      format: "a4",
    });

    const pageHeight = pdf.internal.pageSize.getHeight();
    const pageWidth = pdf.internal.pageSize.getWidth();
    const margin = 15;
    const contentWidth = pageWidth - 2 * margin;
    let yPosition = margin;

    const addTitle = (text: string) => {
      pdf.setFontSize(18);
      pdf.setFont("Arial", "bold");
      pdf.setTextColor(34, 197, 94);
      pdf.text(text, margin, yPosition);
      yPosition += 12;
    };

    const addSubtitle = (text: string) => {
      pdf.setFontSize(13);
      pdf.setFont("Arial", "bold");
      pdf.setTextColor(100, 100, 100);
      pdf.text(text, margin, yPosition);
      yPosition += 10;
    };

    const addLabel = (label: string, value: string) => {
      pdf.setFontSize(10);
      pdf.setFont("Arial", "bold");
      pdf.setTextColor(150, 150, 150);
      pdf.text(label, margin, yPosition);

      pdf.setFont("Arial", "normal");
      pdf.setTextColor(200, 200, 200);
      pdf.text(String(value), margin + 40, yPosition);
      yPosition += 7;
    };

    const addSection = (title: string) => {
      if (yPosition > pageHeight - 30) {
        pdf.addPage();
        yPosition = margin;
      }
      pdf.setFontSize(12);
      pdf.setFont("Arial", "bold");
      pdf.setTextColor(34, 197, 94);
      pdf.text(title, margin, yPosition);
      yPosition += 8;
    };

    const addMultilineText = (text: string, maxWidth = contentWidth) => {
      pdf.setFontSize(9);
      pdf.setFont("Arial", "normal");
      pdf.setTextColor(180, 180, 180);
      const lines = pdf.splitTextToSize(text, maxWidth);
      pdf.text(lines, margin, yPosition);
      yPosition += lines.length * 5 + 3;
    };

    const checkPageBreak = (spaceNeeded = 30) => {
      if (yPosition > pageHeight - spaceNeeded) {
        pdf.addPage();
        yPosition = margin;
      }
    };

    addTitle("NULLPOINT - Fraud Analysis Report");
    pdf.setFontSize(9);
    pdf.setTextColor(100, 100, 100);
    pdf.text(`Generated: ${new Date().toLocaleString()}`, margin, yPosition);
    yPosition += 10;
    pdf.setDrawColor(34, 197, 94);
    pdf.line(margin, yPosition, pageWidth - margin, yPosition);
    yPosition += 8;

    checkPageBreak(25);
    addSubtitle("RISK ASSESSMENT SUMMARY");

    const riskScore = result.final.risk_score;
    const decision = result.final.decision;

    addLabel("Risk Score:", `${riskScore.toFixed(1)}/100`);
    addLabel("Decision:", decision);
    const riskLevel =
      riskScore >= 70 ? "HIGH" : riskScore >= 40 ? "MEDIUM" : "LOW";
    addLabel("Risk Level:", riskLevel);
    yPosition += 5;

    checkPageBreak(30);
    addSection("Analysis Summary");
    if (result.final.reasoning) {
      addMultilineText(result.final.reasoning);
    }

    checkPageBreak(30);
    addSection("Layer 0 - Privacy & Normalization");
    if (result.layer0) {
      addLabel(
        "Clean Text Confidence:",
        `${(result.layer0.clean_text_confidence || 0).toFixed(1)}%`
      );
      addLabel("Words Analyzed:", String(result.layer0.word_count || 0));
      addLabel("PII Detected:", result.layer0.pii_detected ? "Yes" : "No");

      if (result.layer0.character_reduction) {
        yPosition += 2;
        pdf.setFontSize(9);
        pdf.setFont("Arial", "bold");
        pdf.setTextColor(150, 150, 150);
        pdf.text("Text Processing:", margin, yPosition);
        yPosition += 5;

        addLabel(
          "  Original Length:",
          `${result.layer0.character_reduction.original_length} chars`
        );
        addLabel(
          "  Cleaned Length:",
          `${result.layer0.character_reduction.cleaned_length} chars`
        );
        addLabel(
          "  Normalized Length:",
          `${result.layer0.character_reduction.normalized_length} chars`
        );
      }

      if (result.layer0.features) {
        yPosition += 2;
        const features = result.layer0.features;
        pdf.setFontSize(9);
        pdf.setFont("Arial", "bold");
        pdf.setTextColor(150, 150, 150);
        pdf.text("Detected Features:", margin, yPosition);
        yPosition += 5;

        addLabel("  URL Detected:", features.has_url ? "Yes" : "No");
        addLabel(
          "  Urgent Words:",
          features.has_urgent_words ? "Yes" : "No"
        );
        addLabel("  Numbers:", features.has_numbers ? "Yes" : "No");
        addLabel(
          "  Sensitive Keywords:",
          features.has_sensitive_keywords ? "Yes" : "No"
        );
      }
    }

    checkPageBreak(30);
    addSection("Layer 1 - Heuristic Patterns");
    if (result.layer1) {
      addLabel("Heuristic Score:", `${result.layer1.heuristic_score || 0}/150`);
      addLabel("Confidence:", `${(result.layer1.confidence || 0).toFixed(2)}`);
      addLabel("Flags Detected:", String(result.layer1.flags?.length || 0));

      if (result.layer1.flags && result.layer1.flags.length > 0) {
        yPosition += 3;
        pdf.setFontSize(9);
        pdf.setFont("Arial", "bold");
        pdf.setTextColor(150, 150, 150);
        pdf.text("Detected Flags:", margin, yPosition);
        yPosition += 5;

        result.layer1.flags.forEach((flag: string) => {
          addMultilineText(`• ${flag}`, contentWidth - 5);
        });
      }

      if (result.layer1_reasoning?.overall_assessment) {
        yPosition += 3;
        pdf.setFontSize(9);
        pdf.setFont("Arial", "bold");
        pdf.setTextColor(150, 150, 150);
        pdf.text("Overall Assessment:", margin, yPosition);
        yPosition += 4;
        addMultilineText(result.layer1_reasoning.overall_assessment);
      }
    }

    checkPageBreak(30);
    addSection("Layer 2 - Machine Learning Analysis");
    if (result.layer2) {
      addLabel(
        "ML Score:",
        `${result.layer2.ml_text_score?.toFixed(1) || 0}/100`
      );
      addLabel(
        "Confidence:",
        `${(result.layer2.ml_text_confidence || 0).toFixed(2)}`
      );
      addLabel(
        "Prediction:",
        `${(result.layer2.ml_prediction || "unknown").toUpperCase()}`
      );

      if (result.layer2.reasoning) {
        yPosition += 3;
        pdf.setFontSize(9);
        pdf.setFont("Arial", "bold");
        pdf.setTextColor(150, 150, 150);
        pdf.text("ML Reasoning:", margin, yPosition);
        yPosition += 4;
        addMultilineText(result.layer2.reasoning);
      }

      if (result.layer2_reasoning?.text_analysis) {
        yPosition += 3;
        pdf.setFontSize(9);
        pdf.setFont("Arial", "bold");
        pdf.setTextColor(150, 150, 150);
        pdf.text("Text Analysis:", margin, yPosition);
        yPosition += 4;
        addMultilineText(result.layer2_reasoning.text_analysis);
      }

      if (
        result.layer2_reasoning?.ml_patterns_detected &&
        Array.isArray(result.layer2_reasoning.ml_patterns_detected) &&
        result.layer2_reasoning.ml_patterns_detected.length > 0
      ) {
        checkPageBreak(15);
        yPosition += 3;
        pdf.setFontSize(9);
        pdf.setFont("Arial", "bold");
        pdf.setTextColor(150, 150, 150);
        pdf.text("Patterns Detected:", margin, yPosition);
        yPosition += 5;

        result.layer2_reasoning.ml_patterns_detected.forEach(
          (pattern: string) => {
            addMultilineText(`• ${pattern}`, contentWidth - 5);
          }
        );
      }
    }

    checkPageBreak(30);
    addSection("Layer 3 - LLM Analysis");
    if (result.layer3_scoring) {
      addLabel(
        "LLM Score:",
        `${result.layer3_scoring.llm_score?.toFixed(1) || 0}/100`
      );
      addLabel(
        "Confidence:",
        `${(result.layer3_scoring.llm_confidence || 0).toFixed(2)}`
      );

      if (result.layer3_scoring.reasoning) {
        yPosition += 3;
        pdf.setFontSize(9);
        pdf.setFont("Arial", "bold");
        pdf.setTextColor(150, 150, 150);
        pdf.text("LLM Reasoning:", margin, yPosition);
        yPosition += 4;
        addMultilineText(result.layer3_scoring.reasoning);
      }
    }

    if (result.layer3_explanation?.explanation) {
      checkPageBreak(15);
      yPosition += 3;
      pdf.setFontSize(9);
      pdf.setFont("Arial", "bold");
      pdf.setTextColor(150, 150, 150);
      pdf.text("Final Explanation:", margin, yPosition);
      yPosition += 4;
      addMultilineText(result.layer3_explanation.explanation);
    }

    checkPageBreak(20);
    addSection("Input Information");
    addLabel("Input Type:", result.input?.type || "Unknown");
    addLabel("Timestamp:", result.input?.metadata?.timestamp || "N/A");

    pdf.setFontSize(8);
    pdf.setTextColor(100, 100, 100);
    const pageCount = (pdf as any).internal.pages.length - 1;
    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      pdf.text(`Page ${i} of ${pageCount}`, pageWidth / 2, pageHeight - 10, {
        align: "center",
      });
    }

    const timestamp = new Date()
      .toISOString()
      .replace(/[:.]/g, "-")
      .slice(0, -5);
    const filename = `fraud-analysis-${timestamp}.pdf`;

    pdf.save(filename);
  } catch (error) {
    console.error("Error generating PDF:", error);
    throw new Error("Failed to generate PDF");
  }
};

export const downloadPDF = async (result: AnalysisResponse) => {
  await generateAnalysisPDF(result);
};
