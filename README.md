# AYA Search Job Hunt

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

Last built: 2026-08-25T06:07:50.635675
