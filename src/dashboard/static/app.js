// Research Dashboard Frontend JavaScript

document.addEventListener("DOMContentLoaded", () => {
    loadOverview();
    loadConstructs();
    loadEmergentThemes();
    loadCrossDataset();
    loadSurveyModel();
});

function switchTab(tabName) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

    const btn = document.getElementById(`tab-btn-${tabName}`);
    const panel = document.getElementById(`panel-${tabName}`);
    if (btn && panel) {
        btn.classList.add("active");
        panel.classList.add("active");
    }
}

async function loadOverview() {
    try {
        const res = await fetch("/api/overview");
        const data = await res.json();

        document.getElementById("metric-docs").innerText = data.total_documents;
        document.getElementById("metric-docs-sub").innerText = `${data.total_blogs} Blogs • ${data.total_interviews} Interviews`;
        document.getElementById("metric-words").innerText = data.total_words.toLocaleString();
        document.getElementById("metric-segments").innerText = data.total_segments_analyzed.toLocaleString();
        document.getElementById("metric-density").innerText = `${data.coding_density_pct}%`;

        // Render blog list
        const blogList = document.getElementById("blog-list");
        blogList.innerHTML = data.blogs_meta.map(b => 
            `<li style="padding: 6px 0; border-bottom: 1px solid var(--border-subtle); display: flex; justify-content: space-between;">
                <span><strong>${escapeHtml(b.title)}</strong></span>
                <span style="color: var(--text-muted); font-size: 11.5px;">${b.words.toLocaleString()} words</span>
            </li>`
        ).join("");

        // Render interview list
        const intList = document.getElementById("interview-list");
        intList.innerHTML = data.interviews_meta.map(i => 
            `<li style="padding: 6px 0; border-bottom: 1px solid var(--border-subtle); display: flex; justify-content: space-between;">
                <span><strong>${escapeHtml(i.title)}</strong></span>
                <span style="color: var(--text-muted); font-size: 11.5px;">${i.words.toLocaleString()} words</span>
            </li>`
        ).join("");
    } catch (e) {
        console.error("Error loading overview:", e);
    }
}

