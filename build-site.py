#!/usr/bin/env python3
"""
Generate the AYA Search Job Hunt clean static site - FLAT structure.
All lead details inline on cycle pages, direct job links. No 3rd level pages.
"""
import json
import re
from pathlib import Path
from datetime import datetime
from html import escape

# ===== Configuration =====
VAULT_PATH = Path("/home/donzzz/Documents/_obsidian_androidZzz")
PROJECT_PATH = VAULT_PATH / "20-PROJECTS" / "ayako-job-search"
LEADS_DIR = PROJECT_PATH / "leads"
OUTPUT_DIR = Path("/tmp/aya-job-hunt")

# ===== HTML Templates =====

HTML_HEADER_ROOT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Aya's Remote Job Search - Clean Public View">
<title>{title}</title>
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="stylesheet" href="assets/style.css">
<script src="assets/main.js" defer></script>
</head>
<body>
<header>
  <div>
    <h1>{page_title}</h1>
    <div class="subtitle">{subtitle}</div>
  </div>
  <button class="theme-toggle" id="themeToggle">Light</button>
</header>
"""

HTML_FOOTER = """
<button id="backToTop" aria-label="Back to top">^</button>
<footer>
  <p style="text-align: center; color: var(--text-muted); font-size: 0.85rem; padding: 24px;">
    AYA Search Job Hunt - Clean Public View (No PII) | Updated {updated}
    <br>
    <a href="https://github.com/djphamdev/aya-job-hunt" style="color: var(--accent);" target="_blank">GitHub Repo</a>
    | Full drafts & EDD reports in Obsidian vault
  </p>
</footer>
</body>
</html>
"""

# ===== Helper Functions =====

def load_all_evaluated():
    """Load all evaluated JSON files from leads directory."""
    cycles = []
    for json_file in sorted(LEADS_DIR.glob("*-evaluated.json")):
        date_str = json_file.stem.replace("-evaluated", "")
        try:
            data = json.loads(json_file.read_text())
        except Exception as e:
            print(f"  WARNING: Failed to load {json_file}: {e}")
            continue
        
        # Filter to medium, high, and low bands only (not rejected)
        good_leads = [e for e in data if e.get("fit_band") in ("medium", "high", "low")]
        
        cycles.append({
            "date": date_str,
            "leads": good_leads,
            "stats": {
                "total": len(data),
                "high": sum(1 for e in data if e.get("fit_band") == "high"),
                "medium": sum(1 for e in data if e.get("fit_band") == "medium"),
                "low": sum(1 for e in data if e.get("fit_band") == "low"),
                "rejected": sum(1 for e in data if e.get("fit_band") == "reject"),
            }
        })
    return cycles

def generate_index(cycles):
    """Generate the homepage with all cycles as cards."""
    if not cycles:
        return "<h1>No cycles found</h1>"
    
    latest = cycles[-1]
    total_leads = sum(c["stats"]["total"] for c in cycles)
    total_high = sum(c["stats"]["high"] for c in cycles)
    total_medium = sum(c["stats"]["medium"] for c in cycles)
    total_low = sum(c["stats"]["low"] for c in cycles)
    
    html_parts = [HTML_HEADER_ROOT.format(
        title="AYA Search Job Hunt -- Remote Job Leads",
        page_title="AYA Search Job Hunt",
        subtitle=f"100% Remote Only | Bilingual JP/EN | Air Cargo & Logistics | Updated {datetime.now().strftime('%b %d, %Y')}"
    )]
    
    # Stats bar
    html_parts.append(f"""
<div class="stats-bar">
  <div class="stat-card"><div class="num">{total_leads}</div><div class="label">Total Leads</div></div>
  <div class="stat-card"><div class="num high">{total_high}</div><div class="label">High Fit</div></div>
  <div class="stat-card"><div class="num medium">{total_medium}</div><div class="label">Medium Fit</div></div>
  <div class="stat-card"><div class="num low">{total_low}</div><div class="label">Low Fit</div></div>
  <div class="stat-card"><div class="num">{len(cycles)}</div><div class="label">Search Cycles</div></div>
