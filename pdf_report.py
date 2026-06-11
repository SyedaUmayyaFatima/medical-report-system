"""
pdf_report.py
Generates a professional PDF report from the analysis results.
"""

from fpdf import FPDF
import datetime
import json


def clean_text(text: str) -> str:
    """Replace unicode characters unsupported by Helvetica."""
    return (text
        .replace('\u2014', '-')   # em dash
        .replace('\u2013', '-')   # en dash
        .replace('\u2018', "'")   # left single quote
        .replace('\u2019', "'")   # right single quote
        .replace('\u201c', '"')   # left double quote
        .replace('\u201d', '"')   # right double quote
        .replace('\u2022', '*')   # bullet
        .replace('\u00b0', ' degrees')  # degree sign
    )


class MedicalPDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(30, 80, 120)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "Factually Grounded Medical Report", fill=True, ln=True, align="C")
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 6, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Zero-Hallucination System", ln=True, align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()} | ITSOLERA Internship Task - Syeda Umayya Fatima", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(220, 235, 245)
        self.cell(0, 8, title, fill=True, ln=True)
        self.ln(2)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def finding_row(self, finding: dict, index: int):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 6, clean_text(f"Finding {index}: {finding.get('claim', 'N/A')}"), ln=True)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 5, clean_text(f"  Image Region : {finding.get('image_region', 'N/A')}"), ln=True)
        self.cell(0, 5, clean_text(f"  Evidence     : {finding.get('evidence', 'N/A')}"), ln=True)
        self.cell(0, 5, f"  Confidence   : {finding.get('confidence', 0):.2f}", ln=True)
        self.ln(3)


def generate_pdf_report(report_data: dict, scores: dict, evidence_log: list,
                        output_path: str, patient_history: str = ""):
    pdf = MedicalPDFReport()
    pdf.add_page()

    # Patient Info
    pdf.section_title("Patient Information")
    pdf.body_text(clean_text(f"Patient History: {patient_history if patient_history else 'Not provided'}"))

    # Overall Impression
    pdf.section_title("Overall Impression")
    pdf.body_text(clean_text(report_data.get("overall_impression", "No impression generated.")))

    # Validated Findings
    pdf.section_title("Validated Findings (Grounded)")
    findings = report_data.get("validated_findings", [])
    if findings:
        for i, finding in enumerate(findings, 1):
            pdf.finding_row(finding, i)
    else:
        pdf.body_text("No findings could be validated with sufficient evidence.")

    # Refused Claims
    pdf.section_title("Refused Claims (Insufficient Evidence)")
    refused = report_data.get("refused_claims", [])
    if refused:
        for item in refused:
            pdf.set_font("Helvetica", "", 9)
            claim = item.get("attempted_claim", item.get("claim", "N/A"))
            reason = item.get("reason", "N/A")
            pdf.multi_cell(0, 5, clean_text(f"  - REFUSED: {claim}\n    Reason: {reason}"))
            pdf.ln(1)
    else:
        pdf.body_text("No claims were refused.")

    # Limitations
    pdf.section_title("Limitations & Uncertainties")
    pdf.body_text(clean_text(report_data.get("limitations", "None specified.")))


    pdf.section_title("Evaluation Scores")
    for key, value in scores.items():
        label = key.replace("_", " ").title()
        val_str = f"{value:.3f}" if isinstance(value, float) else str(value)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"  {label}: {val_str}", ln=True)

    # Evidence Log
    pdf.add_page()
    pdf.section_title("Evidence Traceability Log")
    pdf.set_font("Helvetica", "", 8)
    for i, entry in enumerate(evidence_log, 1):
        grounded_str = "GROUNDED" if entry.get("grounded") else "REFUSED"
        pdf.multi_cell(0, 4, clean_text(
            f"{i}. [{grounded_str}] {entry.get('claim', 'N/A')}\n"
            f"   Source: {entry.get('source_type', 'N/A')} | {entry.get('source_detail', 'N/A')}\n"
            f"   Confidence: {entry.get('confidence', 0):.2f}\n"
        ))
        pdf.ln(1)

    pdf.output(output_path)
    print(f"[INFO] PDF report saved to: {output_path}")