async function loadConstructs() {
    try {
        const res = await fetch("/api/constructs");
        const data = await res.json();

        // 1. Render Construct Bars
        const container = document.getElementById("construct-bars-container");
        const freqs = data.construct_frequencies;
        const maxFreq = Math.max(...Object.values(freqs), 1);
        
        const colors = ['#6366f1', '#14b8a6', '#f59e0b', '#f43f5e', '#ec4899', '#8b5cf6', '#3b82f6'];
        
        let htmlBars = "";
        let colorIdx = 0;
        for (const [construct, count] of Object.entries(freqs)) {
            const pct = Math.round((count / maxFreq) * 100);
            const color = colors[colorIdx % colors.length];
            colorIdx++;

            htmlBars += `
                <div class="construct-bar-item">
                    <div class="construct-bar-header">
                        <span class="name">${escapeHtml(construct)}</span>
                        <span class="count"><strong>${count}</strong> segments</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width: ${pct}%; background: ${color};"></div>
                    </div>
                </div>
            `;
        }
        container.innerHTML = htmlBars;

        // 2. Render Accordion of Themes & Quotes
        const accordionContainer = document.getElementById("themes-accordion-container");
        let htmlAccordion = "";

        data.final_themes.forEach((theme, idx) => {
            const isOpen = idx === 0 ? "open" : "";
            
            let subThemesHtml = "";
            theme.sub_themes.forEach(st => {
                let quotesHtml = "";
                if (st.verbatim_evidence && st.verbatim_evidence.length > 0) {
                    st.verbatim_evidence.forEach(q => {
                        quotesHtml += `
                            <div class="quote-box">
                                "${escapeHtml(q.text)}"
                                <div class="quote-meta">
                                    <span><strong>Source:</strong> ${escapeHtml(q.doc_title)} (${q.doc_type})</span>
                                    <span><span class="badge badge-indigo">${q.emotional_tone}</span> Conf: ${q.confidence_score}</span>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    quotesHtml = `<div style="font-size: 12px; color: var(--text-muted); font-style: italic;">No high-confidence quotes in current sample.</div>`;
                }

                subThemesHtml += `
                    <div class="subtheme-card">
                        <div class="subtheme-header">
                            <span class="subtheme-title">📌 ${escapeHtml(st.sub_theme_name)}</span>
                            <span style="font-size: 12px; color: var(--text-muted);">${st.frequency} instances • ${st.document_reach} sources</span>
                        </div>
                        <p style="font-size: 12.5px; color: var(--text-secondary); margin-bottom: 10px;">${escapeHtml(st.definition)}</p>
                        ${quotesHtml}
                    </div>
                `;
            });

            htmlAccordion += `
                <div class="theme-accordion">
                    <div class="theme-accordion-header" onclick="toggleAccordion(this)">
                        <div class="theme-accordion-title">
                            <span style="font-size: 16px;">📂</span>
                            <span style="font-weight: 600; font-size: 15px;">${escapeHtml(theme.construct)}</span>
                            <span class="theme-badge-freq">${theme.total_frequency} evidence units</span>
                        </div>
                        <span style="color: var(--text-muted); font-size: 18px;">▾</span>
                    </div>
                    <div class="theme-body ${isOpen}">
                        <p style="font-size: 13px; color: var(--text-secondary); margin-top: 14px; font-style: italic;">
                            Theoretical Definition: ${escapeHtml(theme.theoretical_definition)}
                        </p>
                        ${subThemesHtml}
                    </div>
                </div>
            `;
        });
        accordionContainer.innerHTML = htmlAccordion;

    } catch (e) {
        console.error("Error loading constructs:", e);
    }
}

function toggleAccordion(headerElem) {
    const bodyElem = headerElem.nextElementSibling;
    bodyElem.classList.toggle("open");
}

async function loadEmergentThemes() {
    try {
        const res = await fetch("/api/emergent-themes");
        const data = await res.json();
        const container = document.getElementById("emergent-topics-container");

        let html = "";
        data.emergent_themes.forEach(t => {
            let quotesHtml = "";
            t.exemplar_quotes.slice(0, 2).forEach(q => {
                quotesHtml += `
                    <div class="quote-box" style="border-left-color: var(--accent-teal);">
                        "${escapeHtml(q.text)}"
                        <div class="quote-meta">
                            <span><strong>Source:</strong> ${escapeHtml(q.source_id)}</span>
                            <span>Topic Weight: ${q.weight}</span>
                        </div>
                    </div>
                `;
            });

            html += `
                <div class="subtheme-card" style="margin-bottom: 16px; border-left: 4px solid var(--accent-teal);">
                    <div class="subtheme-header">
                        <span style="font-weight: 700; font-size: 15px; color: #5eead4;">[${t.theme_id}] ${escapeHtml(t.candidate_name)}</span>
                        <span class="badge badge-teal">${t.document_prevalence} documents</span>
                    </div>
                    <div style="margin: 8px 0;">
                        <span style="font-size: 11px; text-transform: uppercase; color: var(--text-muted);">Top Salient Keywords: </span>
                        <span style="font-size: 13px; color: #cbd5e1;">${t.top_keywords.join(", ")}</span>
                    </div>
                    <div style="margin-top: 10px;">
                        <div style="font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Exemplar Verbatim Excerpts:</div>
                        ${quotesHtml}
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    } catch (e) {
        console.error("Error loading emergent themes:", e);
    }
}

async function loadCrossDataset() {
    try {
        const res = await fetch("/api/cross-dataset");
        const data = await res.json();
        const tbody = document.getElementById("cross-dataset-tbody");

        tbody.innerHTML = data.comparison_matrix.map(row => {
            const isDivergent = Math.abs(row.difference_pct) > 8;
            const badgeClass = isDivergent ? "badge-rose" : "badge-teal";
            const diffColor = row.difference_pct > 0 ? "#818cf8" : "#34d399";
            const diffSign = row.difference_pct > 0 ? `+${row.difference_pct}%` : `${row.difference_pct}%`;

            return `
                <tr>
                    <td><strong>${escapeHtml(row.construct)}</strong></td>
                    <td><strong>${row.blog_percentage}%</strong> <span style="color: var(--text-muted); font-size: 11px;">(${row.blog_frequency})</span></td>
                    <td><strong>${row.interview_percentage}%</strong> <span style="color: var(--text-muted); font-size: 11px;">(${row.interview_frequency})</span></td>
                    <td style="color: ${diffColor}; font-weight: 600;">${diffSign}</td>
                    <td><span style="font-size: 12px; color: var(--text-secondary);">${escapeHtml(row.relationship)}</span></td>
                </tr>
            `;
        }).join("");

        document.getElementById("insight-public").innerText = data.discursive_insights.public_blog_nature;
        document.getElementById("insight-private").innerText = data.discursive_insights.private_interview_nature;

    } catch (e) {
        console.error("Error loading cross dataset:", e);
    }
}

async function loadSurveyModel() {
    try {
        const res = await fetch("/api/survey-model");
        const data = await res.json();

        // 1. Hypotheses
        const hypoTbody = document.getElementById("hypotheses-tbody");
        hypoTbody.innerHTML = data.hypotheses.map(h => `
            <tr>
                <td><span class="badge badge-indigo">${h.code}</span></td>
                <td><code>${escapeHtml(h.pathway)}</code></td>
                <td><span style="font-weight: 600; color: ${h.direction.includes('negative') ? '#f43f5e' : '#10b981'};">${h.direction}</span></td>
                <td style="font-size: 12.5px;">${escapeHtml(h.formulation)}</td>
            </tr>
        `).join("");

        // 2. Survey Items
        const itemsTbody = document.getElementById("survey-items-tbody");
        itemsTbody.innerHTML = data.items.map(it => `
            <tr>
                <td><strong>${escapeHtml(it.Construct)}</strong></td>
                <td><span class="badge badge-teal">${it.Code}</span></td>
                <td style="font-size: 13.5px;">"${escapeHtml(it.Item_Text)}"</td>
                <td style="font-size: 12px; color: var(--text-secondary);">${it.Scale}</td>
            </tr>
        `).join("");

    } catch (e) {
        console.error("Error loading survey model:", e);
    }
}

async function analyzePlaygroundText() {
    const text = document.getElementById("playground-text").value.trim();
    if (!text) {
        alert("Please enter or load some text to analyze.");
        return;
    }

    const btn = document.getElementById("btn-analyze-text");
    btn.innerText = "Analyzing...";
    btn.disabled = true;

    try {
        const res = await fetch("/api/analyze-text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        });
        const data = await res.json();
        const r = data.coding_result;

        const resultBox = document.getElementById("playground-result");
        resultBox.style.display = "block";

        const confidencePct = Math.round(r.confidence_score * 100);

        resultBox.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <h3 style="font-size: 16px; font-weight: 700; color: #ffffff;">Model Coding Assessment</h3>
                <span class="badge ${r.is_thematic ? 'badge-teal' : 'badge-indigo'}">
                    ${r.is_thematic ? 'Substantive Thematic Match' : 'General Context'}
                </span>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 16px;">
                <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: var(--radius-sm);">
                    <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Primary Construct</div>
                    <div style="font-size: 15px; font-weight: 600; color: var(--primary-light); margin-top: 4px;">${escapeHtml(r.primary_construct)}</div>
                </div>
                <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: var(--radius-sm);">
                    <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Sub-Dimension Code</div>
                    <div style="font-size: 14px; font-weight: 600; color: #e2e8f0; margin-top: 4px;">${escapeHtml(r.sub_dimension)}</div>
                </div>
                <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: var(--radius-sm);">
                    <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Affective / Emotional Tone</div>
                    <div style="font-size: 14px; font-weight: 600; color: #f59e0b; margin-top: 4px;">${escapeHtml(r.emotional_tone)}</div>
                </div>
                <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: var(--radius-sm);">
                    <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Confidence Score</div>
                    <div style="font-size: 15px; font-weight: 700; color: #10b981; margin-top: 4px;">${r.confidence_score} (${confidencePct}%)</div>
                </div>
            </div>

            <div style="font-size: 12px; color: var(--text-secondary);">
                <strong>Detected Qualitative Indicators / Keywords:</strong> 
                <span style="color: #cbd5e1;">${r.matched_indicators.length > 0 ? r.matched_indicators.join(", ") : "Latent semantic vector affinity (LSA cosine projection)"}</span>
            </div>
        `;
    } catch (e) {
        alert("Analysis error: " + e);
    } finally {
        btn.innerText = "⚡ Run Automated ML Coding";
        btn.disabled = false;
    }
}

function loadSampleText(sampleId) {
    const samples = {
        1: "When I arrived in Naples late at night, the alley near the train station was completely dark with no lighting and no CCTV. Two men started following me and shouting catcalls, which terrified me. I ran into a crowded restaurant to wait until I could catch a licensed taxi.",
        2: "Navigating international solo travel has fundamentally transformed my self-leadership. Before this journey, I had endless self-doubt, but now I know I am resilient, capable, and completely independent. Overcoming these safety hurdles gave me true empowerment.",
        3: "Before boarding any overnight bus, I always put on a cheap fake wedding ring and talk loudly about my husband meeting me at the station. I also share my WhatsApp live location with my parents and keep emergency offline maps on my phone."
    };
    document.getElementById("playground-text").value = samples[sampleId] || "";
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// ===== TAB 8: DOCUMENT UPLOAD & THEMATIC ANALYSIS =====

let _uploadedFile = null;

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) setUploadedFile(file);
}

function handleFileDrop(event) {
    event.preventDefault();
    document.getElementById('upload-drop-zone').classList.remove('drag-over');
    const file = event.dataTransfer.files[0];
    if (file) setUploadedFile(file);
}

function setUploadedFile(file) {
    _uploadedFile = file;
    const badge = document.getElementById('upload-file-badge');
    badge.textContent = '\uD83D\uDCC4 ' + file.name + '  (' + (file.size / 1024).toFixed(1) + ' KB)';
    badge.style.display = 'inline-block';
    // Hide old results
    document.getElementById('upload-results').style.display = 'none';
    document.getElementById('upload-error').style.display = 'none';
}

async function runUploadAnalysis() {
    if (!_uploadedFile) {
        alert('Please select a file first by clicking the upload zone or dragging a file onto it.');
        return;
    }

    const btn = document.getElementById('btn-upload-analyze');
    const progressDiv = document.getElementById('upload-progress');
    const progressFill = document.getElementById('upload-progress-fill');
    const progressLabel = document.getElementById('upload-progress-label');
    const errorDiv = document.getElementById('upload-error');
    const resultsDiv = document.getElementById('upload-results');

    btn.disabled = true;
    btn.textContent = 'Analyzing\u2026';
    errorDiv.style.display = 'none';
    resultsDiv.style.display = 'none';
    progressDiv.style.display = 'block';

    // Animate progress bar through stages
    const stages = [
        { pct: 15, label: 'Parsing document\u2026' },
        { pct: 35, label: 'Segmenting into coding units\u2026' },
        { pct: 60, label: 'Running ML qualitative coding\u2026' },
        { pct: 85, label: 'Extracting themes & evidence quotes\u2026' },
        { pct: 97, label: 'Compiling results\u2026' }
    ];
    let stageIdx = 0;
    const stageTimer = setInterval(() => {
        if (stageIdx < stages.length) {
            progressFill.style.width = stages[stageIdx].pct + '%';
            progressLabel.textContent = stages[stageIdx].label;
            stageIdx++;
        }
    }, 700);

    try {
        const docType = document.getElementById('upload-doc-type').value;
        const formData = new FormData();
        formData.append('file', _uploadedFile);
        formData.append('doc_type', docType);

        const res = await fetch('/api/upload-analyze', {
            method: 'POST',
            body: formData
        });

        clearInterval(stageTimer);

        if (!res.ok) {
            const err = await res.json();
            progressDiv.style.display = 'none';
            errorDiv.textContent = '\u26A0\uFE0F ' + (err.detail || 'Unknown error during analysis.');
            errorDiv.style.display = 'block';
            return;
        }

        progressFill.style.width = '100%';
        progressLabel.textContent = 'Analysis complete!';

        const data = await res.json();

        setTimeout(() => {
            progressDiv.style.display = 'none';
            renderUploadResults(data);
        }, 500);

    } catch (e) {
        clearInterval(stageTimer);
        progressDiv.style.display = 'none';
        errorDiv.textContent = '\u26A0\uFE0F Network error: ' + e.message;
        errorDiv.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.textContent = '\u26A1 Run Thematic Analysis';
    }
}

function renderUploadResults(data) {
    const resultsDiv = document.getElementById('upload-results');
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // --- Summary Cards ---
    const summaryCards = [
        { label: 'Word Count', value: (data.word_count || 0).toLocaleString(), sub: data.title || data.filename },
        { label: 'Total Segments', value: data.total_segments, sub: 'Analyzed coding units' },
        { label: 'Thematic Segments', value: data.thematic_segments_count, sub: 'Safety-relevant passages' },
        { label: 'Thematic Density', value: data.thematic_density_pct + '%', sub: 'Of corpus is thematic' },
        { label: 'Dominant Construct', value: '', sub: data.dominant_construct, bigSub: true },
        { label: 'Dominant Emotion', value: '', sub: data.dominant_emotional_tone, bigSub: true }
    ];

    document.getElementById('upload-summary-cards').innerHTML = summaryCards.map(c => `
        <div class="upload-summary-card">
            <div class="card-label">${c.label}</div>
            ${c.bigSub ? '' : '<div class="card-value">' + escapeHtml(String(c.value)) + '</div>'}
            <div class="card-sub" style="${c.bigSub ? 'font-size:14px;font-weight:600;color:var(--accent-amber);margin-top:4px;' : ''}">${escapeHtml(c.sub)}</div>
        </div>
    `).join('');

    // --- Construct Distribution Bars ---
    const constructs = data.construct_distribution || [];
    const maxFreq = Math.max(...constructs.map(c => c.frequency), 1);
    const colors = ['#6366f1','#14b8a6','#f59e0b','#f43f5e','#ec4899','#8b5cf6','#3b82f6'];
    document.getElementById('upload-construct-bars').innerHTML = constructs.map((c, i) => {
        const pct = Math.round((c.frequency / maxFreq) * 100);
        const col = colors[i % colors.length];
        return `
            <div class="construct-bar-item">
                <div class="construct-bar-header">
                    <span class="name">${escapeHtml(c.construct)}</span>
                    <span class="count"><strong>${c.frequency}</strong> segments &nbsp;|&nbsp; ${c.percentage}%</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:${pct}%; background:${col};"></div>
                </div>
                <div style="font-size:11.5px; color:var(--text-muted); margin-top:4px;">${escapeHtml(c.definition)}</div>
            </div>
        `;
    }).join('');

    // --- Emotion Chips ---
    const emotions = data.emotion_distribution || {};
    const totalEmo = Object.values(emotions).reduce((a, b) => a + b, 0) || 1;
    const emoColors = { 'Fear / Anxiety': '#f43f5e', 'Empowerment / Confidence': '#10b981', 'Frustration / Anger': '#f97316', 'Reflective / Neutral': '#94a3b8', 'Vigilance / Alertness': '#f59e0b', 'Relief / Gratitude': '#14b8a6' };
    document.getElementById('upload-emotion-chips').innerHTML = Object.entries(emotions)
        .sort((a, b) => b[1] - a[1])
        .map(([tone, count]) => {
            const pct = Math.round((count / totalEmo) * 100);
            const col = emoColors[tone] || '#818cf8';
            return `<span class="emotion-chip" style="border-color:${col}33; color:${col};">
                ${escapeHtml(tone)} <strong style="margin-left:6px;">${pct}%</strong> <span style="color:var(--text-muted); font-size:11px;">(${count})</span>
            </span>`;
        }).join('');

    // --- Top Evidence Quotes ---
    const quotes = data.top_evidence_quotes || [];
    document.getElementById('upload-evidence-quotes').innerHTML = quotes
        .filter(q => q.text)
        .map(q => `
            <div class="quote-box" style="margin-bottom:14px;">
                <div style="font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--accent-amber); font-weight:600; margin-bottom:6px;">
                    ${escapeHtml(q.construct)} &rsaquo; ${escapeHtml(q.sub_dimension || '')}
                </div>
                "${escapeHtml(q.text)}"
                <div class="quote-meta">
                    <span><span class="badge badge-indigo">${escapeHtml(q.emotional_tone || '')}</span></span>
                    <span>Confidence: <strong>${q.confidence_score}</strong></span>
                    ${q.matched_indicators && q.matched_indicators.length ? '<span>Keywords: ' + q.matched_indicators.slice(0,4).map(k => '<code style="font-size:11px;background:rgba(255,255,255,.08);padding:1px 5px;border-radius:3px;">' + escapeHtml(k) + '</code>').join(' ') + '</span>' : ''}
                </div>
            </div>
        `).join('') || '<p style="color:var(--text-muted); font-style:italic; font-size:13px;">No high-confidence thematic quotes detected in this document.</p>';
}
