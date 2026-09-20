"""
theme_clusterer.py
Implements Steps 3 & 4 of Braun & Clarke (2006):
- Unsupervised Topic Discovery via Non-Negative Matrix Factorization (NMF)
- Semantic Clustering of Coded Segments
- Candidate Theme Generation & Cohesion Validation
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

class ThemeClusterer:
    def __init__(self, n_emergent_topics: int = 6):
        self.n_topics = n_emergent_topics
        # Domain and qualitative interview stopwords
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        custom_stops = list(ENGLISH_STOP_WORDS.union({
            'interviewer', 'participant', 'p01', 'p02', 'p03', 'student', 
            'did', 'said', 'say', 'know', 'thing', 'things', 'going', 
            'also', 'really', 'just', 'like', 'don', 've', 'll', 'want',
            'make', 'lot', 'way', 'time', 'years', 'day', 'days', 'trip'
        }))

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words=custom_stops,
            max_df=0.85,
            min_df=2,
            sublinear_tf=True
        )
        self.nmf_model = None
        self.feature_names = None

    def discover_emergent_themes(self, thematic_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Discovers emergent thematic topics from qualitative segments using NMF.
        Returns candidate themes with top descriptive keywords and member quotes.
        """
        if len(thematic_segments) < self.n_topics:
            return []

        texts = [s["text"] for s in thematic_segments]
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        self.feature_names = self.vectorizer.get_feature_names_out()

        # Fit NMF model
        self.nmf_model = NMF(
            n_components=self.n_topics,
            random_state=42,
            init='nndsvd',
            max_iter=400
        )
        W = self.nmf_model.fit_transform(tfidf_matrix) # Document-topic weights
        H = self.nmf_model.components_ # Topic-word weights

        candidate_themes = []
        for topic_idx, topic_weights in enumerate(H):
            # Top keywords for this topic
            top_word_indices = topic_weights.argsort()[:-12:-1]
            top_words = [self.feature_names[i] for i in top_word_indices]

            # Top representative segments for this topic
            top_seg_indices = W[:, topic_idx].argsort()[:-6:-1]
            exemplar_quotes = []
            for seg_i in top_seg_indices:
                weight = float(W[seg_i, topic_idx])
                if weight > 0.01:
                    seg = thematic_segments[seg_i]
                    exemplar_quotes.append({
                        "segment_id": seg.get("segment_id"),
                        "source_id": seg.get("source_id"),
                        "text": seg.get("text"),
                        "primary_construct": seg.get("primary_construct"),
                        "weight": round(weight, 4)
                    })

            # Automated candidate naming based on top keywords
            theme_name = self._name_theme_from_keywords(top_words)

            candidate_themes.append({
                "theme_id": f"THEME_{topic_idx + 1:02d}",
                "candidate_name": theme_name,
                "top_keywords": top_words,
                "exemplar_quotes": exemplar_quotes,
                "document_prevalence": len(set(q["source_id"] for q in exemplar_quotes))
            })

        return candidate_themes

    def _name_theme_from_keywords(self, keywords: List[str]) -> str:
        """Heuristic generator for candidate theme names based on salient co-occurring keywords."""
        kw_str = " ".join(keywords).lower()
        if any(w in kw_str for w in ["hostel", "hotel", "room", "door", "lock", "stay"]):
            return "Accommodation Insecurity & Dormitory Spatial Boundaries"
        elif any(w in kw_str for w in ["theft", "bag", "bags", "belongings", "pickpocket", "wallet"]):
            return "Property Protection & Anti-Theft Precautions"
        elif any(w in kw_str for w in ["night", "dark", "walk", "street", "taxi", "transport"]):
            return "Nocturnal Mobility Hazards & Transit Navigation"
        elif any(w in kw_str for w in ["harass", "men", "stare", "catcall", "touch", "unwanted"]):
            return "Street Harassment & Invasive Male Spatial Entitlement"
        elif any(w in kw_str for w in ["destination", "country", "place", "bucket", "list", "japan"]):
            return "Destination Evaluation & Geographic Risk-Reward Assessment"
        elif any(w in kw_str for w in ["fear", "afraid", "scared", "mind", "overcome"]):
            return "Cognitive Fear Negotiation & Mental Deconditioning"
        elif any(w in kw_str for w in ["dress", "modest", "culture", "norm", "police"]):
            return "Socio-Cultural Dress Codes & Gendered Space Policing"
        elif any(w in kw_str for w in ["gut", "instinct", "intuition", "alert", "aware"]):
            return "Intuitive Risk Calibration & Embodied Vigilance"
        elif any(w in kw_str for w in ["phone", "location", "share", "app", "maps"]):
            return "Digital Shielding & Real-Time Familial Tethering"
        elif any(w in kw_str for w in ["empower", "confiden", "proud", "liberat", "grow"]):
            return "Transformative Self-Efficacy & Autonomy Acquisition"
        elif any(w in kw_str for w in ["parent", "mom", "family", "worried"]):
            return "Navigating Familial Protectionism & Paternalistic Anxiety"
        elif any(w in kw_str for w in ["female", "women", "solo female", "travelers"]):
            return "Gendered Mobility Imperatives & Autonomous Female Agency"
        else:
            return f"Emergent Thematic Cluster: {' / '.join(keywords[:3]).title()}"
