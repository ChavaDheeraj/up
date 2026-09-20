"""
doc_analyzer.py
End-to-End Single Document Thematic Analyzer.
Analyzes an uploaded file (DOCX, PDF, TXT, HTML, CSV), runs segmentation,
applies the hybrid ML qualitative coding engine, extracts salient quotes,
and generates summary analytics.
"""

import os
import io
import pandas as pd
from collections import Counter, defaultdict
from typing import Dict, Any, List, Tuple

from ..ingestion.universal_parser import UniversalParser
from ..ingestion.text_segmenter import TextSegmenter
from .coder import QualitativeCoder
from .ontology import CONSTRUCT_TAXONOMY

class DocumentThematicAnalyzer:
    def __init__(self):
        self.parser = UniversalParser()
        self.segmenter = TextSegmenter(min_sentence_length=28)
        self.coder = QualitativeCoder(min_confidence_threshold=0.12)
        self.taxonomy = CONSTRUCT_TAXONOMY

    def analyze_document_bytes(self, filename: str, content_bytes: bytes, doc_type: str = "blog") -> Dict[str, Any]:
        """Performs full thematic analysis on uploaded document bytes."""
        # 1. Ingest & Parse
        parsed_doc = self.parser.parse_file_bytes(filename, content_bytes, doc_type=doc_type)
        
        if not parsed_doc.get("paragraphs"):
            return {
                "error": "No substantive paragraphs or text could be extracted from this document.",
                "filename": filename
            }

        # 2. Segment
        segments = self.segmenter.segment_document(parsed_doc, unit="paragraph")
        if not segments:
            return {
                "error": "Document does not contain sufficiently long text segments for thematic coding.",
                "filename": filename
            }

        # 3. Code Segments
        coded_segments = self.coder.code_all_segments(segments)
        thematic_segments = [s for s in coded_segments if s.get("is_thematic")]

        # 4. Construct Frequencies & Percentages
        construct_counts = Counter([s["primary_construct"] for s in thematic_segments])
        sub_dim_counts = Counter([f"{s['primary_construct']} -> {s['sub_dimension']}" for s in thematic_segments])
        emotion_counts = Counter([s["emotional_tone"] for s in thematic_segments])

        # Fill all constructs in taxonomy even if zero
        construct_distribution = []
        for c_name, c_info in self.taxonomy.items():
            freq = construct_counts.get(c_name, 0)
            pct = round((freq / max(1, len(thematic_segments))) * 100, 1)
            construct_distribution.append({
                "construct": c_name,
                "frequency": freq,
                "percentage": pct,
                "definition": c_info["description"]
            })

        # Sort by frequency descending
        construct_distribution.sort(key=lambda x: x["frequency"], reverse=True)

        # 5. Extract Top Quotes per Construct
        quotes_by_construct = defaultdict(list)
        for s in thematic_segments:
            quotes_by_construct[s["primary_construct"]].append(s)

        top_evidence = []
        for c_data in construct_distribution:
            c_name = c_data["construct"]
            quotes = sorted(quotes_by_construct.get(c_name, []), key=lambda x: x.get("confidence_score", 0), reverse=True)
            if quotes:
                top_q = quotes[0]
                top_evidence.append({
                    "construct": c_name,
                    "sub_dimension": top_q.get("sub_dimension"),
                    "text": top_q.get("text"),
                    "confidence_score": top_q.get("confidence_score"),
                    "emotional_tone": top_q.get("emotional_tone"),
                    "matched_indicators": top_q.get("matched_indicators", []),
                    "segment_id": top_q.get("segment_id")
                })

        # 6. Dominant Constructs & Metrics
        dominant_construct = construct_distribution[0]["construct"] if construct_distribution and construct_distribution[0]["frequency"] > 0 else "None detected"
        dominant_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "Reflective / Neutral"

        thematic_density = round((len(thematic_segments) / max(1, len(coded_segments))) * 100, 1)

        return {
            "filename": filename,
            "title": parsed_doc.get("title", filename),
            "doc_type": doc_type,
            "word_count": parsed_doc.get("word_count", 0),
            "paragraph_count": parsed_doc.get("paragraph_count", 0),
            "total_segments": len(coded_segments),
            "thematic_segments_count": len(thematic_segments),
            "thematic_density_pct": thematic_density,
            "dominant_construct": dominant_construct,
            "dominant_emotional_tone": dominant_emotion,
            "construct_distribution": construct_distribution,
            "emotion_distribution": dict(emotion_counts),
            "top_evidence_quotes": top_evidence,
            "coded_segments": coded_segments
        }

    def generate_excel_bytes(self, analysis_result: Dict[str, Any]) -> bytes:
        """Generates an Excel workbook (.xlsx) for the analyzed document in memory."""
        output = io.BytesIO()
        
        # Sheet 1: Summary & Distribution
        summary_rows = [
            {"Metric": "Document Filename", "Value": analysis_result.get("filename")},
            {"Metric": "Document Title", "Value": analysis_result.get("title")},
            {"Metric": "Document Type", "Value": analysis_result.get("doc_type")},
            {"Metric": "Total Words", "Value": analysis_result.get("word_count")},
            {"Metric": "Analyzed Paragraphs", "Value": analysis_result.get("total_segments")},
            {"Metric": "Thematic Safety Segments", "Value": analysis_result.get("thematic_segments_count")},
            {"Metric": "Thematic Density (%)", "Value": f"{analysis_result.get('thematic_density_pct')}%"},
            {"Metric": "Dominant Construct", "Value": analysis_result.get("dominant_construct")},
            {"Metric": "Dominant Emotional Tone", "Value": analysis_result.get("dominant_emotional_tone")}
        ]
        df_summary = pd.DataFrame(summary_rows)
        df_constructs = pd.DataFrame(analysis_result.get("construct_distribution", []))

        # Sheet 2: Coded Segments
        seg_rows = []
        for s in analysis_result.get("coded_segments", []):
            seg_rows.append({
                "Segment_ID": s.get("segment_id"),
                "Is_Thematic": s.get("is_thematic"),
                "Primary_Construct": s.get("primary_construct"),
                "Sub_Dimension": s.get("sub_dimension"),
                "Confidence_Score": s.get("confidence_score"),
                "Emotional_Tone": s.get("emotional_tone"),
                "Valence": s.get("valence"),
                "Matched_Indicators": ", ".join(s.get("matched_indicators", [])),
                "Text": s.get("text")
            })
        df_segments = pd.DataFrame(seg_rows)

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name="Document_Overview", index=False)
            df_constructs.to_excel(writer, sheet_name="Construct_Distribution", index=False)
            df_segments.to_excel(writer, sheet_name="All_Coded_Segments", index=False)

        output.seek(0)
        return output.getvalue()
