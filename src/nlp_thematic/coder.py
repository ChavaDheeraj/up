"""
coder.py
Hybrid NLP & Machine Learning Coding Engine for qualitative thematic analysis.
Combines TF-IDF semantic vectorization, Cosine similarity against theoretical construct anchors,
rule-augmented pattern matching, and sentiment polarity profiling.
"""

import re
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .ontology import CONSTRUCT_TAXONOMY

class QualitativeCoder:
    def __init__(self, min_confidence_threshold: float = 0.12):
        self.min_confidence_threshold = min_confidence_threshold
        self.taxonomy = CONSTRUCT_TAXONOMY
        self.vectorizer = None
        self.anchor_matrix = None
        self.anchor_labels = [] # List of (construct, sub_dimension)

        # Basic sentiment / emotional polarity lexicon
        self.fear_words = set([
            "scared", "fear", "afraid", "terrified", "panic", "anxious", "anxiety", 
            "dread", "nervous", "vulnerable", "threat", "danger", "dangerous", "unsafe", 
            "threatened", "creepy", "horrifying", "uncomfortable"
        ])
        self.empowerment_words = set([
            "empowered", "empowering", "confident", "confidence", "proud", "capable", 
            "strength", "resilient", "resilience", "independent", "independence", 
            "liberating", "liberation", "freedom", "thrive", "brave", "courage", "flourish"
        ])
        self.caution_words = set([
            "careful", "cautious", "alert", "vigilant", "prepare", "prepared", 
            "boundary", "boundaries", "prevent", "precaution", "rule", "safety measure"
        ])

        self._build_anchor_corpus()

    def _build_anchor_corpus(self):
        """Constructs rich synthetic textual anchors for each theoretical construct and sub-dimension."""
        self.anchor_texts = []
        self.anchor_labels = []

        for construct_name, construct_data in self.taxonomy.items():
            for sub_name, sub_data in construct_data["sub_dimensions"].items():
                # Formulate anchor text containing description repeated + keywords
                kw_str = " ".join(sub_data["keywords"] * 3)
                anchor_text = f"{construct_name}. {construct_data['description']} {sub_name}. {sub_data['description']} {kw_str}"
                self.anchor_texts.append(anchor_text)
                self.anchor_labels.append((construct_name, sub_name))

    def fit(self, corpus_texts: List[str]):
        """Fits the TF-IDF vectorizer on the combined corpus of documents and theoretical anchors."""
        combined_texts = corpus_texts + self.anchor_texts
        # Use min_df=1 for small corpora to avoid eliminating all terms
        min_df = 2 if len(combined_texts) >= 20 else 1
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            max_df=0.95,
            min_df=min_df,
            sublinear_tf=True
        )
        self.vectorizer.fit(combined_texts)
        self.anchor_matrix = self.vectorizer.transform(self.anchor_texts)

    def code_segment(self, segment_text: str) -> Dict[str, Any]:
        """
        Codes a single qualitative text segment:
        - Assigns Primary Construct & Sub-dimension
        - Calculates Confidence Score
        - Determines Emotional Tone (Fear, Caution, Neutral, Empowerment)
        - Extracts Matched Indicators
        """
        clean_text = segment_text.lower()
        
        # 1. Lexicon / Rule Matching
        matched_indicators = []
        rule_scores = {}
        
        for idx, (construct_name, sub_name) in enumerate(self.anchor_labels):
            keywords = self.taxonomy[construct_name]["sub_dimensions"][sub_name]["keywords"]
            match_count = 0
            for kw in keywords:
                if " " in kw:
                    if kw in clean_text:
                        match_count += 2
                        matched_indicators.append(kw)
                else:
                    if re.search(r'\b' + re.escape(kw) + r'\b', clean_text):
                        match_count += 1
                        matched_indicators.append(kw)
            rule_scores[idx] = match_count

        # 2. Semantic Vector Similarity
        if self.vectorizer and self.anchor_matrix is not None:
            seg_vec = self.vectorizer.transform([segment_text])
            sim_scores = cosine_similarity(seg_vec, self.anchor_matrix)[0]
        else:
            sim_scores = np.zeros(len(self.anchor_labels))

        # 3. Hybrid Scoring Fusion
        final_scores = []
        for idx in range(len(self.anchor_labels)):
            cos_score = sim_scores[idx]
            r_score = rule_scores.get(idx, 0)
            # Fused score: cosine similarity + bonus for explicit keywords
            fused = cos_score + (r_score * 0.15)
            final_scores.append(fused)

        best_idx = int(np.argmax(final_scores))
        best_score = float(final_scores[best_idx])
        
        # 4. Sentiment & Emotional Polarity
        words_in_text = set(re.findall(r'\b\w+\b', clean_text))
        fear_matches = list(words_in_text.intersection(self.fear_words))
        empower_matches = list(words_in_text.intersection(self.empowerment_words))
        caution_matches = list(words_in_text.intersection(self.caution_words))

        if len(empower_matches) > len(fear_matches):
            emotional_tone = "Empowerment & Confidence"
            valence = "Positive"
        elif len(fear_matches) > len(empower_matches):
            emotional_tone = "Vulnerability & Fear"
            valence = "Negative"
        elif len(caution_matches) > 0:
            emotional_tone = "Calculated Caution & Vigilance"
            valence = "Protective"
        else:
            emotional_tone = "Reflective / Neutral"
            valence = "Neutral"

        # 5. Threshold Validation
        if best_score >= self.min_confidence_threshold and (rule_scores[best_idx] > 0 or sim_scores[best_idx] > 0.08):
            assigned_construct, assigned_sub = self.anchor_labels[best_idx]
            is_thematic = True
        else:
            assigned_construct = "General Travel Narrative"
            assigned_sub = "Descriptive / Contextual"
            is_thematic = False

        return {
            "primary_construct": assigned_construct,
            "sub_dimension": assigned_sub,
            "confidence_score": round(best_score, 4),
            "is_thematic": is_thematic,
            "emotional_tone": emotional_tone,
            "valence": valence,
            "matched_indicators": list(set(matched_indicators))[:6]
        }

    def code_all_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Codes a batch of segments and returns enriched segment records."""
        # Fit on segments texts first if not already fitted
        texts = [s["text"] for s in segments]
        if self.vectorizer is None:
            self.fit(texts)

        coded_segments = []
        for s in segments:
            res = self.code_segment(s["text"])
            enriched = {**s, **res}
            coded_segments.append(enriched)
        return coded_segments
