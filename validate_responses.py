#!/usr/bin/env python3
"""
Survey response authenticity validation.

Scores each response 0-100 for spam/synthetic risk across 7 signal categories
(email, name, position, free-text, consistency, IP clustering, repetition),
classifies into LIKELY_REAL / UNCERTAIN / SUSPICIOUS / CONFIRMED_SPAM, and
writes a flagged-rows CSV for manual review.

Usage:
    python3 validate_responses.py [--input PATH] [--out PATH]

Defaults:
    --input  ~/Downloads/responses_rows.json
    --out    ./Survey - Flagged Responses.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path


# ---------- Heuristic vocabularies ----------

FREE_MAIL = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "aol.com", "live.com", "msn.com", "mail.com", "gmx.com",
    "yandex.com", "zoho.com", "fastmail.com", "me.com", "mac.com",
    "ymail.com",
}

# Privacy email providers — frequently used by panel/synthetic accounts.
# Real users sometimes use these, so this is a soft signal.
PRIVACY_MAIL = {"proton.me", "protonmail.com", "tuta.io", "tutamail.com", "tutanota.com"}

# Known disposable / throwaway providers.
DISPOSABLE = {
    "mailinator", "guerrillamail", "tempmail", "10minutemail", "throwaway",
    "sharklasers", "yopmail", "getnada", "fakeinbox", "trashmail", "maildrop",
    "mintemail", "dispostable", "fanclub.pm", "digdig.org",
}

# Domain farm patterns observed in this dataset.
# Pattern: <2-3 random letters>.<random word>.<tld> on weird TLDs.
DOMAIN_FARM_TLDS = {".xyz", ".life", ".cloud", ".pm", ".org"}
DOMAIN_FARM_PARENTS = {
    "xintaitong.com", "rehearsalk.com", "lingeringp.com", "youngestsd.com",
    "huhutu.cloud", "tiankaixin77.xyz", "vnaikai.life",
}

MARKETING_POSITION_KEYWORDS = [
    "market", "growth", "brand", "content", "seo", "founder", "ceo", "cmo",
    "vp ", "head of", "director", "gtm", "demand gen", "revops", "rev ops",
    "communications", "comms", "social", "pr ", "public relations",
    "campaign", "performance", "acquisition", "lifecycle", "product market",
    "evangelist", "advoca", "partner",
]

OFF_ICP_KEYWORDS = [
    "kennel", "transmitter", "mail superintendent", "food marketer",
    "grain marketer", "cosmetics marketer", "janitor", "plumber",
    "farm and home", "truck driver",
]

# AI-text fingerprints. Each occurrence adds to the suspicion score.
AI_ISMS = [
    "leveraging", "leverage", "streamline", "streamlining", "robust",
    "seamless", "actionable insights", "in summary", "moreover",
    "furthermore", "key takeaways", "comprehensive", "cutting-edge",
    "state-of-the-art", "synergize", "synergy", "navigate complex",
    "harness the power", "unlock", "transformative", "revolutionize",
    "real-time insights", "data-driven decision",
]

TEMPLATED_OPENINGS = [
    "our team is most excited about",
    "our team is especially excited about",
    "we're most excited about",
    "we are most excited about",
    "we are particularly",
    "we wish ai could",
    "i wish ai could",
    "here are several different",
    "here are several",
    "natural responses for your reference",
    "1. we are",
    "1. our team",
]

# Smoking-gun phrases that are an instant CONFIRMED_SPAM signal.
SMOKING_GUNS = [
    "here are several different natural responses for your reference",
    "natural responses for your reference",
    "1. ", # only counts if combined with other signals (handled below)
]

SPAM_NAME_TOKENS = {"test", "asdf", "qwerty", "admin", "user", "abc", "xyz", "aaaa"}


# ---------- Loading ----------

def load(path: str) -> list[dict]:
    with open(path) as f:
        rows = json.load(f)
    for r in rows:
        a = r.get("answers")
        if isinstance(a, str):
            try:
                a = json.loads(a)
            except json.JSONDecodeError:
                a = {}
        r["_a"] = a or {}
    return rows


# ---------- Per-category scoring ----------

def score_email(r: dict, all_domains: Counter) -> tuple[int, list[str]]:
    flags: list[str] = []
    score = 0
    email = (r.get("email") or "").strip().lower()
    if not email or "@" not in email:
        return 60, ["email:missing-or-invalid"]
    local, _, domain = email.rpartition("@")

    if any(d in domain for d in DISPOSABLE):
        score += 50
        flags.append("email:disposable")

    parent = ".".join(domain.split(".")[-2:])
    if parent in DOMAIN_FARM_PARENTS or any(p in domain for p in DOMAIN_FARM_PARENTS):
        score += 60
        flags.append(f"email:domain-farm({parent})")
    elif domain.count(".") >= 2 and len(domain.split(".")[0]) <= 3:
        # short random subdomain like zz.something.com
        score += 25
        flags.append("email:short-random-subdomain")

    if domain in PRIVACY_MAIL:
        score += 15
        flags.append("email:privacy-provider")

    if domain in FREE_MAIL:
        # Personal email is fine by itself. Score only if combined with
        # numeric-suffix local-part pattern (e.g. johnsmith3859).
        m = re.search(r"\d{3,}$", local)
        if m:
            score += 15
            flags.append(f"email:numeric-suffix({m.group(0)})")

    if local.startswith(("info", "admin", "contact", "hello", "support", "noreply")):
        score += 15
        flags.append("email:generic-prefix")

    # Local-part doesn't share a token with first/last name
    fn = (r.get("first_name") or "").lower()
    ln = (r.get("last_name") or "").lower()
    if fn and len(fn) >= 3 and ln and len(ln) >= 3:
        if fn not in local and ln not in local:
            score += 5
            flags.append("email:no-name-overlap")

    return score, flags


def score_name(r: dict) -> tuple[int, list[str]]:
    flags: list[str] = []
    score = 0
    f = (r.get("first_name") or "").strip()
    l = (r.get("last_name") or "").strip()

    if not f:
        score += 25
        flags.append("name:missing-first")
    if not l or len(l) <= 1:
        score += 25
        flags.append("name:missing-last")
    if re.search(r"\d", f + l):
        score += 30
        flags.append("name:has-digits")
    if f and (f == f.upper() or f == f.lower()) and len(f) > 3:
        score += 5
        flags.append("name:case-suspicious")
    full = (f + l).lower()
    if any(t in full for t in SPAM_NAME_TOKENS):
        score += 50
        flags.append("name:spam-token")

    return score, flags


def score_position(r: dict) -> tuple[int, list[str]]:
    flags: list[str] = []
    score = 0
    pos = (r.get("position") or "").strip()
    if not pos:
        score += 20
        flags.append("position:missing")
        return score, flags

    low = pos.lower()
    if any(kw in low for kw in OFF_ICP_KEYWORDS):
        score += 50
        flags.append("position:off-icp")
    has_mkt = any(kw in low for kw in MARKETING_POSITION_KEYWORDS)
    if not has_mkt:
        score += 10
        flags.append("position:no-marketing-marker")
    else:
        score -= 5  # legitimacy bonus
        flags.append("position:marketing-marker-ok")

    # Very short positions like "Director", "Manager" alone (with no domain context)
    # are a panel signal when paired with other red flags. We don't penalize alone.
    if len(pos.split()) == 1 and low in {"director", "manager", "marketing"}:
        score += 10
        flags.append(f"position:single-word({low})")

    return score, flags


def score_free_text(r: dict) -> tuple[int, list[str]]:
    flags: list[str] = []
    score = 0
    a = r["_a"]

    q5 = a.get("q5_text") or ""  # may not exist
    q10 = a.get("q10") or ""
    q21 = a.get("q21") or ""

    all_text = " ".join([str(q10), str(q21)]).strip()
    low = all_text.lower()

    if not q21.strip():
        score += 10
        flags.append("text:q21-empty")

    # Smoking guns
    if "natural responses for your reference" in low:
        score += 80
        flags.append("text:SMOKING-GUN-template")
    # Numbered-list response (e.g. "1. We are excited...  2. Our team...")
    if re.search(r"\b1\.\s+\w+.{0,150}\b2\.\s+\w+", all_text):
        score += 35
        flags.append("text:numbered-list")

    # Templated openings
    for pat in TEMPLATED_OPENINGS:
        if pat in low:
            score += 15
            flags.append(f"text:template({pat[:30]})")
            break  # only count once

    # AI-isms density (cap contribution at 25)
    ai_hits = sum(1 for w in AI_ISMS if w in low)
    if ai_hits:
        score += min(ai_hits * 5, 25)
        flags.append(f"text:ai-isms({ai_hits})")

    # Very short or empty across all text fields
    if len(all_text) < 30:
        score += 10
        flags.append("text:very-short")

    # Specificity check: does the response mention a specific tool, number, or person?
    has_specifics = bool(re.search(
        r"\b(chatgpt|claude|gemini|notebook|granola|airops|cassidy|hubspot|"
        r"salesforce|outreach|gong|clay|notion|figma|webflow|wordpress|"
        r"perplexity|cursor|lovable|n8n|zapier|\$\d|\d+%)\b", low))
    if not has_specifics and len(all_text) > 30:
        score += 5
        flags.append("text:no-specifics")

    return score, flags


def score_consistency(r: dict) -> tuple[int, list[str]]:
    flags: list[str] = []
    score = 0
    a = r["_a"]
    role = a.get("q1")
    stage = a.get("q2")
    team = a.get("q3")
    budget = a.get("q12")

    if stage == "bootstrapped" and budget in {"150k-plus", "75-150k"}:
        score += 15
        flags.append("consist:bootstrapped-high-budget")
    if team == "just-me" and role in {"vp-marketing", "marketing-ops", "content-lead", "growth-lead"}:
        score += 10
        flags.append(f"consist:solo-team-as-{role}")
    if stage == "public" and role == "founder":
        score += 5
        flags.append("consist:public-stage-founder")
    if role == "other":
        score += 3
        flags.append("consist:role-other")
    # Counting answer pattern: if the user picked >5 options on every multi-select,
    # they may be just clicking everything.
    multiselect_keys = ["q6", "q7", "q8", "q19", "q20", "q25"]
    big_clicks = sum(
        1 for k in multiselect_keys
        if isinstance(a.get(k), list) and len(a[k]) >= 5
    )
    if big_clicks >= 4:
        score += 8
        flags.append("consist:click-everything")

    return score, flags


# ---------- Cross-row signals ----------

def cluster_flags(rows: list[dict]) -> dict[str, list[str]]:
    """Compute IP-hash, email-domain, and template-text clusters."""
    by_id: dict[str, list[str]] = defaultdict(list)

    ip_groups: defaultdict[str, list[dict]] = defaultdict(list)
    for r in rows:
        ip = r.get("ip_hash")
        if ip:
            ip_groups[ip].append(r)

    for ip, grp in ip_groups.items():
        if len(grp) >= 5:
            for r in grp:
                by_id[r["id"]].append(f"cluster:ip-mega({len(grp)})")
        elif len(grp) >= 3:
            for r in grp:
                by_id[r["id"]].append(f"cluster:ip-medium({len(grp)})")
        elif len(grp) == 2:
            for r in grp:
                by_id[r["id"]].append("cluster:ip-pair")

    # Domain clusters (only count for non-corporate-looking domains)
    dom_groups: defaultdict[str, list[dict]] = defaultdict(list)
    for r in rows:
        dom = (r.get("email") or "").rpartition("@")[-1].lower()
        if dom:
            dom_groups[dom].append(r)
    for dom, grp in dom_groups.items():
        if dom in FREE_MAIL or dom in PRIVACY_MAIL:
            continue
        if len(grp) >= 4:
            for r in grp:
                by_id[r["id"]].append(f"cluster:domain-many({dom},n={len(grp)})")

    return by_id


def cluster_severity(cluster: list[str]) -> int:
    score = 0
    for f in cluster:
        if "ip-mega" in f:
            score += 50
        elif "ip-medium" in f:
            score += 25
        elif "ip-pair" in f:
            score += 10
        elif "domain-many" in f:
            score += 30
    return score


# ---------- Aggregation ----------

def classify(score: int) -> str:
    if score >= 100:
        return "CONFIRMED_SPAM"
    if score >= 60:
        return "SUSPICIOUS"
    if score >= 30:
        return "UNCERTAIN"
    return "LIKELY_REAL"


def evaluate(rows: list[dict]) -> list[dict]:
    domains = Counter(
        (r.get("email") or "").rpartition("@")[-1].lower() for r in rows
    )
    cluster_by_id = cluster_flags(rows)

    out = []
    for r in rows:
        e_s, e_f = score_email(r, domains)
        n_s, n_f = score_name(r)
        p_s, p_f = score_position(r)
        t_s, t_f = score_free_text(r)
        c_s, c_f = score_consistency(r)
        cluster = cluster_by_id.get(r["id"], [])
        cl_s = cluster_severity(cluster)

        total = max(0, e_s + n_s + p_s + t_s + c_s + cl_s)
        flags = e_f + n_f + p_f + t_f + c_f + cluster
        out.append({
            "id": r["id"],
            "email": r.get("email"),
            "name": f"{r.get('first_name') or ''} {r.get('last_name') or ''}".strip(),
            "position": r.get("position"),
            "score": total,
            "category": classify(total),
            "flags": "; ".join(flags),
            "created_at": r.get("created_at"),
            "advisor_optin": r.get("optin_advisor"),
            "report_optin": r.get("optin_report"),
            "ip_hash": (r.get("ip_hash") or "")[:16],
            "scores_breakdown": (
                f"email={e_s} name={n_s} pos={p_s} text={t_s} "
                f"consist={c_s} cluster={cl_s}"
            ),
        })
    return out


# ---------- Reporting ----------

def print_summary(results: list[dict], total: int) -> None:
    cats = Counter(r["category"] for r in results)
    print(f"\n=== RESPONSE QUALITY SUMMARY (n={total}) ===")
    order = ["LIKELY_REAL", "UNCERTAIN", "SUSPICIOUS", "CONFIRMED_SPAM"]
    for c in order:
        n = cats.get(c, 0)
        pct = 100 * n / total if total else 0
        print(f"  {c:18s} {n:4d}  ({pct:.0f}%)")

    print("\n=== TOP-SCORING FLAGS (most common) ===")
    all_flags: Counter[str] = Counter()
    for r in results:
        for f in r["flags"].split("; "):
            if not f:
                continue
            # Bucket parametrized flags
            key = re.sub(r"\(.*\)", "", f)
            all_flags[key] += 1
    for f, n in all_flags.most_common(25):
        print(f"  {f:40s} {n:4d}")

    susp = [r for r in results if r["category"] in {"SUSPICIOUS", "CONFIRMED_SPAM"}]
    optin_in_susp = sum(1 for r in susp if r["advisor_optin"])
    print(f"\nAdvisor-opted-in inside suspicious/confirmed-spam: {optin_in_susp}")
    print("These are the leads that would otherwise have been sent to sales.")


def write_csv(results: list[dict], out_path: str) -> int:
    review = [r for r in results if r["category"] != "LIKELY_REAL"]
    review.sort(key=lambda r: r["score"], reverse=True)
    fields = [
        "category", "score", "name", "email", "position", "advisor_optin",
        "report_optin", "created_at", "ip_hash", "flags", "scores_breakdown",
        "id",
    ]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in review:
            w.writerow({k: r.get(k) for k in fields})
    return len(review)


def main() -> None:
    p = argparse.ArgumentParser()
    home = os.path.expanduser("~")
    p.add_argument("--input", default=f"{home}/Downloads/responses_rows.json")
    p.add_argument(
        "--out",
        default=str(Path(__file__).parent / "Survey - Flagged Responses.csv"),
    )
    args = p.parse_args()

    rows = load(args.input)
    n = len(rows)
    print(f"Loaded {n} responses from {args.input}")

    results = evaluate(rows)
    print_summary(results, n)

    written = write_csv(results, args.out)
    print(f"\nWrote {written} flagged rows to: {args.out}")
    print("(LIKELY_REAL rows are not in the file; they don't need review.)")


if __name__ == "__main__":
    main()
