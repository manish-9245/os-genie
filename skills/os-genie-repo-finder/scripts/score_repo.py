#!/usr/bin/env python3
"""Deterministic repo scorer for os-genie-repo-finder.

Usage:
    gh issue list --repo <o/r> --state all --limit 50 \
      --json state,createdAt,closedAt > issues.json
    gh pr list --repo <o/r> --state all --limit 50 \
      --json state,createdAt,mergedAt > prs.json
    python3 score_repo.py --repo <owner/repo> --issues issues.json --prs prs.json \
      [--commits-30d N] [--commits-prior-30d M] [--mergers N] [--top-share 0.38] \
      [--released-days-ago N] [--docs 1]

Weights mirror gh-analyzer: momentum 30 / bus 25 / issue-health 20 /
PR-latency 15 / release-loop 10. Medians, not means. Stdlib only.
"""
import argparse
import json
import statistics
from datetime import datetime, timezone


def parse_dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def days(a, b):
    return (b - a).total_seconds() / 86400.0


def median(xs):
    return statistics.median(xs) if xs else None


def load_list(path):
    """Load a JSON list; empty/missing file yields [] instead of crashing."""
    try:
        with open(path) as f:
            raw = f.read().strip()
        return json.loads(raw) if raw else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--issues", default="")
    p.add_argument("--prs", default="")
    p.add_argument("--commits-30d", type=int, default=None)
    p.add_argument("--commits-prior-30d", type=int, default=None)
    p.add_argument("--mergers", type=int, default=None)
    p.add_argument("--top-share", type=float, default=None)
    p.add_argument("--released-days-ago", type=int, default=None)
    p.add_argument("--docs", type=int, default=None,
                   help="0-3: CONTRIBUTING + CI + runnable tests count")
    a = p.parse_args()
    now = datetime.now(timezone.utc)
    out = {"repo": a.repo, "breakdown": {}}

    # 1. Momentum (30)
    if a.commits_30d is None:
        m, why_m = 0, "no commit data: pass --commits-30d/--commits-prior-30d"
    else:
        prior = a.commits_prior_30d or 0
        trend = ((a.commits_30d - prior) / prior) if prior else (1.0 if a.commits_30d else 0.0)
        if a.commits_30d == 0:
            m, why_m = 0, "no commits in 30d"
        elif trend >= -0.2:
            m, why_m = 30, "steady/growing (%+d%%)" % round(trend * 100)
        elif trend >= -0.5:
            m, why_m = 18, "mild dip (%d%%)" % round(trend * 100)
        else:
            m, why_m = 5, "severe drop (%d%%)" % round(trend * 100)
    out["breakdown"]["momentum"] = {"pts": m, "why": why_m, "weight": 30}

    # 2. Bus factor (25)
    if a.mergers is None:
        b, why_b = 0, "unknown: pass --mergers + --top-share"
    elif a.mergers >= 3 and (a.top_share or 0) <= 0.5:
        b, why_b = 25, "%d mergers, top share %.0f%%" % (a.mergers, (a.top_share or 0) * 100)
    elif a.mergers >= 2:
        b, why_b = 15, "%d mergers" % a.mergers
    else:
        b, why_b = 5, "bus factor 1 risk"
    out["breakdown"]["bus_factor"] = {"pts": b, "why": why_b, "weight": 25}

    # 3. Issue health (20)
    if a.issues:
        issues = load_list(a.issues)
        closed = [i for i in issues if i.get("state") == "CLOSED"]
        rate = len(closed) / len(issues) if issues else 0
        lat = []
        for i in closed:
            c, cl = parse_dt(i.get("createdAt")), parse_dt(i.get("closedAt"))
            if c and cl:
                lat.append(days(c, cl))
        med = median(lat)
        if rate >= 0.7:
            h, why_h = 20, "%.0f%% closed" % (rate * 100)
        elif rate >= 0.5:
            h, why_h = 12, "%.0f%% closed" % (rate * 100)
        elif rate > 0:
            h, why_h = 4, "%.0f%% closed" % (rate * 100)
        else:
            h, why_h = 0, "no closures in sample"
        why_h += "; median close %.0fd" % med if med is not None else ""
    else:
        h, why_h = 0, "no issue data: pass --issues"
    out["breakdown"]["issue_health"] = {"pts": h, "why": why_h, "weight": 20}

    # 4. PR latency (15)
    if a.prs:
        prs = load_list(a.prs)
        merged = [x for x in prs if x.get("mergedAt")]
        lat = []
        for x in merged:
            c, mg = parse_dt(x.get("createdAt")), parse_dt(x.get("mergedAt"))
            if c and mg:
                lat.append(days(c, mg))
        med = median(lat)
        rate_m = len(merged) / len(prs) if prs else 0
        if med is None:
            pr_pts, why_p = 0, "no merges in sample"
        elif med <= 7:
            pr_pts, why_p = 15, "median merge %.1fd" % med
        elif med <= 21:
            pr_pts, why_p = 10, "median merge %.1fd" % med
        elif med <= 60:
            pr_pts, why_p = 5, "median merge %.1fd" % med
        else:
            pr_pts, why_p = 0, "median merge %.1fd" % med
        if rate_m < 0.3:
            pr_pts = min(pr_pts, 5)
            why_p += "; merge rate %.0f%% <30%%" % (rate_m * 100)
    else:
        pr_pts, why_p = 0, "no PR data: pass --prs"
    out["breakdown"]["pr_latency"] = {"pts": pr_pts, "why": why_p, "weight": 15}

    # 5. Release loop (10)
    if a.released_days_ago is None or a.docs is None:
        r, why_r = 0, "unknown: pass --released-days-ago + --docs (0-3)"
    else:
        score = 0
        if a.released_days_ago <= 90:
            score += 4
        score += min(a.docs, 3) * 2
        r, why_r = min(score, 10), "release %dd ago, docs %d/3" % (a.released_days_ago, a.docs)
    out["breakdown"]["release_loop"] = {"pts": r, "why": why_r, "weight": 10}

    total = sum(v["pts"] for v in out["breakdown"].values())
    out["score"] = total
    out["verdict"] = ("FIRST-PICK" if total >= 75 else
                      "RECOMMEND" if total >= 60 else "SKIP")
    print(json.dumps(out, indent=2))
    return 0 if total >= 60 else 2


if __name__ == "__main__":
    raise SystemExit(main())
