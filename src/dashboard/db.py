"""
db.py
SQLite Database Abstraction for ML-Based Qualitative Research Analysis System.
Manages persistent storage for Projects, Documents, Paragraphs, Coded Segments,
Codebooks, Candidate Themes, Framework Mappings, Contradictions, and Researcher Validations.
"""

import os
import sqlite3
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DB_PATH = os.path.join(OUTPUTS_DIR, "research.db")

def get_db_connection() -> sqlite3.Connection:
    target_path = DB_PATH
    if os.environ.get("VERCEL") or not os.access(os.path.dirname(DB_PATH) or ".", os.W_OK):
        tmp_dir = "/tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        target_path = os.path.join(tmp_dir, "research.db")
        if not os.path.exists(target_path) and os.path.exists(DB_PATH):
            import shutil
            shutil.copy2(DB_PATH, target_path)

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Projects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        created_at TEXT
    )
    """)

    # 2. Documents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id TEXT UNIQUE NOT NULL,
        filename TEXT NOT NULL,
        title TEXT,
        doc_type TEXT NOT NULL, -- 'blog' or 'interview'
        word_count INTEGER DEFAULT 0,
        paragraph_count INTEGER DEFAULT 0,
        destination TEXT,
        traveller_context TEXT,
        familiarisation_summary TEXT, -- JSON format
        status TEXT DEFAULT 'Processed',
        created_at TEXT
    )
    """)

    # 3. Paragraphs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS paragraphs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id TEXT NOT NULL,
        paragraph_num INTEGER NOT NULL,
        text TEXT NOT NULL,
        FOREIGN KEY(doc_id) REFERENCES documents(doc_id)
    )
    """)

    # 4. Coded Segments (Initial Coding)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coded_segments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id TEXT NOT NULL,
        doc_type TEXT NOT NULL,
        paragraph_num INTEGER NOT NULL,
        text TEXT NOT NULL,
        code_name TEXT NOT NULL,
        code_definition TEXT,
        construct TEXT NOT NULL,
        sub_dimension TEXT,
        emotional_tone TEXT,
        valence TEXT,
        confidence REAL,
        matched_indicators TEXT, -- JSON array
        status TEXT DEFAULT 'Proposed', -- Proposed, Approved, Rejected, Modified
        reason TEXT,
        FOREIGN KEY(doc_id) REFERENCES documents(doc_id)
    )
    """)

    # 5. Codebook
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS codebook (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code_name TEXT UNIQUE NOT NULL,
        definition TEXT,
        evidence_sample TEXT,
        construct TEXT,
        frequency INTEGER DEFAULT 0,
        doc_count INTEGER DEFAULT 0,
        confidence REAL,
        status TEXT DEFAULT 'Approved' -- Proposed, Approved, Rejected
    )
    """)

    # 6. Candidate Themes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS themes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        theme_name TEXT UNIQUE NOT NULL,
        definition TEXT,
        related_codes TEXT, -- JSON array
        subthemes TEXT, -- JSON array
        blog_frequency INTEGER DEFAULT 0,
        interview_frequency INTEGER DEFAULT 0,
        total_evidence_count INTEGER DEFAULT 0,
        related_constructs TEXT, -- JSON array
        contradictory_evidence TEXT,
        confidence REAL,
        status TEXT DEFAULT 'Proposed', -- Proposed, Approved, Rejected, Merged, Split
        notes TEXT
    )
    """)

    # 7. Blog vs Interview Comparison
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comparisons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        theme_name TEXT NOT NULL,
        blogs_status TEXT, -- 'Present', 'Absent', 'Stronger'
        interviews_status TEXT,
        is_both BOOLEAN,
        difference_notes TEXT,
        type TEXT -- 'Convergence', 'Divergence', 'Blog-Specific', 'Interview-Specific'
    )
    """)

    # 8. Framework Mappings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS framework_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        theme_name TEXT NOT NULL,
        construct TEXT NOT NULL,
        evidence_quote TEXT NOT NULL,
        doc_id TEXT NOT NULL,
        paragraph_num INTEGER,
        interpretation_level TEXT NOT NULL -- 'Direct Evidence', 'Reasonable Interpretation', 'Theoretical Interpretation'
    )
    """)

    # 9. Contradictions & Negative Evidence
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contradictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        positive_quote TEXT,
        positive_doc TEXT,
        negative_quote TEXT,
        negative_doc TEXT,
        context_notes TEXT
    )
    """)

    # 10. Researcher Validations & Metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS validations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL, -- 'code', 'theme', 'segment'
        entity_id INTEGER NOT NULL,
        ai_suggestion TEXT,
        researcher_decision TEXT NOT NULL, -- 'Approved', 'Rejected', 'Modified'
        researcher_notes TEXT,
        timestamp TEXT
    )
    """)

    # 11. Model Testing Runs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_test_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_name TEXT NOT NULL,
        sample_size INTEGER,
        agreement_rate REAL,
        precision_score REAL,
        recall_score REAL,
        f1_score REAL,
        disagreements_summary TEXT, -- JSON
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()
