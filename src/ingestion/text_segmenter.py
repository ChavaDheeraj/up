"""
text_segmenter.py
Segments parsed documents into qualitative coding units (paragraphs and sentences)
with unique segment IDs and metadata for traceability in NVivo and audit trails.
"""

import re
from typing import List, Dict, Any

class TextSegmenter:
    def __init__(self, min_sentence_length: int = 20):
        self.min_sentence_length = min_sentence_length
        # Sentence splitting pattern accounting for abbreviations
        self.sentence_regex = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+')

    def segment_document(self, parsed_doc: Dict[str, Any], unit: str = "paragraph") -> List[Dict[str, Any]]:
        """
        Segments a parsed document into discrete coding units.
        `unit` can be 'paragraph' (recommended for thematic context) or 'sentence'.
        """
        source_id = parsed_doc.get("source_id", "doc")
        doc_title = parsed_doc.get("title", source_id)
        doc_type = parsed_doc.get("type", "blog")
        paragraphs = parsed_doc.get("paragraphs", [])

        segments = []
        global_seg_idx = 1

        for p_idx, p_data in enumerate(paragraphs, start=1):
            p_text = p_data.get("text", "").strip()
            p_tag = p_data.get("tag", "p")

            if unit == "paragraph":
                if len(p_text) >= self.min_sentence_length:
                    segments.append({
                        "segment_id": f"{source_id}_P{p_idx:03d}",
                        "source_id": source_id,
                        "doc_title": doc_title,
                        "doc_type": doc_type,
                        "unit": "paragraph",
                        "paragraph_num": p_idx,
                        "sentence_num": None,
                        "structural_tag": p_tag,
                        "text": p_text,
                        "word_count": len(p_text.split())
                    })
            elif unit == "sentence":
                raw_sentences = self.sentence_regex.split(p_text)
                for s_idx, s in enumerate(raw_sentences, start=1):
                    s_clean = s.strip()
                    if len(s_clean) >= self.min_sentence_length:
                        segments.append({
                            "segment_id": f"{source_id}_P{p_idx:03d}_S{s_idx:02d}",
                            "source_id": source_id,
                            "doc_title": doc_title,
                            "doc_type": doc_type,
                            "unit": "sentence",
                            "paragraph_num": p_idx,
                            "sentence_num": s_idx,
                            "structural_tag": p_tag,
                            "text": s_clean,
                            "word_count": len(s_clean.split())
                        })

        return segments
