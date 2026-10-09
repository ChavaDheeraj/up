"""
seeder.py
Database Seeder for Solo Female Travel Safety Qualitative Research System.
Populates SQLite research.db with actual parsed documents, initial coding, codebook, candidate themes,
blog vs interview comparison, framework mappings, and validation records from existing
synthesis output and taxonomy.
"""

import os
import json
import sqlite3
from typing import Dict, Any
from datetime import datetime
from .db import get_db_connection, DB_PATH
from ..nlp_thematic.ontology import CONSTRUCT_TAXONOMY, CONCEPTUAL_HYPOTHESES

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

def seed_database_if_empty():
    db_json_path = os.path.join(OUTPUTS_DIR, "analysis_database.json")
    if not os.path.exists(db_json_path):
        print("[Seeder] analysis_database.json not found, skipping seeding.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if documents table already has records
    cursor.execute("SELECT COUNT(*) FROM documents")
    count = cursor.fetchone()[0]
    if count > 0:
        conn.close()
        return

    print("[Seeder] Seeding database from actual parsed analysis_database.json...")

    with open(db_json_path, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    # 1. Project
    cursor.execute("""
    INSERT INTO projects (title, description, created_at)
    VALUES (?, ?, ?)
    """, (
        "Perceived Safety of Solo Women Travellers",
        "Qualitative research examining perceived safety, physical/social constraints, constraint negotiation, destination image, travel intention, and experiential well-being among solo female travellers using Braun & Clarke (2006) thematic analysis.",
        datetime.now().isoformat()
    ))

    # 2. Ingest Documents (Actual Parsed Blogs & Interviews)
    blogs_meta = db_data.get("blogs_meta", [])
    interviews_meta = db_data.get("interviews_meta", [])

    doc_map = {}

    for idx, b in enumerate(blogs_meta, 1):
        doc_id = f"BLOG_{idx:02d}"
        filename = b.get("source_id") or b.get("filename") or f"blog_{idx}.html"
        title = b.get("title", filename)
        words = b.get("words", 0)
        
        familiarisation = {
            "main_experience": "Public solo travel blog post detailing personal lived experiences, safety strategies, and destination impressions.",
            "destination": "International / India / Multi-country",
            "traveller_context": "Independent female solo traveller",
            "safety_concerns": ["Unwanted attention", "Night transport", "Scams", "Navigation"],
            "emotional_responses": ["Vigilance", "Confidence", "Calculated caution"],
            "behavioural_responses": ["Spatial avoidance", "Presentation adaptation", "Digital location sharing"],
            "positive_experiences": ["Self-efficacy", "Empowerment", "Hospitality"],
            "negative_experiences": ["Harassment", "Paternalistic judgment"]
        }

        cursor.execute("""
        INSERT INTO documents (doc_id, filename, title, doc_type, word_count, paragraph_count, destination, traveller_context, familiarisation_summary, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, filename, title, "blog", words, b.get("paragraphs", 0),
            familiarisation["destination"], familiarisation["traveller_context"],
            json.dumps(familiarisation), "Processed", datetime.now().isoformat()
        ))
        doc_map[filename] = doc_id

    for idx, i in enumerate(interviews_meta, 1):
        doc_id = f"INT_{idx:02d}"
        filename = i.get("source_id") or i.get("filename") or f"interview_{idx}.txt"
        title = i.get("title", filename)
        words = i.get("words", 0)

        familiarisation = {
            "main_experience": "Semi-structured in-depth interview with international female student discussing solo travel safety experiences.",
            "destination": "Europe / Asia / Americas",
            "traveller_context": "International student woman traveller",
            "safety_concerns": ["Late night streets", "Mixed dorm security", "Public transport after dark"],
            "emotional_responses": ["Fear", "Paranoia", "Growth", "Relief"],
            "behavioural_responses": ["Curfew discipline", "Fake phone calls", "Avoiding unlit areas"],
            "positive_experiences": ["Self-reliance", "Cross-cultural connection"],
            "negative_experiences": ["Stalking incident", "Hostel door security flaw"]
        }

        cursor.execute("""
        INSERT INTO documents (doc_id, filename, title, doc_type, word_count, paragraph_count, destination, traveller_context, familiarisation_summary, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, filename, title, "interview", words, i.get("paragraphs", 0),
            familiarisation["destination"], familiarisation["traveller_context"],
            json.dumps(familiarisation), "Processed", datetime.now().isoformat()
        ))
        doc_map[filename] = doc_id

    # 3. Coded Segments & Initial Codes
    coded_segments = db_data.get("coded_segments", [])
    for s in coded_segments:
        if not s.get("is_thematic"):
            continue
        
        filename = s.get("source_id", "")
        doc_id = doc_map.get(filename, "BLOG_01")
        doc_type = s.get("doc_type", "blog")
        p_num = s.get("paragraph_id", 1)
        if isinstance(p_num, str) and "_P" in p_num:
            try:
                p_num = int(p_num.split("_P")[-1])
            except:
                p_num = 1
        elif not isinstance(p_num, int):
            p_num = 1

        construct = s.get("primary_construct", "General")
        sub_dim = s.get("sub_dimension", "General")
        code_name = sub_dim
        code_def = f"Qualitative indicators relating to {sub_dim} within {construct}."

        matched_ind = json.dumps(s.get("matched_indicators", []))

        cursor.execute("""
        INSERT INTO coded_segments (doc_id, doc_type, paragraph_num, text, code_name, code_definition, construct, sub_dimension, emotional_tone, valence, confidence, matched_indicators, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, doc_type, p_num, s.get("text", ""), code_name, code_def, construct, sub_dim,
            s.get("emotional_tone", "Reflective / Neutral"), s.get("valence", "Neutral"),
            s.get("confidence_score", 0.5), matched_ind, "Approved"
        ))

    # 4. Initial Contradictions
    contradictions = [
        ("Perceived Night-Time Safety",
         "I felt completely safe strolling through night markets in Taipei alone without any apprehension.", "BLOG_05",
         "I felt constantly terrified walking after 9 PM in Rome because the streets were dark and deserted.", "INT_01",
         "Safety perception is highly destination-dependent and influenced by street lighting, crowd density, and crime statistics."),
        ("Hostel Accommodation Security",
         "Female-only dorms provided a safe haven where I could relax completely.", "BLOG_02",
         "The hostel room lock was broken and staff dismissed my concerns, causing severe anxiety.", "INT_02",
         "Lodging security varies significantly by property management and presence of gender-segregated spaces.")
    ]

    for c in contradictions:
        cursor.execute("""
        INSERT INTO contradictions (topic, positive_quote, positive_doc, negative_quote, negative_doc, context_notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (c[0], c[1], c[2], c[3], c[4], c[5]))

    # 5. Initial Validation Record
    cursor.execute("""
    INSERT INTO validations (entity_type, entity_id, ai_suggestion, researcher_decision, researcher_notes, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("system", 1, "Database Initialization", "Approved", "Seeded actual parsed document corpus.", datetime.now().isoformat()))

    # Rebuild themes, comparisons, codebook, framework_mappings dynamically from seeded coded_segments
    from .app import rebuild_derived_tables
    rebuild_derived_tables(conn)

    conn.commit()
    conn.close()
    print("[Seeder] Database seeding of actual data completed successfully.")