</div>
""")
    
    # Latest cycle highlight
    if latest:
        html_parts.append(f"""
<div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 24px;">
  <h2 style="margin-bottom: 12px;">NEW Latest Update - {latest['date']}</h2>
  <div class="stats-bar" style="margin-bottom: 0;">
    <div class="stat-card"><div class="num medium">{latest['stats']['medium']}</div><div class="label">Medium Fit (Obsidian has drafts)</div></div>
    <div class="stat-card"><div class="num low">{latest['stats']['low']}</div><div class="label">Worth Reviewing</div></div>
    <div class="stat-card"><div class="num">{latest['stats']['total']}</div><div class="label">Total Scanned</div></div>
  </div>
  <div style="margin-top: 14px;">
    <a href="cycle-{latest['date']}.html" class="action-btn primary">View Latest Leads -></a>
    <a href="ai-llm-direct-links.html" class="action-btn secondary" style="margin-left: 12px; background: linear-gradient(135deg, #0c4a6e 0%, #0ea5e9 100%); color: #fff; border-color: #0ea5e9;">AI / LLM Training (129 leads)</a>
  </div>
</div>
""")
    
    # All cycles list
    html_parts.append('<h2 style="margin-bottom: 16px;">All Search Cycles</h2>\n<div style="display: flex; flex-wrap: wrap; gap: 8px;">\n')
    for c in cycles:
        date_formatted = datetime.strptime(c['date'], '%Y-%m-%d').strftime('%A, %b %d, %Y')
        html_parts.append(f"""
<a href="cycle-{c['date']}.html" class="cycle-card">
  <div class="cycle-meta">
    <span class="cycle-date">{date_formatted}</span>
    <span class="cycle-stats">{c['stats']['medium']} Medium - {c['stats']['low']} Low - {c['stats']['total']} scanned</span>
  </div>
  <span class="cycle-badge">{c['stats']['medium']} Medium</span>
</a>
""")
    
    html_parts.append('</div>\n')

    # AI / LLM Training category page link
    html_parts.append("""
<div style="margin-top: 32px;">
  <h2 style="margin-bottom: 16px;">AI / LLM Training - New Category</h2>
  <a href="ai-llm-training.html" class="cycle-card" style="background: linear-gradient(135deg, #0c4a6e 0%, #0ea5e9 100%); color: #fff; border-color: #0ea5e9;">
    <div class="cycle-meta">
      <span class="cycle-date" style="font-size: 1rem; font-weight: 600;">AI / LLM Training & Data Annotation</span>
      <span class="cycle-stats">129 LLM leads - Bilingual JP/EN - Remote studio work</span>
    </div>
    <span class="cycle-badge" style="background: rgba(255,255,255,0.25);">NEW</span>
  </a>
</div>
""")
    
    # Note about Obsidian
    html_parts.append("""
<div class="obsidian-note">
  <strong>Note for Aya:</strong> Full email drafts, EDD certification details, and personalized cover letters are in your Obsidian vault at <code>20-PROJECTS/ayako-job-search/leads/</code>. This public view shows only job links, employer info, and fit scores.
</div>
""")
    
    html_parts.append(HTML_FOOTER.format(updated=datetime.now().strftime('%Y-%m-%d %H:%M')))
    return ''.join(html_parts)

def generate_cycle_page(cycle):
    """Generate the per-cycle listing with ALL lead details inline."""
    html_parts = [HTML_HEADER_ROOT.format(
        title=f"Job Leads -- {cycle['date']} -- AYA Search Job Hunt",
        page_title=f"Leads from {cycle['date']}",
        subtitle=f"{cycle['stats']['medium']} Medium fit (Obsidian has drafts) | {cycle['stats']['low']} Low fit | {cycle['stats']['total']} total"
    )]
    
    # Breadcrumb - link back to index
    html_parts.append("""
