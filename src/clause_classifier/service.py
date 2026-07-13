"""
Clause Classification Service
Fine-tuned transformer models for classifying legal clauses.
Supports RoBERTa-legal and other pre-trained legal language models.

Now integrated with clause segmentation: per-clause classification,
with contract-level summary.
"""
# ✅ correct relative import – goes up to 'src', then into 'clause_segmentation'

import re
from typing import Any

# Import the segmentation module (supports both package execution styles)
try:
    from src.clause_segmentation import Clause, segment_contract
except ImportError:
    from clause_segmentation import Clause, segment_contract

# Legal clause types commonly found in contracts (CUAD dataset categories)
LEGAL_CLAUSE_TYPES = [
    "governing_law",
    "choice_of_forum",
    "arbitration",
    "notice_period",
    "termination_for_convenience",
    "termination_for_cause",
    "non_compete",
    "non_solicit",
    "intellectual_property_assignment",
    "confidentiality",
    "limitation_of_liability",
    "indemnification",
    "insurance",
    "warranty",
    "payment_terms",
    "force_majeure",
    "assignment",
    "entire_agreement",
    "amendment",
    "severability",
    "counterparts",
    "survival",
    "waiver",
    "publicity",
    "audit_rights",
    "data_protection",
    "subcontracting",
]


