"""
evaluator.py
Evaluates generated reports on factuality, grounding, and clinical reliability.
"""


class ReportEvaluator:
    def __init__(self):
        self.scores = {}

    def evaluate(self, report_data: dict) -> dict:
        """
        Evaluate a generated report and return penalty-weighted scores.
        Each hallucination deducts more than a missed finding.
        """
        validated = report_data.get("validated_findings", [])
        refused = report_data.get("refused_claims", [])
        hallucination_rate = report_data.get("hallucination_rate", 0.0)

        total_claims = len(validated) + len(refused)

        # Grounding score: how many claims have image region evidence
        grounded_count = sum(
            1 for f in validated
            if f.get("image_region") and f["image_region"] != "unspecified"
        )
        grounding_score = (grounded_count / len(validated)) if validated else 1.0

        # Confidence score: average confidence of validated findings
        if validated:
            avg_confidence = sum(f.get("confidence", 0) for f in validated) / len(validated)
        else:
            avg_confidence = 0.0

        # Penalty-weighted factuality score
        # Each hallucination penalizes 2x more than a missed finding
        hallucination_penalty = hallucination_rate * 2.0
        factuality_score = max(0.0, 1.0 - hallucination_penalty)

        # Refusal rate (higher = more cautious = better for zero-hallucination)
        refusal_rate = len(refused) / total_claims if total_claims > 0 else 0.0

        # Clinical reliability: combination of factuality + grounding
        clinical_reliability = (factuality_score * 0.6) + (grounding_score * 0.4)

        self.scores = {
            "factuality_score": round(factuality_score, 3),
            "grounding_score": round(grounding_score, 3),
            "avg_confidence": round(avg_confidence, 3),
            "hallucination_rate": round(hallucination_rate, 3),
            "refusal_rate": round(refusal_rate, 3),
            "clinical_reliability": round(clinical_reliability, 3),
            "total_claims_attempted": total_claims,
            "validated_findings": len(validated),
            "refused_claims": len(refused)
        }

        return self.scores

    def print_scores(self):
        print(f"\n{'='*50}")
        print(f"EVALUATION SCORES")
        print(f"{'='*50}")
        for key, value in self.scores.items():
            label = key.replace("_", " ").title()
            if isinstance(value, float):
                print(f"{label:<30}: {value:.3f}")
            else:
                print(f"{label:<30}: {value}")
        print(f"{'='*50}\n")