<div class="breadcrumb">
  <a href="index.html"><- Home / All Cycles</a>
</div>
""")
    
    # Filter bar
    html_parts.append("""
<div class="filter-bar">
  <label>Filter:</label>
  <select id="fitFilter">
    <option value="all">All Leads</option>
    <option value="medium" selected>Medium Fit (Obsidian has drafts)</option>
    <option value="high">High Fit</option>
    <option value="low">Low Fit (Worth Reviewing)</option>
  </select>
  <input type="text" id="searchFilter" placeholder="Search title or company...">
</div>
""")
    
    # Sort by fit score descending
    leads = sorted(cycle['leads'], key=lambda x: x.get('fit_score', 0), reverse=True)
    
    html_parts.append('<div class="lead-list">\n')
    for e in leads:
        lead = e.get('lead', {})
        band = e.get('fit_band', '')
        score = e.get('fit_score', 0)
        title = lead.get('title', '')
        company = lead.get('company', '')
        location = lead.get('location', '')
        url = lead.get('url', '')
        source = lead.get('source', '')
        strengths = e.get('strengths', [])
        gaps = e.get('gaps', [])
        red_flags = e.get('red_flags', [])
        
        # Build badges
        badges = []
        if band == 'high':
            badges.append(f'<span class="badge badge-high">High {score}</span>')
        elif band == 'medium':
            badges.append(f'<span class="badge badge-medium">Medium {score}</span>')
        elif band == 'low':
            badges.append(f'<span class="badge badge-low">{score}</span>')
        
        # Remote indicator
        loc_lower = (location or '').lower()
        title_lower = (title or '').lower()
        if any(kw in (loc_lower + ' ' + title_lower) for kw in ['remote', 'virtual', 'work from home', 'wfh']):
            badges.append('<span class="badge badge-remote">Remote</span>')
        
        # Bilingual indicator
        if any(kw in (title_lower + ' ' + (company or '').lower()) for kw in ['japanese', 'bilingual', 'jp/en']):
            badges.append('<span class="badge badge-jp">JP</span>')
        
        badges_html = ' '.join(badges)
        
        # Remote / JP indicators for meta line
        meta_parts = []
        if any(kw in (loc_lower + ' ' + title_lower) for kw in ['remote', 'virtual', 'work from home', 'wfh']):
            meta_parts.append('<span>Remote</span>')
        if any(kw in (title_lower + ' ' + (company or '').lower()) for kw in ['japanese', 'bilingual', 'jp/en']):
            meta_parts.append('<span>JP</span>')
        meta_html = ' '.join(meta_parts) if meta_parts else ''
        
        # Strengths HTML
        strengths_html = ''
        if strengths:
            strengths_html = '<div class="details-section"><div class="details-section-title">Strengths</div><ul class="strengths-list">'
            for s in strengths:
                strengths_html += f'<li>{escape(s)}</li>'
            strengths_html += '</ul></div>'
        
        # Gaps HTML
        gaps_html = ''
        if gaps:
            gaps_html = '<div class="details-section"><div class="details-section-title">Gaps</div><ul class="gaps-list">'
            for g in gaps:
                gaps_html += f'<li>{escape(g)}</li>'
            gaps_html += '</ul></div>'
        
        # Red flags HTML
        red_flags_html = ''
        if red_flags:
            red_flags_html = '<div class="details-section"><div class="details-section-title">Red Flags</div><ul class="gaps-list">'
            for r in red_flags:
                red_flags_html += f'<li>{escape(r)}</li>'
            red_flags_html += '</ul></div>'
        
        # Build lead card
        html_parts.append(f"""
