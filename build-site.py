#!/usr/bin/env python3
"""
Generate the AYA Search Job Hunt clean static site - FLAT structure.
All lead details inline on cycle pages, direct job links. No 3rd level pages.
"""
import json
import re
import os
import sys
import html
from pathlib import Path
from datetime import datetime

VAULT_LEADS_DIR = Path("/home/donzzz/Documents/_obsidian_androidZzz/20-PROJECTS/ayako-job-search/leads")
OUTPUT_DIR = Path("/tmp/aya-job-hunt")

# ===== Helpers =====

def slugify(text, max_len=60):
    text = str(text or "").lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = text.strip('-')
    return text[:max_len]

def escape(text):
    return html.escape(str(text or ""))

def load_all_cycles():
    """Load all evaluated leads from all cycle dates"""
    cycles = []
    eval_files = sorted(VAULT_LEADS_DIR.glob("*-evaluated.json"), reverse=True)
    for ef in eval_files:
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})-evaluated', ef.name)
        if not date_match:
            continue
        date_str = date_match.group(1)
        data = json.loads(ef.read_text())
        if not data:
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
  <button class="theme-toggle" id="themeToggle">☀️ Light</button>
</header>
"""

HTML_FOOTER = """
<button id="backToTop" aria-label="Back to top">↑</button>
<footer>
  <p>AYA Search Job Hunt — Clean public view of remote job leads</p>
  <p>Auto-generated from LinkedIn + freehire.me + career-ops • Updated: {updated}</p>
</footer>
</body>
</html>
"""

def generate_index(cycles, total_leads):
    latest = cycles[0] if cycles else None
    total_medium = sum(c["stats"]["medium"] for c in cycles)
    total_high = sum(c["stats"]["high"] for c in cycles)
    total_low = sum(c["stats"]["low"] for c in cycles)
    
    html_parts = [HTML_HEADER_ROOT.format(
        title="AYA Search Job Hunt — Remote Job Leads",
        page_title="🔍 AYA Search Job Hunt",
        subtitle=f"100% Remote Only · Bilingual JP/EN · Air Cargo & Logistics · Updated {datetime.now().strftime('%b %d, %Y')}"
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
  <h2 style="margin-bottom: 12px;">🆕 Latest Update — {latest['date']}</h2>
  <div class="stats-bar" style="margin-bottom: 0;">
    <div class="stat-card"><div class="num medium">{latest['stats']['medium']}</div><div class="label">Medium Fit (Obsidian has drafts)</div></div>
    <div class="stat-card"><div class="num low">{latest['stats']['low']}</div><div class="label">Worth Reviewing</div></div>
    <div class="stat-card"><div class="num">{latest['stats']['total']}</div><div class="label">Total Scanned</div></div>
  </div>
  <div style="margin-top: 14px;">
    <a href="cycle-{latest['date']}.html" class="action-btn primary">View Latest Leads →</a>
  </div>
</div>
""")
    
    # All cycles list
    html_parts.append('<h2 style="margin-bottom: 16px;">📅 All Search Cycles</h2>\n<div style="display: flex; flex-wrap: wrap; gap: 8px;">\n')
    for c in cycles:
        date_formatted = datetime.strptime(c['date'], '%Y-%m-%d').strftime('%A, %b %d, %Y')
        html_parts.append(f"""
<a href="cycle-{c['date']}.html" class="cycle-card">
  <div class="cycle-meta">
    <span class="cycle-date">{date_formatted}</span>
    <span class="cycle-stats">{c['stats']['medium']} Medium · {c['stats']['low']} Low · {c['stats']['total']} scanned</span>
  </div>
  <span class="cycle-badge">{c['stats']['medium']} Medium</span>
</a>
""")
    
    html_parts.append('</div>\n')
    
    # Note about Obsidian
    html_parts.append("""
<div class="obsidian-note">
  <strong>📝 Note for Aya:</strong> Full email drafts, EDD certification details, and personalized cover letters are in your Obsidian vault at <code>20-PROJECTS/ayako-job-search/leads/</code>. This public view shows only job links, employer info, and fit scores.
</div>
""")
    
    html_parts.append(HTML_FOOTER.format(updated=datetime.now().strftime('%Y-%m-%d %H:%M')))
    return ''.join(html_parts)

