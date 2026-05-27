#!/usr/bin/env python3
"""
Survey analysis for GrowthOS launch insights.

Reads responses_rows.json (export from the survey backend) and prints / writes
the headline stats, narrative-validation cuts, cross-tabs, and a vetted
high-intent lead list.

Usage:
    python3 analyze_survey.py [--input PATH] [--leads-out PATH]

Defaults:
    --input      ~/Downloads/responses_rows.json
    --leads-out  ./Survey - High Intent Leads.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path


# Question label map (must match the survey form)
QUESTIONS = {
    "q1": "Role",
    "q2": "Stage",
    "q3": "Team size",
    "q4": "AI adoption (1-10)",
    "q5": "How AI is changing work",
    "q6": "AI produced last 90d",
    "q7": "AI use areas",
    "q8": "AI tools",
    "q9": "AI spend visibility",
    "q11": "Primary inbound driver",
    "q12": "Monthly mkt budget",
    "q13": "Content/SEO/organic spend",
    "q14": "Content management model",
    "q15": "Consolidated view of web/content",
    "q16": "Content-to-revenue attribution",
    "q17": "AI changed publishing output",
    "q18": "Clearest AI ROI",
    "q19": "Biggest AI challenge (top 2)",
    "q20": "AI creates new problems",
    "q22": "Tracking AI brand mentions",
    "q23": "AI search strategy",
    "q24": "Biggest barrier to AI visibility",
    "q25": "AI investment next 12mo (top 2)",
    "q26": "AI playbook",
    "q27": "Biggest content/organic blocker",
}

# Likely off-ICP position keywords (manual heuristic)
OFF_ICP_KEYWORDS = [
    "kennel", "transmitter", "mail superintendent", "food marketer",
    "grain marketer", "cosmetics marketer", "janitor", "plumber",
    "farm and home", "truck driver",
]


def load_responses(path: str) -> list[dict]:
    with open(path) as f:
        rows = json.load(f)
    out = []
    for r in rows:
        a = r.get("answers")
        if isinstance(a, str):
            try:
                a = json.loads(a)
            except json.JSONDecodeError:
                a = {}
        out.append({**r, "_a": a or {}})
    return out


def dist(rows: list[dict], field: str) -> Counter:
    c: Counter = Counter()
    for r in rows:
        v = r["_a"].get(field)
        if isinstance(v, list):
            for x in v:
                c[x] += 1
        else:
            c[v] += 1
    return c


def pct(n: int, total: int) -> float:
    return 100.0 * n / total if total else 0.0


def print_dist(label: str, c: Counter, total: int) -> None:
    print(f"\n=== {label} ===")
    for v, n in c.most_common():
        print(f"  {v!s:<35} {n:>3}  ({pct(n, total):.0f}%)")


def crosstab(rows, field_a, field_b) -> dict[str, Counter]:
    out: defaultdict[str, Counter] = defaultdict(Counter)
    for r in rows:
        a = r["_a"].get(field_a)
        b = r["_a"].get(field_b)
        if isinstance(b, list):
            for bv in b:
                out[a][bv] += 1
        else:
            out[a][b] += 1
    return out


def write_high_intent_csv(rows: list[dict], out_path: str) -> int:
    """Write the high-intent lead list.

    Definition: opted in for an advisor session AND planning AI-visibility
    investment AND not currently tracking AI brand mentions.
    """
    fieldnames = [
        "name", "email", "position", "role", "stage", "team_size", "budget",
        "tracking_state", "strategy_state", "barrier", "off_icp_flag",
    ]
    n = 0
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            a = r["_a"]
            investing = isinstance(a.get("q25"), list) and "ai-visibility" in a["q25"]
            not_tracking = a.get("q22") in {"know-should", "checked-few", "not-priority"}
            if not (investing and not_tracking and r.get("optin_advisor")):
                continue
            pos = (r.get("position") or "").lower()
            off_icp = any(kw in pos for kw in OFF_ICP_KEYWORDS)
            w.writerow({
                "name": f"{r.get('first_name', '')} {r.get('last_name', '')}".strip(),
                "email": r.get("email", ""),
                "position": r.get("position", ""),
                "role": a.get("q1", ""),
                "stage": a.get("q2", ""),
                "team_size": a.get("q3", ""),
                "budget": a.get("q12", ""),
                "tracking_state": a.get("q22", ""),
                "strategy_state": a.get("q23", ""),
                "barrier": a.get("q24", ""),
                "off_icp_flag": "review" if off_icp else "",
            })
            n += 1
    return n


def main() -> None:
    p = argparse.ArgumentParser()
    home = os.path.expanduser("~")
    p.add_argument("--input", default=f"{home}/Downloads/responses_rows.json")
    p.add_argument(
        "--leads-out",
        default=str(Path(__file__).parent / "Survey - High Intent Leads.csv"),
    )
    args = p.parse_args()

    rows = load_responses(args.input)
    n = len(rows)
    print(f"Total responses: {n}")

    for q, label in QUESTIONS.items():
        print_dist(f"{q.upper()} · {label}", dist(rows, q), n)

    # Composite signals used in the launch insights page
    icp_count = sum(
        1 for r in rows
        if r["_a"].get("q1") in {"vp-marketing", "growth-lead", "founder", "content-lead"}
        and r["_a"].get("q2") in {"seed", "series-a", "series-bc", "bootstrapped"}
        and r["_a"].get("q12") in {"10-25k", "25-75k", "75-150k", "150k-plus"}
    )
    frag = sum(
        1 for r in rows
        if r["_a"].get("q15") in {"partial", "no-separate", "no-visibility"}
        or r["_a"].get("q27") == "fragmentation"
    )
    eng_pain = sum(
        1 for r in rows
        if (
            "skill-loss" in (r["_a"].get("q19") or [])
            or "hiring" in (r["_a"].get("q19") or [])
            or "tools" in (r["_a"].get("q19") or [])
            or "tool-churn" in (r["_a"].get("q20") or [])
        )
    )
    attr = sum(
        1 for r in rows
        if r["_a"].get("q16") in {"partial", "mostly-no", "dont-try"}
    )
    high_intent_gap = sum(
        1 for r in rows
        if isinstance(r["_a"].get("q25"), list)
        and "ai-visibility" in r["_a"]["q25"]
        and r["_a"].get("q22") in {"know-should", "checked-few", "not-priority"}
    )
    advisor_optin = sum(1 for r in rows if r.get("optin_advisor"))
    report_optin = sum(1 for r in rows if r.get("optin_report"))

    print("\n=== COMPOSITE SIGNALS ===")
    print(f"  ICP fit (role + stage + budget):        {icp_count} ({pct(icp_count, n):.0f}%)")
    print(f"  Fragmentation pain:                     {frag} ({pct(frag, n):.0f}%)")
    print(f"  'Marketing Engineer' disenchantment:    {eng_pain} ({pct(eng_pain, n):.0f}%)")
    print(f"  Attribution pain:                       {attr} ({pct(attr, n):.0f}%)")
    print(f"  High-intent gap (planning AEO,         ")
    print(f"   not yet tracking):                     {high_intent_gap} ({pct(high_intent_gap, n):.0f}%)")
    print(f"  Opted in for report:                    {report_optin} ({pct(report_optin, n):.0f}%)")
    print(f"  Opted in for advisor session:           {advisor_optin} ({pct(advisor_optin, n):.0f}%)")

    leads = write_high_intent_csv(rows, args.leads_out)
    print(f"\nHigh-intent leads written to: {args.leads_out}")
    print(f"  (n={leads})")


if __name__ == "__main__":
    main()