<div class="lead-card" data-band="{band}">
  <div class="lead-card-header">
    <div>
      <h3>{escape(str(title or ""))}</h3>
      <div class="company">{escape(str(company or ""))} | {escape(str(location or ""))}</div>
      <div class="meta">{meta_html}</div>
    </div>
    <div style="white-space: nowrap;">{badges_html}</div>
  </div>
  
  <div class="lead-details">
    <div class="lead-details-grid">
      <div class="lead-detail-item">
        <div class="label">Fit Score</div>
        <div class="value">{score} / 100</div>
      </div>
      <div class="lead-detail-item">
        <div class="label">Fit Band</div>
        <div class="value">{band.upper()}</div>
      </div>
      <div class="lead-detail-item">
        <div class="label">Source</div>
        <div class="value">{escape(str(source or ""))}</div>
      </div>
      <div class="lead-detail-item">
        <div class="label">Date Found</div>
        <div class="value">{cycle['date']}</div>
      </div>
      <div class="lead-detail-item">
        <div class="label">Job Posting</div>
        <div class="value"><a href="{escape(str(url or ""))}" target="_blank" rel="noopener noreferrer">{escape(str(source or ""))} -></a></div>
      </div>
    </div>
    
    {strengths_html}
    {gaps_html}
    {red_flags_html}
    
    <div class="action-bar">
      <a href="{escape(str(url or ""))}" target="_blank" rel="noopener noreferrer" class="action-btn primary">Open Job Posting</a>
    </div>
  </div>
</div>
""")
    
    html_parts.append('</div>\n')
    html_parts.append(HTML_FOOTER.format(updated=datetime.now().strftime('%Y-%m-%d %H:%M')))
    return ''.join(html_parts)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "assets").mkdir(exist_ok=True)
    
    print("Generating AYA Search Job Hunt flat site (no 3rd level)...")
    
    cycles = load_all_evaluated()
    
    if not cycles:
        print("  No cycles found!")
        return
    
    # Generate index
    index_html = generate_index(cycles)
    (OUTPUT_DIR / "index.html").write_text(index_html)
    print(f"  index.html -- {len(cycles)} cycles, {sum(c['stats']['total'] for c in cycles)} total leads")
    
    # Generate cycle pages
    for cycle in cycles:
        cycle_html = generate_cycle_page(cycle)
        (OUTPUT_DIR / f"cycle-{cycle['date']}.html").write_text(cycle_html)
        print(f"  cycle-{cycle['date']}.html -- {cycle['stats']['medium']} medium, {cycle['stats']['low']} low, {cycle['stats']['total']} total")
    
    # Copy assets (style.css, main.js, favicon.svg)
    import shutil
    for asset in ["style.css", "main.js", "favicon.svg"]:
        src = OUTPUT_DIR / "assets" / asset
        if src.exists():
            continue
    
    # Generate README
    readme = """# AYA Search Job Hunt

**Live Site: https://djphamdev.github.io/aya-job-hunt/**

Clean public view of remote job leads. No PII, no email drafts.

## Site Structure
- index.html - Homepage with all cycles
- cycle-YYYY-MM-DD.html - Per-cycle leads with all details inline
- ai-llm-training.html - AI/LLM Training category page
- assets/style.css - Styles
- assets/main.js - Theme toggle, back-to-top, filters
- assets/favicon.svg - Blue glassy 3D star

## Data Source
Obsidian vault: `20-PROJECTS/ayako-job-search/leads/`
- *-leads.json: Raw leads
- *-evaluated.json: Scored leads
- *-email-drafts.md: Email drafts (private, not on site)
- *-edd-report.md: EDD work search reports

## Auto-Update
Cron runs every 12h (6AM/6PM), rebuilds site, pushes to GitHub Pages.
"""
    (OUTPUT_DIR / "README.md").write_text(readme)
    
    print(f"\nFlat site generated: {OUTPUT_DIR}")
    print(f"   {len(cycles)} cycles | {sum(c['stats']['total'] for c in cycles)} leads | 0 separate lead pages")

if __name__ == "__main__":
    main()