class ClauseClassifier:
    """
    Transformer-based clause classifier using pre-trained legal language models.
    Supports both single‑clause and full‑contract (segmented) classification.
    """

    def __init__(self, model_name: str = "roberta-base"):
        """
        Initialize the clause classifier.

        Args:
            model_name: Name of the pre-trained model to use
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._model_loaded = False

        # Try to load transformers
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            self.AutoTokenizer = AutoTokenizer
            self.AutoModelForSequenceClassification = AutoModelForSequenceClassification
            self.TRANSFORMERS_AVAILABLE = True
        except ImportError:
            self.TRANSFORMERS_AVAILABLE = False

    def load_model(self, fine_tuned_path: str | None = None):
        """
        Load the pre-trained/fine-tuned model.

        Args:
            fine_tuned_path: Path to fine-tuned model weights (optional)
        """
        if not self.TRANSFORMERS_AVAILABLE:
            return

        try:
            model_to_load = fine_tuned_path or "roberta-base"
            self.tokenizer = self.AutoTokenizer.from_pretrained(model_to_load)
            self.model = self.AutoModelForSequenceClassification.from_pretrained(
                model_to_load, num_labels=len(LEGAL_CLAUSE_TYPES)
            )
            self._model_loaded = True
        except Exception:
            self._model_loaded = False

    # ------------------------------------------------------------
    # Single clause classification (existing)
    # ------------------------------------------------------------
    def classify_clause(self, text: str) -> dict[str, Any]:
        """
        Classify a single legal clause.

        Args:
            text: The clause text to classify

        Returns:
            Dictionary with:
            - label: Predicted clause type
            - confidence: Confidence score (0-1)
            - all_scores: Optional scores for all classes
        """
        if not text or not text.strip():
            return {"label": "unknown", "confidence": "0.00"}

        # If model not loaded, use heuristic-based classification
        if not self._model_loaded or not self.TRANSFORMERS_AVAILABLE:
            return self._heuristic_classify(text)

        try:
            import torch
            import torch.nn.functional as F

            inputs = self.tokenizer(
                text, return_tensors="pt", truncation=True, max_length=512, padding=True
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = F.softmax(logits, dim=1)[0]

            top_idx = torch.argmax(probabilities).item()
            confidence = probabilities[top_idx].item()

            return {
                "label": LEGAL_CLAUSE_TYPES[top_idx],
                "confidence": f"{confidence:.2f}",
                "all_scores": {
                    LEGAL_CLAUSE_TYPES[i]: f"{probabilities[i].item():.4f}"
                    for i in range(len(LEGAL_CLAUSE_TYPES))
                },
            }
        except Exception:
            return self._heuristic_classify(text)

    def classify_multiple_clauses(self, clauses: list[str]) -> list[dict[str, Any]]:
        """Batch classify a list of clause texts."""
        return [self.classify_clause(clause) for clause in clauses]

    # ------------------------------------------------------------
    # Heuristic fallback (unchanged)
    # ------------------------------------------------------------
    def _heuristic_classify(self, text: str) -> dict[str, Any]:
        """Fallback heuristic-based classification using keyword matching."""
        text_lower = text.lower()

        patterns = {
            "governing_law": r"governing law|laws of|jurisdiction|governed by",
            "choice_of_forum": r"court|venue|forum|judicial",
            "arbitration": r"arbitration|arbitrator|arbiter|dispute resolution",
            "notice_period": r"notice|days prior|written notice",
            "termination_for_convenience": r"terminate.*convenience|terminate.*any reason",
            "termination_for_cause": r"terminate.*cause|breach|default|violation",
            "non_compete": r"non-compete|competing business|competitive activity",
            "non_solicit": r"non-solicit|solicit employees|solicit customers",
            "intellectual_property_assignment": (
                r"intellectual property|IP rights|work product|inventions"
            ),
            "confidentiality": r"confidential|non-disclosure|proprietary information",
            "limitation_of_liability": (
                r"limitation of liability|consequential damages|indirect damages"
            ),
            "indemnification": r"indemnif[y|ication]|hold harmless|defend against",
            "insurance": r"insurance|coverage|policy|insured",
            "warranty": r"warranty|representations|warrant",
            "payment_terms": r"payment|invoice|fees|compensation|consideration",
            "force_majeure": r"force majeure|act of god|unforeseeable|circumstances beyond",
            "assignment": r"assignment|transfer rights|assign",
            "entire_agreement": r"entire agreement|merger|integration|complete agreement",
            "amendment": r"amendment|modify|modification|change",
            "severability": r"severability|severable|invalid provision",
            "counterparts": r"counterparts|separate copies|executed separately",
            "survival": r"survival|survive termination|remain in effect",
            "waiver": r"waiver|waive|failure to enforce",
            "publicity": r"publicity|press release|public announcement",
            "audit_rights": r"audit|examination|records inspection",
            "data_protection": r"data protection|privacy|GDPR|personal data",
            "subcontracting": r"subcontract|subcontractor|delegate",
        }

        best_match = None
        best_score = 0
        for clause_type, pattern in patterns.items():
            matches = len(re.findall(pattern, text_lower))
            if matches > best_score:
                best_score = matches
                best_match = clause_type

        if best_match and best_score > 0:
            confidence = min(0.95, 0.5 + (best_score * 0.15))
            return {"label": best_match, "confidence": f"{confidence:.2f}"}

        return {"label": "other", "confidence": "0.50"}

    # ------------------------------------------------------------
    # NEW: Full contract classification (with segmentation)
    # ------------------------------------------------------------
    def classify_contract(self, contract_text: str) -> dict[str, Any]:
        """
        Classify each clause in a full contract after automatic segmentation.

        Returns:
            Dictionary with:
            - "clauses": list of per‑clause results (includes heading, text, label, confidence)
            - "summary": counts of each clause type
            - "risk_factors": list of high‑risk clause types present (optional)
        """
        # 1. Segment the contract
        clauses: list[Clause] = segment_contract(contract_text)

        # 2. Classify each clause
        results = []
        type_counts = {}
        for clause in clauses:
            classification = self.classify_clause(clause.text)
            result = {
                "heading": clause.heading,
                "text": clause.text,
                "start_char": clause.start_char,
                "end_char": clause.end_char,
                "label": classification.get("label", "unknown"),
                "confidence": classification.get("confidence", "0.00"),
            }
            results.append(result)

            # Count labels
            label = result["label"]
            type_counts[label] = type_counts.get(label, 0) + 1

        # 3. Build summary
        summary = {"total_clauses": len(results), "type_counts": type_counts}

        # 4. (Optional) Identify high‑risk clauses – e.g., termination, indemnification
        #    We'll treat 'termination_for_cause' and 'indemnification' as risk factors.
        risk_labels = {"termination_for_cause", "indemnification", "limitation_of_liability"}
        risk_factors = [r for r in results if r["label"] in risk_labels]

        return {
            "clauses": results,
            "summary": summary,
            "risk_factors": risk_factors,
            "risk_count": len(risk_factors),
        }


# ------------------------------------------------------------
# Convenience functions (backward compatible)
# ------------------------------------------------------------
def classify_clause(text: str) -> dict[str, str]:
    """Classify a single clause (convenience)."""
    classifier = ClauseClassifier()
    result = classifier.classify_clause(text)
    return {"label": result["label"], "confidence": result["confidence"]}


def classify_contract(contract_text: str) -> dict[str, Any]:
    """Classify all clauses in a full contract (convenience)."""
    classifier = ClauseClassifier()
    return classifier.classify_contract(contract_text)
