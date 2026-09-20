"""
codebook_exporter.py
Exports qualitative coding outputs to NVivo-compatible XML, multi-sheet Excel (.xlsx),
and CSV formats for academic documentation and archival.
"""

import os
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Any

class CodebookExporter:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_excel_codebook(self, 
                              coded_segments: List[Dict[str, Any]], 
                              synthesis_data: Dict[str, Any],
                              cross_comparison: Dict[str, Any] = None,
                              filename: str = "codebook.xlsx") -> str:
        """Exports a multi-sheet Excel workbook containing the qualitative codebook and evidence."""
        out_path = os.path.join(self.output_dir, filename)

        # 1. Sheet 1: Codebook Taxonomy
        tax_rows = []
        for c in synthesis_data.get("final_themes", []):
            construct_name = c["construct"]
            c_def = c["theoretical_definition"]
            for st in c["sub_themes"]:
                tax_rows.append({
                    "Higher_Order_Construct": construct_name,
                    "Construct_Definition": c_def,
                    "Sub_Theme_Code": st["sub_theme_name"],
                    "Sub_Theme_Definition": st["definition"],
                    "Frequency_in_Corpus": st["frequency"],
                    "Document_Reach": st["document_reach"]
                })
        df_taxonomy = pd.DataFrame(tax_rows)

        # 2. Sheet 2: All Coded Segments
        seg_rows = []
        for s in coded_segments:
            seg_rows.append({
                "Segment_ID": s.get("segment_id"),
                "Source_Document": s.get("source_id"),
                "Document_Title": s.get("doc_title"),
                "Document_Type": s.get("doc_type", "blog"),
                "Is_Thematic": s.get("is_thematic"),
                "Primary_Construct": s.get("primary_construct"),
                "Sub_Dimension_Code": s.get("sub_dimension"),
                "Confidence_Score": s.get("confidence_score"),
                "Emotional_Tone": s.get("emotional_tone"),
                "Valence": s.get("valence"),
                "Matched_Indicators": ", ".join(s.get("matched_indicators", [])),
                "Verbatim_Quote": s.get("text")
            })
        df_segments = pd.DataFrame(seg_rows)

        # 3. Sheet 3: Construct Frequencies
        freq_rows = []
        for c, freq in synthesis_data.get("construct_frequencies", {}).items():
            freq_rows.append({
                "Construct": c,
                "Occurrence_Count": freq,
                "Percentage_of_Coded_Evidence": round((freq / max(1, synthesis_data.get("thematic_segments_count", 1))) * 100, 2)
            })
        df_freq = pd.DataFrame(freq_rows)

        # 4. Sheet 4: Cross Dataset Comparison (if present)
        df_cross = pd.DataFrame()
        if cross_comparison and "comparison_matrix" in cross_comparison:
            df_cross = pd.DataFrame(cross_comparison["comparison_matrix"])

        # Write to Excel with styling
        with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
            df_taxonomy.to_excel(writer, sheet_name="Codebook_Taxonomy", index=False)
            df_segments.to_excel(writer, sheet_name="Coded_Segments", index=False)
            df_freq.to_excel(writer, sheet_name="Construct_Frequencies", index=False)
            if not df_cross.empty:
                df_cross.to_excel(writer, sheet_name="Cross_Dataset_Comparison", index=False)

        # Also write standalone CSV of coded segments for easy scripting
        csv_path = os.path.join(self.output_dir, "coded_segments.csv")
        df_segments.to_csv(csv_path, index=False, encoding='utf-8')

        return out_path

    def export_nvivo_xml(self, synthesis_data: Dict[str, Any], filename: str = "nvivo_codebook.xml") -> str:
        """Exports an NVivo/QDA-compatible Codebook XML file for direct import into qualitative software."""
        out_path = os.path.join(self.output_dir, filename)

        root = ET.Element("Project", attrib={"xmlns": "http://www.qsrinternational.com/nvivo/codebook"})
        nodes = ET.SubElement(root, "Codes")

        for theme in synthesis_data.get("final_themes", []):
            construct_node = ET.SubElement(nodes, "Code", attrib={
                "name": theme["construct"],
                "description": theme["theoretical_definition"]
            })
            for st in theme["sub_themes"]:
                sub_node = ET.SubElement(construct_node, "Code", attrib={
                    "name": st["sub_theme_name"],
                    "description": st["definition"],
                    "frequency": str(st["frequency"])
                })

        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        return out_path
