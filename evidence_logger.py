"""
evidence_logger.py
Logs every clinical claim with its source evidence for traceability.
"""

import json
import datetime


class EvidenceLogger:
    def __init__(self):
        self.log = []

    def add_entry(self, claim: str, source_type: str, source_detail: str, confidence: float):
        """
        Add a grounded claim to the evidence log.
        source_type: 'image_region' | 'patient_history' | 'prior_report'
        """
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "claim": claim,
            "source_type": source_type,
            "source_detail": source_detail,
            "confidence": confidence,
            "grounded": True
        }
        self.log.append(entry)
        return entry

    def add_refused_claim(self, attempted_claim: str, reason: str):
        """Log a claim that was refused due to insufficient evidence."""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "claim": attempted_claim,
            "source_type": "REFUSED",
            "source_detail": reason,
            "confidence": 0.0,
            "grounded": False
        }
        self.log.append(entry)
        return entry

    def get_log(self):
        return self.log

    def save_log(self, filepath: str):
        with open(filepath, "w") as f:
            json.dump(self.log, f, indent=2)
        print(f"Evidence log saved to {filepath}")

    def get_hallucination_rate(self):
        if not self.log:
            return 0.0
        refused = sum(1 for e in self.log if not e["grounded"])
        return refused / len(self.log)

    def print_summary(self):
        total = len(self.log)
        grounded = sum(1 for e in self.log if e["grounded"])
        refused = total - grounded
        print(f"\n{'='*50}")
        print(f"EVIDENCE LOG SUMMARY")
        print(f"{'='*50}")
        print(f"Total claims attempted : {total}")
        print(f"Grounded claims        : {grounded}")
        print(f"Refused (no evidence)  : {refused}")
        print(f"Hallucination rate     : {self.get_hallucination_rate():.2%}")
        print(f"{'='*50}\n")
