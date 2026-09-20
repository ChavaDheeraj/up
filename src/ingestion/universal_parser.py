"""
universal_parser.py
Universal file ingestion engine supporting DOCX, PDF, TXT, HTML, and CSV documents
for qualitative thematic analysis.
"""

import os
import io
import re
from typing import Dict, Any, List
from .blog_parser import BlogParser
from .transcript_parser import TranscriptParser

class UniversalParser:
    def __init__(self):
        self.blog_parser = BlogParser()
        self.transcript_parser = TranscriptParser()

    def parse_file_bytes(self, filename: str, content_bytes: bytes, doc_type: str = "blog") -> Dict[str, Any]:
        """Parses file content from raw bytes based on file extension."""
        ext = os.path.splitext(filename)[1].lower()
        title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()

        if ext == ".docx":
            return self._parse_docx(filename, content_bytes, title, doc_type)
        elif ext == ".pdf":
            return self._parse_pdf(filename, content_bytes, title, doc_type)
        elif ext in [".html", ".htm"]:
            return self._parse_html(filename, content_bytes, title)
        elif ext == ".csv":
            return self._parse_csv(filename, content_bytes, title, doc_type)
        else: # Default to plain text (.txt, .md, etc.)
            return self._parse_txt(filename, content_bytes, title, doc_type)

    def _parse_docx(self, filename: str, content_bytes: bytes, title: str, doc_type: str) -> Dict[str, Any]:
        import docx
        doc = docx.Document(io.BytesIO(content_bytes))
        paragraphs = []
        for p in doc.paragraphs:
            text = re.sub(r'\s+', ' ', p.text.strip())
            if len(text) >= 25:
                paragraphs.append({"tag": "p", "text": text})

        full_text = "\n\n".join([p["text"] for p in paragraphs])
        if doc_type == "interview":
            return self.transcript_parser.parse_text(full_text, source_id=filename)

        return {
            "source_id": filename,
            "title": title,
            "type": doc_type,
            "word_count": len(full_text.split()),
            "paragraph_count": len(paragraphs),
            "paragraphs": paragraphs,
            "full_text": full_text
        }

    def _parse_pdf(self, filename: str, content_bytes: bytes, title: str, doc_type: str) -> Dict[str, Any]:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(content_bytes))
        extracted_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                extracted_text.append(t)
        
        raw_full = "\n\n".join(extracted_text)
        paragraphs = []
        # Split by double newline or large breaks
        for block in re.split(r'\n\s*\n', raw_full):
            clean = re.sub(r'\s+', ' ', block.strip())
            if len(clean) >= 28:
                paragraphs.append({"tag": "p", "text": clean})

        full_text = "\n\n".join([p["text"] for p in paragraphs])
        if doc_type == "interview":
            return self.transcript_parser.parse_text(full_text, source_id=filename)

        return {
            "source_id": filename,
            "title": title,
            "type": doc_type,
            "word_count": len(full_text.split()),
            "paragraph_count": len(paragraphs),
            "paragraphs": paragraphs,
            "full_text": full_text
        }

    def _parse_html(self, filename: str, content_bytes: bytes, title: str) -> Dict[str, Any]:
        text_content = content_bytes.decode("utf-8", errors="ignore")
        return self.blog_parser.parse_html(text_content, source_id=filename)

    def _parse_txt(self, filename: str, content_bytes: bytes, title: str, doc_type: str) -> Dict[str, Any]:
        text_content = content_bytes.decode("utf-8", errors="ignore")
        if doc_type == "interview":
            return self.transcript_parser.parse_text(text_content, source_id=filename)

        lines = [re.sub(r'\s+', ' ', l.strip()) for l in text_content.split('\n') if len(l.strip()) >= 25]
        paragraphs = [{"tag": "p", "text": l} for l in lines]
        full_text = "\n\n".join([p["text"] for p in paragraphs])

        return {
            "source_id": filename,
            "title": title,
            "type": doc_type,
            "word_count": len(full_text.split()),
            "paragraph_count": len(paragraphs),
            "paragraphs": paragraphs,
            "full_text": full_text
        }

    def _parse_csv(self, filename: str, content_bytes: bytes, title: str, doc_type: str) -> Dict[str, Any]:
        import pandas as pd
        df = pd.read_csv(io.BytesIO(content_bytes), encoding="utf-8", on_bad_lines='skip')
        # Find text columns
        text_cols = [c for c in df.columns if df[c].dtype == object]
        paragraphs = []
        for col in text_cols:
            for val in df[col].dropna():
                s = str(val).strip()
                if len(s) >= 25:
                    paragraphs.append({"tag": "csv_cell", "text": s})

        full_text = "\n\n".join([p["text"] for p in paragraphs])
        return {
            "source_id": filename,
            "title": title,
            "type": doc_type,
            "word_count": len(full_text.split()),
            "paragraph_count": len(paragraphs),
            "paragraphs": paragraphs,
            "full_text": full_text
        }
