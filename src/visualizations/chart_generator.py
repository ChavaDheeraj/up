"""
chart_generator.py
Generates publication-ready academic figures and thematic distribution charts
using Matplotlib and Seaborn.
"""

import os
import matplotlib
matplotlib.use('Agg') # Non-interactive headless backend
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List

class ChartGenerator:
    def __init__(self, output_dir: str = "outputs/figures"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Apply clean academic styling
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
        plt.rcParams['axes.edgecolor'] = '#cccccc'
        plt.rcParams['axes.linewidth'] = 0.8

    def plot_construct_frequencies(self, synthesis_data: Dict[str, Any], filename: str = "construct_frequencies.png") -> str:
        """Plots frequency of higher-order theoretical constructs."""
        out_path = os.path.join(self.output_dir, filename)
        freqs = synthesis_data.get("construct_frequencies", {})
        if not freqs:
            return ""

        sorted_items = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
        constructs = [k for k, v in sorted_items]
        counts = [v for k, v in sorted_items]

        fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
        palette = sns.color_palette("mako", len(constructs))
        bars = ax.barh(constructs, counts, color=palette, edgecolor='none', height=0.65)
        
        ax.invert_yaxis() # Top down
        ax.set_title("Frequency of Identified Theoretical Constructs in Qualitative Corpus", fontsize=13, pad=15, fontweight='bold', color='#222222')
        ax.set_xlabel("Number of Coded Segments / Evidence Units", fontsize=11, labelpad=10)
        
        # Add value labels at bar ends
        for bar in bars:
            width = bar.get_width()
            ax.text(width + max(1, max(counts)*0.015), bar.get_y() + bar.get_height()/2, 
                    f"{int(width)}", ha='left', va='center', fontsize=10, fontweight='bold', color='#444444')

        plt.tight_layout()
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return out_path

    def plot_emotional_tones(self, coded_segments: List[Dict[str, Any]], filename: str = "emotional_tone_distribution.png") -> str:
        """Plots the distribution of emotional valences and tones across the travel narratives."""
        out_path = os.path.join(self.output_dir, filename)
        thematic = [s for s in coded_segments if s.get("is_thematic")]
        if not thematic:
            return ""

        tones = [s.get("emotional_tone", "Neutral") for s in thematic]
        from collections import Counter
        counts = Counter(tones)

        labels = list(counts.keys())
        values = list(counts.values())

        fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
        colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948']
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=140,
            colors=colors[:len(labels)],
            wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
        )

        for at in autotexts:
            at.set_color('white')
            at.set_fontweight('bold')

        ax.set_title("Emotional & Affective Tone Distribution Across Qualitative Evidence", fontsize=12, pad=12, fontweight='bold')
        plt.tight_layout()
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return out_path

    def plot_cross_dataset_comparison(self, cross_data: Dict[str, Any], filename: str = "cross_dataset_comparison.png") -> str:
        """Plots comparative clustered bar chart of Blogs vs. Interviews percentage emphasis."""
        out_path = os.path.join(self.output_dir, filename)
        matrix = cross_data.get("comparison_matrix", [])
        if not matrix:
            return ""

        constructs = [m["construct"] for m in matrix]
        blog_pcts = [m["blog_percentage"] for m in matrix]
        int_pcts = [m["interview_percentage"] for m in matrix]

        import numpy as np
        y = np.arange(len(constructs))
        height = 0.35

        fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
        ax.barh(y - height/2, blog_pcts, height, label='Solo Travel Blogs (Public Discourse, N=40)', color='#3b82f6')
        ax.barh(y + height/2, int_pcts, height, label='Student Interviews (Private Narrative, N=50)', color='#10b981')

        ax.set_yticks(y)
        ax.set_yticklabels(constructs, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel('Percentage of Coded Discourse (%)', fontsize=11, labelpad=10)
        ax.set_title('Cross-Dataset Triangulation: Public Blogs vs. Private Interviews', fontsize=13, pad=15, fontweight='bold', color='#1e293b')
        ax.legend(loc='lower right', frameon=True, framealpha=0.95)

        plt.tight_layout()
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return out_path
