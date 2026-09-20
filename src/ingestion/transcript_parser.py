"""
transcript_parser.py
Parses semi-structured interview transcripts (TXT, DOCX, CSV, JSON),
isolating participant narratives from interviewer prompts to prevent coding bias.
"""

import os
import re
from typing import Dict, Any, List

class TranscriptParser:
    def __init__(self):
        # Regex patterns to detect speaker prefixes
        self.interviewer_pattern = re.compile(
            r'^(interviewer|researcher|moderator|int|q|res)\s*(\d*)\s*[:\-–—]', 
            re.IGNORECASE
        )
        self.participant_pattern = re.compile(
            r'^(participant|respondent|interviewee|student|part|p|resp)\s*(\d*)\s*[:\-–—]', 
            re.IGNORECASE
        )

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parses a transcript file (TXT, DOCX, JSON)."""
        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()

        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return self.parse_text(content, source_id=file_name)
        elif ext == '.docx':
            try:
                import docx
                doc = docx.Document(file_path)
                content = "\n".join([p.text for p in doc.paragraphs])
                return self.parse_text(content, source_id=file_name)
            except Exception as e:
                # Fallback to plain read if python-docx has issues
                return {"source_id": file_name, "error": str(e), "paragraphs": []}
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return self.parse_text(content, source_id=file_name)

    def parse_text(self, text: str, source_id: str = "interview_unknown") -> Dict[str, Any]:
        """Parses dialogue lines, segregating participant turns and interviewer prompts."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        turns = []
        current_speaker = "participant"  # default if not indicated
        current_speaker_id = "P"
        current_text = []

        participant_paragraphs = []
        all_turns = []

        for line in lines:
            int_match = self.interviewer_pattern.match(line)
            part_match = self.participant_pattern.match(line)

            if int_match:
                # Flush previous
                if current_text:
                    turn_content = " ".join(current_text)
                    all_turns.append({"speaker": current_speaker, "speaker_id": current_speaker_id, "text": turn_content})
                    if current_speaker == "participant" and len(turn_content) > 15:
                        participant_paragraphs.append({"tag": "participant_turn", "text": turn_content})
                    current_text = []
                current_speaker = "interviewer"
                current_speaker_id = int_match.group(0).rstrip(':-–— ')
                cleaned_line = self.interviewer_pattern.sub('', line).strip()
                if cleaned_line:
                    current_text.append(cleaned_line)

            elif part_match:
                # Flush previous
                if current_text:
                    turn_content = " ".join(current_text)
                    all_turns.append({"speaker": current_speaker, "speaker_id": current_speaker_id, "text": turn_content})
                    if current_speaker == "participant" and len(turn_content) > 15:
                        participant_paragraphs.append({"tag": "participant_turn", "text": turn_content})
                    current_text = []
                current_speaker = "participant"
                current_speaker_id = part_match.group(0).rstrip(':-–— ')
                cleaned_line = self.participant_pattern.sub('', line).strip()
                if cleaned_line:
                    current_text.append(cleaned_line)
            else:
                current_text.append(line)

        # Flush final turn
        if current_text:
            turn_content = " ".join(current_text)
            all_turns.append({"speaker": current_speaker, "speaker_id": current_speaker_id, "text": turn_content})
            if current_speaker == "participant" and len(turn_content) > 15:
                participant_paragraphs.append({"tag": "participant_turn", "text": turn_content})

        # If no explicit markers were found, treat all substantive paragraphs as participant statements
        if not participant_paragraphs:
            for line in lines:
                if len(line) > 25:
                    participant_paragraphs.append({"tag": "p", "text": line})

        full_participant_text = "\n\n".join([p["text"] for p in participant_paragraphs])

        return {
            "source_id": source_id,
            "title": f"Interview Transcript - {source_id}",
            "type": "interview",
            "speaker_turns_count": len(all_turns),
            "participant_turns_count": len(participant_paragraphs),
            "word_count": len(full_participant_text.split()),
            "paragraphs": participant_paragraphs,
            "full_text": full_participant_text,
            "turns": all_turns
        }
