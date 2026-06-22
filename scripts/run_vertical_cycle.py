#!/usr/bin/env python
"""Run a small evidence-linked research cycle from literature to ranked outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from industrial_research_lab.pipeline import PROFILES, run_profile


QUERIES = (
    '"stochastic inventory" disruption threshold control',
    '"first passage" reliability maintenance industrial',
    '"supply chain disruption" "Markov decision process"',
)

HYPOTHESES = (
    ("H1", "Near-critical disruption amplification", "At fixed positive capacity margin, increasing disruption probability monotonically increases finite-horizon collapse probability.", "inventory disruption supply chain", 4.45),
    ("H2", "Criticality-adaptive buffer", "A state-dependent buffer lowers collapse probability relative to a fixed buffer at matched average inventory.", "inventory threshold control", 4.30),
    ("H3", "Network criticality early warning", "A diffusion-based criticality index predicts disruption cascades earlier than utilization alone.", "network criticality cascade diffusion", 4.15),
    ("H4", "Robust threshold under uncertain drift", "A drift-robust threshold sacrifices little nominal cost while reducing tail collapse risk under parameter error.", "robust stochastic threshold drift", 4.05),
    ("H5", "First-passage service constraint", "Optimizing a first-passage service constraint produces different buffers than steady-state service-level optimization.", "first passage service level buffer", 3.95),
)


def fetch_openalex(max_items: int) -> list[dict]:
    records: dict[str, dict] = {}
    per_query = max(3, (max_items + len(QUERIES) - 1) // len(QUERIES))
    for query in QUERIES:
        params = urllib.parse.urlencode({
            "search": query,
            "per-page": per_query,
            "select": "id,doi,title,publication_year,cited_by_count,primary_location,authorships",
            "mailto": "research-factory@example.com",
        })
        request = urllib.request.Request(
            f"https://api.openalex.org/works?{params}",
            headers={"User-Agent": "industrial-risk-control/0.1 (research prototype)"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        for item in payload.get("results", []):
            key = item.get("doi") or item.get("id")
            if not key or key in records:
                continue
            source = ((item.get("primary_location") or {}).get("source") or {}).get("display_name")
            authors = [
                (a.get("author") or {}).get("display_name", "")
                for a in item.get("authorships", [])[:4]
            ]
            records[key] = {
                "openalex_id": item.get("id"),
                "doi": item.get("doi"),
                "title": item.get("title"),
                "year": item.get("publication_year"),
                "cited_by_count": item.get("cited_by_count", 0),
                "source": source,
                "authors": authors,
                "retrieval_query": query,
            }
    return sorted(records.values(), key=lambda x: (-x["cited_by_count"], x["title"] or ""))[:max_items]


def corpus_text(records: list[dict]) -> str:
    return " ".join((r.get("title") or "").lower() for r in records)


def evidence_count(text: str, terms: str) -> int:
    return sum(text.count(term) for term in terms.split())


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def checksum_tree(root: Path) -> None:
    manifest_path = root / "VERTICAL_CYCLE_MANIFEST.json"
    checksum_path = root / "CHECKSUMS.sha256"
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path not in {manifest_path, checksum_path}:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            entries.append({"path": path.relative_to(root).as_posix(), "sha256": digest, "bytes": path.stat().st_size})
    manifest_path.write_text(json.dumps({"generated_utc": datetime.now(timezone.utc).isoformat(), "files": entries}, indent=2), encoding="utf-8")
    checksum_path.write_text("".join(f"{e['sha256']}  {e['path']}\n" for e in entries), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/vertical-cycle"))
    parser.add_argument("--max-literature-items", type=int, default=12)
    parser.add_argument("--pilot-profile", choices=("ci", "smoke"), default="ci")
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    records = fetch_openalex(args.max_literature_items)
    if len(records) < 5:
        raise RuntimeError(f"Only {len(records)} literature records retrieved; at least 5 required")
    literature = root / "literature"
    literature.mkdir(exist_ok=True)
    (literature / "OPENALEX_RECORDS.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    write_csv(literature / "CORPUS.csv", records, ["openalex_id", "doi", "title", "year", "cited_by_count", "source", "authors", "retrieval_query"])

    text = corpus_text(records)
    ranked = []
    for hid, name, claim, terms, base in HYPOTHESES:
        support = evidence_count(text, terms)
        ranked.append({"rank": 0, "id": hid, "hypothesis": name, "falsifiable_claim": claim, "title_term_hits": support, "score": round(base + min(support, 4) * 0.05, 2), "novelty_status": "provisional_requires_full_review"})
    ranked.sort(key=lambda x: -x["score"])
    for index, item in enumerate(ranked, 1):
        item["rank"] = index
    write_csv(root / "hypotheses" / "HYPOTHESES_RANKED.csv", ranked, list(ranked[0]))

    gap_lines = ["# Evidence-Limited Gap Map", "", f"Live OpenAlex search retrieved {len(records)} deduplicated records.", "", "## Candidate gaps"]
    for item in ranked[:3]:
        gap_lines.append(f"- **{item['hypothesis']}**: {item['title_term_hits']} title-term hits; novelty remains provisional pending full-text systematic review.")
    gap_lines += ["", "## Boundary", "Absence or rarity of title terms is not proof of novelty. DOI/OpenAlex identifiers establish traceability, not exhaustive coverage."]
    (literature / "GAP_MAP.md").write_text("\n".join(gap_lines) + "\n", encoding="utf-8")

    selected = ranked[0]
    experiment_dir = root / "experiments"
    experiment_dir.mkdir(exist_ok=True)
    experiment = {
        "selected_hypothesis": selected["id"], "claim": selected["falsifiable_claim"],
        "pilot_profile": args.pilot_profile, "master_seed": 20260429,
        "primary_metric": "collapse_probability", "comparison": "adjacent disruption probabilities",
        "promotion_rule": "infrastructure pass and positive adjacent risk differences across both configured seeds",
        "frozen_before_run": True,
    }
    (experiment_dir / "FROZEN_EXPERIMENT.json").write_text(json.dumps(experiment, indent=2), encoding="utf-8")

    pilot = run_profile(PROFILES[args.pilot_profile], root / "results" / "pilot", resume=not args.fresh)
    direction_stable = bool(pilot["infrastructure_pass"] and all(d["risk_difference"] > 0 for d in pilot["adjacent_risk_differences"]))
    claim_rows = [{"claim_id": selected["id"], "claim": selected["falsifiable_claim"], "literature_evidence": f"{len(records)} live records screened by title/metadata", "computational_evidence": "results/pilot/summary.json", "status": "pilot_supported" if direction_stable else "rejected", "limitation": "small pilot; candidate novelty only"}]
    write_csv(root / "claims" / "CLAIM_EVIDENCE_MATRIX.csv", claim_rows, list(claim_rows[0]))

    report_dir = root / "reports"
    report_dir.mkdir(exist_ok=True)
    differences = [round(d["risk_difference"], 4) for d in pilot["adjacent_risk_differences"]]
    report = ["# Vertical Cycle Portfolio Report", "", "## Outcome", f"Selected `{selected['id']}`: **{selected['hypothesis']}**.", f"The deterministic `{args.pilot_profile}` pilot infrastructure pass was `{pilot['infrastructure_pass']}`.", "", "## Evidence", f"- {len(records)} relevance-ranked OpenAlex records were retrieved with traceable identifiers.", "- Hypotheses were ranked using fixed scores plus transparent title-term evidence.", "- The experiment specification was frozen before computation.", f"- Adjacent collapse-risk differences were {differences}; all were positive: `{direction_stable}`.", "", "## Decision", "PROMOTE TO A LARGER CONFIRMATORY RUN" if direction_stable else "REJECT UNTIL EFFECT DIRECTION IS STABLE", "", "## Scientific boundary", "This cycle demonstrates end-to-end orchestration and pilot evidence for the stated monotonic direction. It does not establish novelty, causality, or publication readiness; those require systematic full-text review and confirmatory replication."]
    (report_dir / "PORTFOLIO_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    skeptical = ["# Skeptical Review", "", "- Search coverage is small and limited to OpenAlex metadata.", "- Title-term counts are prioritization signals, not novelty evidence.", "- The pilot validates infrastructure and preliminary effect direction, not a paper claim.", "- Confirmation needs broader sensitivity analysis and independent replication."]
    (report_dir / "SKEPTICAL_REVIEW.md").write_text("\n".join(skeptical) + "\n", encoding="utf-8")
    status = {"status": "complete", "live_literature_search": True, "records": len(records), "selected_hypothesis": selected["id"], "pilot_pass": bool(pilot["infrastructure_pass"]), "effect_direction_stable": direction_stable, "novelty_established": False, "paper_ready": False}
    (root / "VERTICAL_CYCLE_STATUS.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    checksum_tree(root)
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