def generate_cycle_page(cycle):
    """Generate the per-cycle listing with ALL lead details inline."""
    html_parts = [HTML_HEADER_ROOT.format(
        title=f"Job Leads — {cycle['date']} — AYA Search Job Hunt",
        page_title=f"🔍 Leads from {cycle['date']}",
        subtitle=f"{cycle['stats']['medium']} Medium fit (Obsidian has drafts) · {cycle['stats']['low']} Low fit · {cycle['stats']['total']} total"
    )]
    
    # Breadcrumb - link back to index
    html_parts.append("""
<div class="breadcrumb">
  <a href="index.html">← Home / All Cycles</a>
</div>
""")
    
    # Filter bar
    html_parts.append("""
<div class="filter-bar">
  <label>Filter:</label>
  <select id="fitFilter">
    <option value="all">All Leads</option>
    <option value="medium" selected>✉️ Medium Fit (Obsidian has drafts)</option>
    <option value="high">⭐ High Fit</option>
    <option value="low">📋 Low Fit (Worth Reviewing)</option>
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
            badges.append(f'<span class="badge badge-high">⭐ High {score}</span>')
        elif band == 'medium':
            badges.append(f'<span class="badge badge-medium">✉️ Medium {score}</span>')
        elif band == 'low':
            badges.append(f'<span class="badge badge-low">{score}</span>')
        
        # Remote indicator
        loc_lower = (location or '').lower()
        title_lower = (title or '').lower()
        if any(kw in (loc_lower + ' ' + title_lower) for kw in ['remote', 'virtual', 'work from home', 'wfh']):
            badges.append('<span class="badge badge-remote">🏠 Remote</span>')
        
        # Bilingual indicator
        if any(kw in (title_lower + ' ' + (company or '').lower()) for kw in ['japanese', 'bilingual', 'jp/en']):
            badges.append('<span class="badge badge-jp">🇯🇵 日本語</span>')
        
        strengths_str = ', '.join(strengths[:3]) if strengths else ''
        gaps_str = ', '.join(gaps[:3]) if gaps else ''
        flags_str = ', '.join(red_flags[:3]) if red_flags else ''
        
        html_parts.append(f"""
<div class="lead-card" data-band="{band}">
  <div class="lead-card-header">
    <div>
      <h3>{escape(title)}</h3>
      <div class="company">{escape(company)} · {escape(location)}</div>
      {'<div class="meta">' + ('<span>✓ ' + escape(strengths_str) + '</span>' if strengths_str else '') + '</div>' if strengths_str else ''}
    </div>
    <div style="white-space: nowrap;">{''.join(badges)}</div>
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
        <div class="value">{escape(source)}</div>
      </div>
      <div class="lead-detail-item">
        <div class="label">Date Found</div>
        <div class="value">{cycle['date']}</div>
      </div>
      <div class="lead-detail-item">
        <div class="label">Job Posting</div>
        <div class="value"><a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{escape(source)} ↗</a></div>
      </div>
    </div>
    
    {'<div class="details-section"><div class="details-section-title">✅ Strengths</div><ul class="strengths-list">' + ''.join(f'<li>{escape(s)}</li>' for s in strengths) + '</ul></div>' if strengths else ''}
    {'<div class="details-section"><div class="details-section-title">⚠️ Gaps</div><ul class="gaps-list">' + ''.join(f'<li>{escape(g)}</li>' for g in gaps) + '</ul></div>' if gaps else ''}
    {'<div class="details-section"><div class="details-section-title">🚩 Red Flags</div><ul class="flags-list">' + ''.join(f'<li>{escape(r)}</li>' for r in red_flags) + '</ul></div>' if red_flags else ''}
    
    <div class="action-bar">
      <a href="{escape(url)}" target="_blank" rel="noopener noreferrer" class="action-btn primary">🔗 Open Job Posting</a>
    </div>
  </div>
</div>
""")
    
    html_parts.append('</div>\n')
    
    # Note
    html_parts.append("""
<div class="obsidian-note" style="margin-top: 24px;">
  <strong>📝 Medium-fit leads have full email drafts in Obsidian.</strong> Open your vault → <code>20-PROJECTS/ayako-job-search/leads/</code> → today's <code>-email-drafts.md</code> for the personalized draft and EDD details.
</div>
""")
    
    html_parts.append(HTML_FOOTER.format(updated=datetime.now().strftime('%Y-%m-%d %H:%M')))
    return ''.join(html_parts)

def main():
    print("📝 Generating AYA Search Job Hunt flat site (no 3rd level)...")
    
    cycles = load_all_cycles()
    if not cycles:
        print("⚠️ No evaluated leads found in vault. Running site with empty state.")
        cycles = []
    
    # Create output directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    # No leads/ subdir needed anymore
    
    total_leads = sum(len(c['leads']) for c in cycles)
    
    # Generate index.html
    index_html = generate_index(cycles, total_leads)
    (OUTPUT_DIR / "index.html").write_text(index_html)
    print(f"  ✅ index.html — {len(cycles)} cycles, {total_leads} total leads")
    
    # Generate cycle pages (all details inline)
    for cycle in cycles:
        cycle_html = generate_cycle_page(cycle)
        (OUTPUT_DIR / f"cycle-{cycle['date']}.html").write_text(cycle_html)
        print(f"  ✅ cycle-{cycle['date']}.html — {len(cycle['leads'])} leads (all inline)")
    
    # Generate README
    readme = f"""# AYA Search Job Hunt

**🌐 Live Site: https://djphamdev.github.io/aya-job-hunt/**

Clean public view of remote job leads. **No PII, no email drafts.**

## Site Structure (Flat - No 3rd Level)
- `index.html` — Homepage with all search cycles
- `cycle-YYYY-MM-DD.html` — Per-cycle lead listing with ALL details inline
- `assets/` — CSS and JavaScript (dark mode default, light toggle, back-to-top)

## Privacy
- No personal info (name, email, phone, address)
- No email drafts or cover letters
- Only job posting links, employer info, fit scores, strengths/gaps
- Full drafts remain in private Obsidian vault

## Update
Run `python3 build-site.py` to regenerate from the latest evaluated leads in the Obsidian vault.

Last built: {datetime.now().isoformat()}
"""
    (OUTPUT_DIR / "README.md").write_text(readme)
    
    print(f"\n✅ Flat site generated: {OUTPUT_DIR}")
    print(f"   {len(cycles)} cycles · {total_leads} leads · 0 separate lead pages")

if __name__ == "__main__":
    main()