# AYA Search Job Hunt

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
