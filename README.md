# GrowthOS Launch — Strategy Browser

Internal strategy & planning archive for the GrowthOS launch (Jun 2, 2026).

The live site is `index.html` — hosted via GitHub Pages, or open it locally with any browser, or run a quick local server:

```bash
python3 -m http.server 8000
# then open http://localhost:8000/
```

## What's in here

| File | What it is |
|---|---|
| `index.html` | The browsable strategy site — opens in any browser, no build step |
| `Launch Video - Narrative Spine.md` | Four-beat arc captured from Marcel + Harmony meeting (May 27) |
| `Launch Video - 90s Script - Marcel V2.md` | Current draft of the 90-second Marcel cut |
| `Launch Video - 90s Script - Marcel V1.md` | Prior draft (kept for diff) |
| `Episode 1 - Surrogate Card.md` | One-page handout for the Whiteboard Sessions surrogate |
| `Will - Video Content Expansion Notes.md` | Will's expansion proposals — Whiteboard Sessions + Charlie |
| `Survey Insights - GrowthOS Launch.md` | N=100 survey insights for the launch |
| `analyze_survey.py` | Reproducible analysis script — re-run as more responses come in |
| `render_charlie.py` | Charlie character render pipeline (gpt-image-2) |
| `assets/` | Charlie character renders (10 style variants + prototypes) |
| `🎬 GrowthOS Marketing Week ... .md` | Source Notion export — Marketing Week plan |

## Excluded from git (see `.gitignore`)

- `.env` — OpenAI API key
- `Survey - High Intent Leads.csv` — contains PII (real names + emails)
- `.venv/` — local Python environment
- `.DS_Store`, IDE caches

## Re-running the survey analysis

```bash
# Drop a fresh export at ~/Downloads/responses_rows.json, then:
python3 analyze_survey.py
```

This regenerates the leads CSV in this folder and prints all distributions and composite signals.

## Re-rendering Charlie style variants

```bash
source .venv/bin/activate
python3 render_charlie.py style-01-photoreal style-02-pixar  # or any scene ids
python3 render_charlie.py --list                              # to see all scenes
```
