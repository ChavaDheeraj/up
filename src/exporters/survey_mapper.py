"""
survey_mapper.py
Bridges qualitative thematic findings from Phase 1 (Blogs) & Phase 2 (Interviews)
into Phase 3 Quantitative Survey Design & Structural Equation Modeling (SEM).
Operationalizes qualitative themes into Likert-scale measurement items and formal SEM hypotheses.
"""

import os
import pandas as pd
from typing import Dict, Any, List
from ..nlp_thematic.ontology import CONCEPTUAL_HYPOTHESES

# Operationalized Measurement Items mapped from qualitative themes
SURVEY_CONSTRUCT_ITEMS = [
    # Physical Constraints
    {"Construct": "Physical Constraints", "Code": "PC1", "Item_Text": "I worry about being followed, catcalled, or stared at when navigating public spaces alone.", "Scale": "7-point Likert (1=Strongly Disagree, 7=Strongly Agree)"},
    {"Construct": "Physical Constraints", "Code": "PC2", "Item_Text": "I perceive nocturnal transit (e.g., night trains, deserted bus stops, unlicensed taxis) as high-risk for solo female travel.", "Scale": "7-point Likert"},
    {"Construct": "Physical Constraints", "Code": "PC3", "Item_Text": "I am concerned about accommodation vulnerabilities (e.g., weak door locks, ground floor rooms, unsecured dorms).", "Scale": "7-point Likert"},
    
    # Social Constraints
    {"Construct": "Social Constraints", "Code": "SC1", "Item_Text": "In many destinations, I feel constrained by patriarchal norms and restrictive cultural expectations for women.", "Scale": "7-point Likert"},
    {"Construct": "Social Constraints", "Code": "SC2", "Item_Text": "My family and social circle express persistent anxiety and protective pressure regarding my solo travel.", "Scale": "7-point Likert"},
    {"Construct": "Social Constraints", "Code": "SC3", "Item_Text": "I worry about societal victim-blaming or judgment if a safety incident occurs while travelling unaccompanied.", "Scale": "7-point Likert"},

    # Constraint Negotiation Strategies
    {"Construct": "Constraint Negotiation", "Code": "CN1", "Item_Text": "I deliberately alter my presentation (e.g., purposeful walking, fake rings, avoiding eye contact) to deter unwanted attention.", "Scale": "7-point Likert"},
    {"Construct": "Constraint Negotiation", "Code": "CN2", "Item_Text": "I use digital safety tools (e.g., live location tracking, fake phone calls, offline maps) to maintain virtual security tethers.", "Scale": "7-point Likert"},
    {"Construct": "Constraint Negotiation", "Code": "CN3", "Item_Text": "I strictly plan my movements around daylight hours and vet accommodation reviews specifically written by women.", "Scale": "7-point Likert"},
    {"Construct": "Constraint Negotiation", "Code": "CN4", "Item_Text": "I rely on embodied intuition and gut instincts to exit situations as soon as something feels off.", "Scale": "7-point Likert"},

    # Perceived Safety
    {"Construct": "Perceived Safety", "Code": "PS1", "Item_Text": "During my solo journeys, I experience an overall sense of security and psychological comfort.", "Scale": "7-point Likert"},
    {"Construct": "Perceived Safety", "Code": "PS2", "Item_Text": "My subjective feeling of safety is shaped more by my situational vigilance than by sensationalized media reports.", "Scale": "7-point Likert"},
    {"Construct": "Perceived Safety", "Code": "PS3", "Item_Text": "I frequently feel vulnerable or apprehensive when walking alone in unfamiliar travel environments. (R)", "Scale": "7-point Likert (Reverse Coded)"},

    # Destination Image
    {"Construct": "Destination Image", "Code": "DI1", "Item_Text": "A destination's perceived safety reputation is a primary criterion in my positive evaluation of that country/city.", "Scale": "7-point Likert"},
    {"Construct": "Destination Image", "Code": "DI2", "Item_Text": "I view destinations with welcoming, respectful host communities as female-friendly travel destinations.", "Scale": "7-point Likert"},
    {"Construct": "Destination Image", "Code": "DI3", "Item_Text": "I have confidence that local authorities and emergency services in the destination would protect a solo female traveller.", "Scale": "7-point Likert"},

    # Travel Intention
    {"Construct": "Travel Intention", "Code": "TI1", "Item_Text": "Perceived safety concerns directly influence whether I visit, alter the itinerary of, or boycott a destination.", "Scale": "7-point Likert"},
    {"Construct": "Travel Intention", "Code": "TI2", "Item_Text": "I intend to undertake solo travel adventures in the next 12 to 24 months.", "Scale": "7-point Likert"},
    {"Construct": "Travel Intention", "Code": "TI3", "Item_Text": "I actively encourage and advocate for other women to experience solo travel.", "Scale": "7-point Likert"},

    # Well-Being & Self-Leadership
    {"Construct": "Well-Being & Self-Leadership", "Code": "WB1", "Item_Text": "Solo travel has significantly elevated my self-reliance, problem-solving capability, and self-leadership.", "Scale": "7-point Likert"},
    {"Construct": "Well-Being & Self-Leadership", "Code": "WB2", "Item_Text": "Successfully negotiating safety challenges and overcoming fear gives me a profound sense of empowerment.", "Scale": "7-point Likert"},
    {"Construct": "Well-Being & Self-Leadership", "Code": "WB3", "Item_Text": "Solo travel enhances my psychological well-being, mindfulness, and personal fulfillment.", "Scale": "7-point Likert"}
]

class SurveyMapper:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_survey_instrument(self, filename: str = "phase3_survey_constructs.csv") -> Tuple[str, str]:
        """Exports survey items CSV and Markdown specification for Phase 3 questionnaire administration."""
        out_csv = os.path.join(self.output_dir, filename)
        df_items = pd.DataFrame(SURVEY_CONSTRUCT_ITEMS)
        df_items.to_csv(out_csv, index=False, encoding='utf-8')

        # Also create a comprehensive markdown specification
        md_path = os.path.join(self.output_dir, "phase3_survey_specification.md")
        lines = [
            "# Phase 3 Quantitative Survey Instrument & SEM Model Specification",
            "**Title:** Assessing Perceived Safety of Solo Women Travellers",
            "**Bridge:** Operationalized from Braun & Clarke (2006) Thematic Analysis of Travel Blogs & Semi-Structured Interviews.",
            "",
            "## Conceptual Structural Equation Model (SEM) Hypotheses",
            "| Hypothesis | Structural Pathway | Expected Sign | Theoretical Formulation |",
            "| :--- | :--- | :---: | :--- |"
        ]

        for h in CONCEPTUAL_HYPOTHESES:
            lines.append(f"| **{h['code']}** | `{h['pathway']}` | {h['direction']} | {h['formulation']} |")

        lines.extend([
            "",
            "## Operationalized Measurement Scales (N = 400 Women Travellers)",
            "| Construct | Item Code | Survey Indicator Statement | Scale |",
            "| :--- | :---: | :--- | :--- |"
        ])

        for it in SURVEY_CONSTRUCT_ITEMS:
            lines.append(f"| {it['Construct']} | **{it['Code']}** | \"{it['Item_Text']}\" | {it['Scale']} |")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return out_csv, md_path
