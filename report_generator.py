"""
report_generator.py
Generates grounded radiology/pathology reports using GPT-4o Vision.
Every claim is linked to a source. Refuses unsupported claims.
"""

import base64
import json
from openai import OpenAI
from evidence_logger import EvidenceLogger
from hallucination_detector import HallucinationDetector


def encode_image(image_path: str) -> str:
    """Encode image to base64 for GPT-4o Vision."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


SYSTEM_PROMPT = """You are a highly cautious AI radiology assistant with zero hallucination tolerance.

STRICT RULES:
1. Only report findings you can DIRECTLY observe in the image.
2. Every finding must include WHERE in the image you see it (e.g., "lower left lobe", "right upper quadrant").
3. If you cannot clearly see something, say "Cannot determine from available image".
4. NEVER guess, infer, or assume findings not visible in the image.
5. NEVER use words like "probably", "possibly", "might", "could be", "suggests".
6. If patient history mentions a condition, only confirm it if you can SEE evidence in the image.
7. Partial generation with explicit uncertainty is required — fluent confabulation is NOT acceptable.

OUTPUT FORMAT (strict JSON):
{
  "findings": [
    {
      "claim": "specific finding statement",
      "image_region": "exact location in image",
      "confidence": 0.0-1.0,
      "evidence": "what exactly you see that supports this claim",
      "grounded": true
    }
  ],
  "refused_claims": [
    {
      "attempted_claim": "what could not be confirmed",
      "reason": "why it was refused"
    }
  ],
  "overall_impression": "brief grounded summary — only confirmed findings",
  "limitations": "what could not be determined and why"
}"""


class ReportGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.logger = EvidenceLogger()
        self.detector = HallucinationDetector(confidence_threshold=0.75)

    def generate_report(self, image_path: str, patient_history: str = "", prior_report: str = "") -> dict:
        """Generate a fully grounded medical report from an image."""

        print(f"\n[INFO] Analyzing image: {image_path}")
        base64_image = encode_image(image_path)

        # Build user message
        user_content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "high"
                }
            }
        ]

        context_text = "Analyze this medical image and generate a grounded report.\n"
        if patient_history:
            context_text += f"\nPatient History: {patient_history}"
        if prior_report:
            context_text += f"\nPrior Report: {prior_report}"
        context_text += "\n\nReturn ONLY valid JSON as specified. No extra text."

        user_content.append({"type": "text", "text": context_text})

        # Call GPT-4o Vision
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            max_tokens=1500,
            temperature=0.1  # Low temperature for factual consistency
        )

        raw_output = response.choices[0].message.content.strip()

        # Clean JSON if wrapped in markdown
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```")[1]
            if raw_output.startswith("json"):
                raw_output = raw_output[4:]

        try:
            report_data = json.loads(raw_output)
        except json.JSONDecodeError:
            print("[WARNING] Could not parse JSON response. Returning raw output.")
            return {"raw_output": raw_output, "error": "JSON parse failed"}

        # Process findings through hallucination detector
        validated_findings = []
        for finding in report_data.get("findings", []):
            check = self.detector.check_claim(
                claim=finding.get("claim", ""),
                confidence=finding.get("confidence", 0.0),
                evidence=finding.get("evidence", "")
            )

            if check["is_safe"]:
                self.logger.add_entry(
                    claim=finding["claim"],
                    source_type="image_region",
                    source_detail=finding.get("image_region", "unspecified"),
                    confidence=finding.get("confidence", 0.0)
                )
                validated_findings.append(finding)
            else:
                self.detector.flag_claim(finding["claim"], check["reason"])
                self.logger.add_refused_claim(finding["claim"], check["reason"])
                print(f"[REFUSED] {finding['claim']} — {check['reason']}")

        # Log refused claims from GPT itself
        for refused in report_data.get("refused_claims", []):
            self.logger.add_refused_claim(
                refused.get("attempted_claim", ""),
                refused.get("reason", "Insufficient evidence")
            )

        report_data["validated_findings"] = validated_findings
        report_data["hallucination_rate"] = self.logger.get_hallucination_rate()

        return report_data

    def get_logger(self):
        return self.logger

    def get_detector(self):
        return self.detector
