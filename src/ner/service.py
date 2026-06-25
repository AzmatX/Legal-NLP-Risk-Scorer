"""
Named Entity Recognition (NER) for Legal Documents.

This module uses spaCy to extract legal entities including organizations, dates,
monetary values, parties, and other legally significant entities from contract text.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import spacy
    SPACY_AVAILABLE = True
    logger.info("spaCy successfully loaded for NER processing")
except ImportError as e:
    SPACY_AVAILABLE = False
    logger.warning(f"spaCy not available: {e}. Some NER features will be limited.")


# Predefined legal entity types to extract
LEGAL_ENTITY_TYPES = {
    "ORG": "Organizations",
    "DATE": "Dates",
    "MONEY": "Monetary Values",
    "PERSON": "Persons/Parties",
    "GPE": "Geopolitical Entities",
    "LAW": "Laws/Regulations",
    "TIME": "Time expressions",
    "PERCENT": "Percentages",
    "QUANTITY": "Quantities",
    "CARDINAL": "Numbers/Cardinals",
    "ORDINAL": "Ordinal Numbers",
    "EVENT": "Events",
    "WORK_OF_ART": "Titles/Works",
    "PRODUCT": "Products",
    "LANGUAGE": "Languages",
    "NORP": "Nationalities/Religious/Political Groups",
    "FAC": "Facilities",
    "LOC": "Locations"
}

# Legal-specific entity patterns for enhanced extraction
LEGAL_PATTERNS = {
    "CONTRACT_PARTIES": ["Party A", "Party B", "Licensor", "Licensee", "Buyer", "Seller", 
                         "Lessee", "Lessor", "Contractor", "Client", "Provider", "Recipient"],
    "LEGAL_CURRENCY": ["USD", "EUR", "GBP", "$", "€", "£", "dollars", "euros"],
    "LEGAL_DATES": ["effective date", "execution date", "termination date", "expiration date"]
}


class NERProcessor:
    """
    Named Entity Recognition processor for legal documents.
    
    Provides comprehensive entity extraction with support for custom patterns,
    entity filtering, and batch processing.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the NER processor.
        
        Args:
            model_name: Name of the spaCy model to use
        """
        self.model_name = model_name
        self.nlp = None
        self._model_loaded = False
        
        if SPACY_AVAILABLE:
            self._load_model()
        else:
            logger.warning("spaCy not available, NER will use fallback mode")
    
    def _load_model(self) -> bool:
        """
        Load spaCy model, downloading if necessary.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if self._model_loaded and self.nlp is not None:
            return True
        
        try:
            # Try to load the specified model
            try:
                logger.info(f"Loading spaCy model: {self.model_name}")
                self.nlp = spacy.load(self.model_name)
                self._model_loaded = True
                logger.info(f"Successfully loaded spaCy model: {self.model_name}")
                return True
            except OSError:
                # Download if not available
                logger.info(f"Model {self.model_name} not found, downloading...")
                spacy.cli.download(self.model_name)
                self.nlp = spacy.load(self.model_name)
                self._model_loaded = True
                logger.info(f"Successfully downloaded and loaded: {self.model_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            self.nlp = None
            self._model_loaded = False
            return False
    
    def extract_entities(
        self, 
        text: str, 
        entity_types: set[str] | None = None,
        include_metadata: bool = True
    ) -> list[dict[str, Any]]:
        """
        Extract legal entities from text.
        
        Args:
            text: Input text to analyze
            entity_types: Optional set of entity types to filter (e.g., {"ORG", "DATE"})
            include_metadata: Whether to include additional metadata
            
        Returns:
            List of dictionaries containing entity information
        """
        if not text or not text.strip():
            logger.debug("Empty text provided for entity extraction")
            return []
        
        # Use fallback if spaCy not available
        if self.nlp is None:
            logger.warning("Using fallback entity extraction (spaCy not available)")
            return self._fallback_extraction(text, entity_types)
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        entities = []
        for ent in doc.ents:
            # Filter by entity types if specified
            if entity_types and ent.label_ not in entity_types:
                continue
            
            # Only include recognized legal entity types
            if ent.label_ not in LEGAL_ENTITY_TYPES:
                continue
            
            entity_data = {
                "text": ent.text,
                "label": ent.label_,
                "description": LEGAL_ENTITY_TYPES.get(ent.label_, "Unknown"),
                "start": ent.start_char,
                "end": ent.end_char
            }
            
            if include_metadata:
                entity_data.update({
                    "start_token": ent.start,
                    "end_token": ent.end,
                    "lemma": ent.lemma_ if hasattr(ent, 'lemma_') else None,
                    "confidence": 1.0  # spaCy doesn't provide confidence scores
                })
            
            entities.append(entity_data)
        
        logger.info(f"Extracted {len(entities)} entities from text ({len(text)} chars)")
        return entities
    
    def _fallback_extraction(
        self, 
        text: str, 
        entity_types: set[str] | None = None
    ) -> list[dict[str, Any]]:
        """
        Fallback entity extraction when spaCy is unavailable.
        
        Uses simple pattern matching for common legal terms.
        """
        entities = []
        
        # Look for contract parties
        for party in LEGAL_PATTERNS["CONTRACT_PARTIES"]:
            if party in text:
                if entity_types is None or "PERSON" in entity_types:
                    start = text.find(party)
                    entities.append({
                        "text": party,
                        "label": "PERSON",
                        "description": "Contract Party",
                        "start": start,
                        "end": start + len(party),
                        "fallback": True
                    })
        
        # Look for currency indicators
        for currency in LEGAL_PATTERNS["LEGAL_CURRENCY"]:
            if currency in text:
                if entity_types is None or "MONEY" in entity_types:
                    start = text.find(currency)
                    entities.append({
                        "text": currency,
                        "label": "MONEY",
                        "description": "Currency Indicator",
                        "start": start,
                        "end": start + len(currency),
                        "fallback": True
                    })
        
        return entities
    
    def extract_by_type(
        self, 
        text: str, 
        entity_type: str
    ) -> list[dict[str, Any]]:
        """
        Extract entities of a specific type.
        
        Args:
            text: Input text
            entity_type: Single entity type (e.g., "ORG", "DATE")
            
        Returns:
            List of entities matching the specified type
        """
        return self.extract_entities(text, entity_types={entity_type})
    
    def extract_parties(self, text: str) -> list[dict[str, Any]]:
        """
        Extract contract parties from text.
        
        Args:
            text: Contract text
            
        Returns:
            List of party entities (PERSON label)
        """
        return self.extract_by_type(text, "PERSON")
    
    def extract_dates(self, text: str) -> list[dict[str, Any]]:
        """
        Extract date entities from text.
        
        Args:
            text: Contract text
            
        Returns:
            List of date entities
        """
        return self.extract_by_type(text, "DATE")
    
    def extract_monetary_values(self, text: str) -> list[dict[str, Any]]:
        """
        Extract monetary values from text.
        
        Args:
            text: Contract text
            
        Returns:
            List of monetary value entities
        """
        return self.extract_by_type(text, "MONEY")
    
    def get_entity_summary(
        self, 
        text: str,
        deduplicate: bool = True
    ) -> dict[str, list[str]]:
        """
        Get a summary of entities grouped by type.
        
        Args:
            text: Input text
            deduplicate: Whether to remove duplicate entity texts
            
        Returns:
            Dictionary mapping entity types to lists of entity texts
        """
        entities = self.extract_entities(text)
        summary = {}
        
        for ent in entities:
            label = ent["label"]
            if label not in summary:
                summary[label] = []
            
            text_value = ent["text"]
            if deduplicate:
                if text_value not in summary[label]:
                    summary[label].append(text_value)
            else:
                summary[label].append(text_value)
        
        logger.info(f"Entity summary: {len(summary)} types found")
        return summary
    
    def process_batch(
        self, 
        texts: list[str],
        entity_types: set[str] | None = None
    ) -> list[list[dict[str, Any]]]:
        """
        Process multiple texts in batch.
        
        Args:
            texts: List of texts to process
            entity_types: Optional entity type filter
            
        Returns:
            List of entity lists, one per input text
        """
        results = []
        for i, text in enumerate(texts):
            try:
                entities = self.extract_entities(text, entity_types)
                results.append(entities)
                logger.debug(f"Processed text {i+1}/{len(texts)}: {len(entities)} entities")
            except Exception as e:
                logger.error(f"Error processing text {i}: {e}")
                results.append([])
        
        return results


# Legacy function wrappers for backward compatibility
_default_processor: NERProcessor | None = None


def _get_default_processor() -> NERProcessor:
    """Get or create the default NER processor."""
    global _default_processor
    if _default_processor is None:
        _default_processor = NERProcessor()
    return _default_processor


def extract_legal_entities(text: str) -> list[dict[str, Any]]:
    """
    Extract legal entities from text using spaCy NER.
    
    Args:
        text: Input text to analyze
        
    Returns:
        List of dictionaries containing entity information:
        - text: The entity text
        - label: Entity type (ORG, DATE, MONEY, etc.)
        - start: Start character position
        - end: End character position
        - description: Human-readable description
    """
    processor = _get_default_processor()
    return processor.extract_entities(text)


def extract_entities_by_type(text: str, entity_types: list[str]) -> list[dict[str, Any]]:
    """
    Extract only specific entity types from text.
    
    Args:
        text: Input text to analyze
        entity_types: List of entity types to extract (e.g., ["ORG", "DATE"])
        
    Returns:
        Filtered list of entities matching the specified types
    """
    processor = _get_default_processor()
    return processor.extract_entities(text, entity_types=set(entity_types))


def get_entity_summary(text: str) -> dict[str, list[str]]:
    """
    Get a summary of entities grouped by type.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary mapping entity types to lists of entity texts
    """
    processor = _get_default_processor()
    return processor.get_entity_summary(text)
