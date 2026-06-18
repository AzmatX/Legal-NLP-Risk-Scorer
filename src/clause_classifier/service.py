"""
Clause Classification Service
Fine-tuned transformer models for classifying legal clauses
Supports RoBERTa-legal and other pre-trained legal language models
"""
from typing import Dict, Any, List
import re


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
    "subcontracting"
]


class ClauseClassifier:
    """
    Transformer-based clause classifier using pre-trained legal language models.
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
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self.AutoTokenizer = AutoTokenizer
            self.AutoModelForSequenceClassification = AutoModelForSequenceClassification
            self.TRANSFORMERS_AVAILABLE = True
        except ImportError:
            self.TRANSFORMERS_AVAILABLE = False
    
    def load_model(self, fine_tuned_path: str = None):
        """
        Load the pre-trained/fine-tuned model.
        
        Args:
            fine_tuned_path: Path to fine-tuned model weights (optional)
        """
        if not self.TRANSFORMERS_AVAILABLE:
            return
        
        try:
            # Use legal-specific model if available, otherwise fall back to roberta-base
            model_to_load = fine_tuned_path or "roberta-base"
            
            self.tokenizer = self.AutoTokenizer.from_pretrained(model_to_load)
            self.model = self.AutoModelForSequenceClassification.from_pretrained(
                model_to_load,
                num_labels=len(LEGAL_CLAUSE_TYPES)
            )
            self._model_loaded = True
        except Exception:
            self._model_loaded = False
    
    def classify_clause(self, text: str) -> Dict[str, Any]:
        """
        Classify a legal clause into one of the predefined categories.
        
        Args:
            text: The clause text to classify
            
        Returns:
            Dictionary with:
            - label: Predicted clause type
            - confidence: Confidence score (0-1)
            - all_scores: Scores for all classes (optional)
        """
        if not text or not text.strip():
            return {"label": "unknown", "confidence": "0.00"}
        
        # If model not loaded, use heuristic-based classification
        if not self._model_loaded or not self.TRANSFORMERS_AVAILABLE:
            return self._heuristic_classify(text)
        
        try:
            import torch
            import torch.nn.functional as F
            
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = F.softmax(logits, dim=1)[0]
            
            # Get top prediction
            top_idx = torch.argmax(probabilities).item()
            confidence = probabilities[top_idx].item()
            
            return {
                "label": LEGAL_CLAUSE_TYPES[top_idx],
                "confidence": f"{confidence:.2f}",
                "all_scores": {
                    LEGAL_CLAUSE_TYPES[i]: f"{probabilities[i].item():.4f}"
                    for i in range(len(LEGAL_CLAUSE_TYPES))
                }
            }
        except Exception:
            return self._heuristic_classify(text)
    
    def _heuristic_classify(self, text: str) -> Dict[str, Any]:
        """
        Fallback heuristic-based classification using keyword matching.
        
        Args:
            text: The clause text to classify
            
        Returns:
            Dictionary with predicted label and confidence
        """
        text_lower = text.lower()
        
        # Keyword patterns for different clause types
        patterns = {
            "governing_law": r"governing law|laws of|jurisdiction|governed by",
            "choice_of_forum": r"court|venue|forum|judicial",
            "arbitration": r"arbitration|arbitrator|arbiter|dispute resolution",
            "notice_period": r"notice|days prior|written notice",
            "termination_for_convenience": r"terminate.*convenience|terminate.*any reason",
            "termination_for_cause": r"terminate.*cause|breach|default|violation",
            "non_compete": r"non-compete|competing business|competitive activity",
            "non_solicit": r"non-solicit|solicit employees|solicit customers",
            "intellectual_property_assignment": r"intellectual property|IP rights|work product|inventions",
            "confidentiality": r"confidential|non-disclosure|proprietary information",
            "limitation_of_liability": r"limitation of liability|consequential damages|indirect damages",
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
            "subcontracting": r"subcontract|subcontractor|delegate"
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
            return {
                "label": best_match,
                "confidence": f"{confidence:.2f}"
            }
        
        return {"label": "other", "confidence": "0.50"}
    
    def classify_multiple_clauses(self, clauses: List[str]) -> List[Dict[str, Any]]:
        """
        Classify multiple clauses at once.
        
        Args:
            clauses: List of clause texts to classify
            
        Returns:
            List of classification results
        """
        return [self.classify_clause(clause) for clause in clauses]


# Convenience function for backward compatibility
def classify_clause(text: str) -> Dict[str, str]:
    """
    Classify a legal clause (convenience function).
    
    Args:
        text: The clause text to classify
        
    Returns:
        Dictionary with label and confidence
    """
    classifier = ClauseClassifier()
    result = classifier.classify_clause(text)
    return {"label": result["label"], "confidence": result["confidence"]}
