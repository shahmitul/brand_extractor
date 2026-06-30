import re
import spacy
from typing import List, Dict, Set

class BrandExtractor:
    def __init__(self, brands_data: Dict):
        # Load English model for POS tagging
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        self.brand_lookup = {}
        self.aliases = []
        self._prepare_brand_data(brands_data)
        
        self.neg_patterns = [
            r"keep it simple",
            r"clear winner",
            r"clear results",
            r"dove-soft",
            r"always read"
        ]

    def _prepare_brand_data(self, data: Dict):
        all_brands = [data['target_brand']] + data['competitors']
        for brand in all_brands:
            canonical = brand['canonical']
            for alias in brand['aliases']:
                self.brand_lookup[alias.lower()] = canonical
                self.aliases.append(alias)
        
        self.aliases.sort(key=len, reverse=True)

    def _is_valid_mention(self, text: str, start: int, end: int, alias: str) -> bool:
        surface = text[start:end]
        context_window = text[max(0, start-15):min(len(text), end+20)].lower()

        # 1. Hard-coded phrase exclusions
        for pattern in self.neg_patterns:
            if re.search(pattern, context_window):
                return False

        # 2. English common word disambiguation (Always, Simple, Clear, Dove)
        common_words = {"always", "simple", "clear", "dove"}
        if alias.lower() in common_words:
            # Most brands in AI responses are Title Case
            if not surface[0].isupper():
                return False
            
            # Use NLP to check if it acts as a Proper Noun (PROPN)
            doc = self.nlp(text)
            for token in doc:
                if token.idx <= start < (token.idx + len(token.text)):
                    if token.pos_ in ["ADV", "ADJ", "VERB"]:
                        return False
        return True

    def extract(self, text: str) -> List[Dict]:
        results = []
        
        for alias in self.aliases:
            # Arabic vs English regex strategy
            is_arabic = bool(re.search(r'[\u0600-\u06FF]', alias))
            
            if is_arabic:
                pattern = re.compile(re.escape(alias))
            else:
                pattern = re.compile(r'\b' + re.escape(alias) + r'\b', re.IGNORECASE)

            for match in pattern.finditer(text):
                start, end = match.span()
                
                # Check for overlaps (don't extract 'Head' if it's part of 'Head & Shoulders')
                if any(start >= r['start'] and end <= r['end'] for r in results):
                    continue

                if self._is_valid_mention(text, start, end, alias):
                    results.append({
                        "canonical": self.brand_lookup[alias.lower()],
                        "surface": text[start:end],
                        "start": start,
                        "end": end
                    })
        
        return sorted(results, key=lambda x: x['start'])