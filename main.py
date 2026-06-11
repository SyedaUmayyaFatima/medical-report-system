"""
main.py
Factually Grounded Medical Report Generation with Zero-Hallucination Constraints
ITSOLERA PVT LTD — Generative AI Internship Screening Task
Author: Syeda Umayya Fatima
"""

import os
import sys
import json
import dotenv

from report_generator import ReportGenerator
from evaluator import ReportEvaluator
from pdf_report import generate_pdf_report


dotenv.load_dotenv()
API_KEY = API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")


IMAGE_PATH = "sample_xray.jpg"  

PATIENT_HISTORY = """
Patient: 58-year-old male
Chief Complaint: Persistent cough and shortness of breath for 3 weeks
Medical History: Hypertension, ex-smoker (20 pack-years)
Medications: Amlodipine 5mg
Vitals: BP 138/88, HR 92, SpO2 94% on room air
"""

PRIOR_REPORT = """
Previous CXR (3 months ago): No acute cardiopulmonary process identified.
Mild cardiomegaly noted. No pleural effusion.
"""


def main():
    print("=" * 60)
    print("  FACTUALLY GROUNDED MEDICAL REPORT GENERATION SYSTEM")
    print("  Zero-Hallucination Constraint Pipeline")
    print("  Author: Syeda Umayya Fatima | ITSOLERA Task")
    print("=" * 60)

    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n[ERROR] Please set your OpenAI API key!")
        print("Option 1: Create a .env file with: OPENAI_API_KEY=your_key_here")
        print("Option 2: Replace YOUR_API_KEY_HERE in main.py")
        sys.exit(1)

    if not os.path.exists(IMAGE_PATH):
        print(f"\n[ERROR] Image not found: {IMAGE_PATH}")
        print("Please provide a chest X-ray image named 'sample_xray.jpg'")
        print("Or update IMAGE_PATH variable in main.py")
        sys.exit(1)


    print("\n[STEP 1] Generating grounded medical report...")
    generator = ReportGenerator(api_key=API_KEY)
    report_data = generator.generate_report(
        image_path=IMAGE_PATH,
        patient_history=PATIENT_HISTORY,
        prior_report=PRIOR_REPORT
    )

    if "error" in report_data:
        print(f"[ERROR] Report generation failed: {report_data['error']}")
        sys.exit(1)

    # Step 2: Evaluate the report
    print("\n[STEP 2] Evaluating report quality...")
    evaluator = ReportEvaluator()
    scores = evaluator.evaluate(report_data)
    evaluator.print_scores()

   
    print("\n[STEP 3] Hallucination detection results...")
    generator.get_detector().print_report()

    
    print("\n[STEP 4] Evidence log summary...")
    logger = generator.get_logger()
    logger.print_summary()

    print("\n[STEP 5] Saving evidence log...")
    logger.save_log("evidence_log.json")

    
    with open("report_output.json", "w") as f:
        json.dump(report_data, f, indent=2)
    print("[INFO] Full report saved to: report_output.json")

   
    print("\n[STEP 6] Generating PDF report...")
    generate_pdf_report(
        report_data=report_data,
        scores=scores,
        evidence_log=logger.get_log(),
        output_path="medical_report.pdf",
        patient_history=PATIENT_HISTORY
    )

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("  Outputs:")
    print("    - report_output.json   (full report data)")
    print("    - evidence_log.json    (traceability log)")
    print("    - medical_report.pdf   (final PDF report)")
    print("=" * 60)


if __name__ == "__main__":
    main()
