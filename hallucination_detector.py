"""
hallucination_detector.py
Detects and prevents hallucinated claims in medical reports.
"""

import re


UNCERTAINTY_PHRASES = [
    "probably", "possibly", "might be", "could be", "appears to be",
    "suggests", "seems", "likely", "unlikely", "perhaps", "may indicate",
    "cannot rule out", "suspicious for", "concerning for"
]

HIGH_RISK_CLAIMS = [
    "cancer", "tumor", "malignant", "malignancy", "carcinoma",
    "metastasis", "fracture", "pneumonia", "effusion", "embolism",
    "infarction", "hemorrhage", "mass", "nodule", "lesion"
]


class HallucinationDetector:
    def __init__(self, confidence_threshold: float = 0.75):
        self.confidence_threshold = confidence_threshold
        self.flagged_claims = []

    def check_claim(self, claim: str, confidence: float, evidence: str) -> dict:
        """
        Check if a claim is grounded or potentially hallucinated.
        Returns a dict with: is_safe, reason, action
        """
        claim_lower = claim.lower()

      
        if confidence < self.confidence_threshold:
            return {
                "is_safe": False,
                "reason": f"Confidence {confidence:.2f} below threshold {self.confidence_threshold}",
                "action": "REFUSE"
            }

        
        contains_high_risk = any(word in claim_lower for word in HIGH_RISK_CLAIMS)
        if contains_high_risk and len(evidence.strip()) < 20:
            return {
                "is_safe": False,
                "reason": "High-risk medical claim lacks sufficient evidence",
                "action": "REFUSE"
            }

       
        contains_uncertainty = any(phrase in claim_lower for phrase in UNCERTAINTY_PHRASES)
        if contains_uncertainty:
            return {
                "is_safe": False,
                "reason": f"Claim contains uncertainty language — not suitable for grounded report",
                "action": "REFUSE_OR_QUALIFY"
            }

       
        if not evidence or evidence.strip() == "":
            return {
                "is_safe": False,
                "reason": "No evidence provided for claim",
                "action": "REFUSE"
            }

        return {
            "is_safe": True,
            "reason": "Claim is grounded with sufficient evidence",
            "action": "ACCEPT"
        }

    def flag_claim(self, claim: str, reason: str):
        self.flagged_claims.append({"claim": claim, "reason": reason})

    def get_flagged_claims(self):
        return self.flagged_claims

    def print_report(self):
        print(f"\n{'='*50}")
        print(f"HALLUCINATION DETECTION REPORT")
        print(f"{'='*50}")
        if not self.flagged_claims:
            print("No hallucinated claims detected.")
        else:
            for i, item in enumerate(self.flagged_claims, 1):
                print(f"{i}. FLAGGED: {item['claim']}")
                print(f"   Reason : {item['reason']}\n")
        print(f"{'='*50}\n")
