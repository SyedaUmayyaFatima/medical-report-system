# Factually Grounded Medical Report Generation
## Zero-Hallucination Constraint Pipeline
### ITSOLERA PVT LTD — Generative AI Internship Task
**Author: Syeda Umayya Fatima**

---

## Overview
This system generates radiology and pathology reports from medical images using GPT-4o Vision. Every clinical claim is explicitly linked to a verifiable source (image region, patient history, or prior report). The system refuses to generate any claim it cannot ground with evidence.

## Architecture
```
main.py                  ← Entry point / pipeline orchestrator
report_generator.py      ← GPT-4o Vision grounded report generation
hallucination_detector.py← Detects and refuses unsupported claims
evidence_logger.py       ← Logs every claim with its source evidence
evaluator.py             ← Scores report on factuality & grounding
pdf_report.py            ← Generates final PDF with all findings
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key
Create a `.env` file in the project folder:
```
OPENAI_API_KEY=your_key_here
```

### 3. Add Your Image
Place a chest X-ray image named `sample_xray.jpg` in the project folder.
Or update `IMAGE_PATH` in `main.py`.

### 4. Run the Pipeline
```bash
python main.py
```

## Output Files
| File | Description |
|------|-------------|
| `medical_report.pdf` | Full grounded PDF report |
| `report_output.json` | Structured report data |
| `evidence_log.json` | Traceability log per claim |

## Key Features
- **Zero Hallucination**: System refuses claims without sufficient evidence
- **Grounded Generation**: Every finding linked to specific image region
- **Evidence Attribution**: Full traceability log per generated claim
- **Penalty-Weighted Scoring**: Hallucinations penalized 2x vs missed findings
- **Uncertainty-Aware**: Explicit limitations section in every report

## Datasets Referenced
- MIMIC-CXR (PhysioNet — requires credentialed access)
- PadChest (BIMCV)
- OpenPath (Google Drive — link inactive at time of submission)

## Evaluation Metrics
- Factuality Score
- Grounding Score
- Hallucination Rate
- Clinical Reliability Score
- Refusal Rate
