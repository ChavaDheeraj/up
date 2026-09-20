"""
blog_parser.py
Extracts clean, structured text and metadata from raw HTML travel blogs,
safely stripping scripts, styling, nav, footer, comments, and boilerplate.
"""

import os
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class BlogParser:
    def __init__(self):
        self.drop_tags = ['script', 'style', 'noscript', 'iframe', 'svg', 'form', 'button', 'input', 'select', 'textarea', 'nav', 'footer', 'header']

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parses a single HTML file and returns clean article text, metadata, and paragraphs."""
        file_name = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        return self.parse_html(html_content, source_id=file_name)

    def parse_html(self, html_content: str, source_id: str = "unknown") -> Dict[str, Any]:
        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. Extract Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        else:
            title = source_id

        clean_title = re.sub(r'\s*[-|–—]\s*.*$', '', title).strip() or title

        # 2. Decompose scripts, styles, forms, iframes, nav, header, footer
        for tag in soup.find_all(self.drop_tags):
            try:
                tag.decompose()
            except Exception:
                pass

        # Decompose specific comment containers
        for c in soup.find_all(id=re.compile(r'^(comments|respond)', re.I)):
            try:
                c.decompose()
            except Exception:
                pass

        # 3. Extract substantive textual units
        raw_paragraphs = []
        for p in soup.find_all(['p', 'h2', 'h3', 'h4', 'blockquote', 'li']):
            # Skip if inside aside, comments, or share sections
            if p.find_parent(['aside', 'nav', 'footer', 'header']):
                continue
            if p.find_parent(class_=re.compile(r'(comment-list|comments-area|comment-respond|sharedaddy)', re.I)):
                continue

            text = re.sub(r'\s+', ' ', p.get_text().strip())

            # Filter out boilerplate, short lines, social widgets
            if len(text) >= 28 and not self._is_boilerplate(text):
                raw_paragraphs.append({
                    "tag": p.name,
                    "text": text
                })

        full_text = "\n\n".join([p["text"] for p in raw_paragraphs])
        word_count = len(full_text.split())

        return {
            "source_id": source_id,
            "title": clean_title,
            "raw_title": title,
            "type": "blog",
            "word_count": word_count,
            "paragraph_count": len(raw_paragraphs),
            "paragraphs": raw_paragraphs,
            "full_text": full_text
        }

    def _is_boilerplate(self, text: str) -> bool:
        """Heuristics to identify web boilerplate, cookie notices, and affiliate disclaimers."""
        low = text.lower()
        if 'cookie policy' in low or 'all rights reserved' in low or 'terms of use' in low:
            return True
        if 'sign up for' in low or 'subscribe to our' in low or 'affiliate commission' in low:
            return True
        if 'pin it for later' in low or 'leave a reply' in low or 'comments are closed' in low:
            return True
        if re.match(r'^(photo credit|read next|table of contents|posted on|updated on|sharing is caring|share this)', low):
            return True
        return False
