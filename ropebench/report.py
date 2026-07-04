"""Render benchmark metrics as a markdown table and CSV."""

from __future__ import annotations

import csv
import io

from .runner import BUCKETS, KINDS, ProbeFilter, RegimeMetrics, paired

_ORDER = ("full-history", "truncate", "summary", "rope", "rope-unbound")
_TERCILES = ("early", "mid", "late")


def _ordered(metrics: dict[str, RegimeMetrics]) -> list[RegimeMetrics]:
    return [metrics[n] for n in _ORDER if n in metrics] + [
        m for n, m in metrics.items() if n not in _ORDER
    ]


def markdown(metrics: dict[str, RegimeMetrics]) -> str:
    lines = [
        "| Regime | Acc | short | medium | long | fact | decision | status "
        "| retrieval | tokens | acc/10k tok |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for m in _ordered(metrics):
        cells = [
            m.name,
            f"{m.accuracy():.0%}",
            *(f"{m.accuracy(bucket=b):.0%}" for b in BUCKETS),
            *(f"{m.accuracy(kind=k):.0%}" for k in KINDS),
            f"{m.retrieval_rate:.0%}",
            f"{m.total_tokens:,}",
            f"{m.efficiency:.1f}",
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def paired_table(metrics: dict[str, RegimeMetrics], anchor: str = "rope") -> str:
    """Per condition-pair: n, point diff, 95% CI, verdict — anchored on the
    rope, so every claim in prose has a traceable CI (S1)."""
    if anchor not in metrics:
        return ""
    lines = [
        f"| {anchor} vs | n | {anchor} acc | other acc | diff | 95% CI | verdict |",
        "|---|---|---|---|---|---|---|",
    ]
    for name in _ORDER:
        if name == anchor or name not in metrics:
            continue
        r = paired(metrics[anchor], metrics[name])
        lines.append(
            f"| {name} | {r.n} | {r.mean_a:.0%} | {r.mean_b:.0%} | "
            f"{r.diff:+.1%} | [{r.ci_low:+.1%}, {r.ci_high:+.1%}] | "
            f"{r.verdict.replace('A-', anchor + '-')} |"
        )
    return "\n".join(lines)


def age_stratified_table(
    metrics: dict[str, RegimeMetrics], n_turns: int,
    condition: str = "summary", anchor: str = "rope",
) -> str:
    """Recall by fact-age tercile — the lead figure for 'summaries eat OLD
    facts'. Compares ``condition`` against ``anchor`` per tercile with CIs."""
    if condition not in metrics or anchor not in metrics:
        return ""
    lines = [
        f"| fact age | n | {condition} recall | {anchor} recall | diff | 95% CI |",
        "|---|---|---|---|---|---|",
    ]
    def in_tercile(tercile: str) -> ProbeFilter:
        return lambda p: p.age_tercile(n_turns) == tercile

    for tercile in _TERCILES:
        r = paired(metrics[condition], metrics[anchor], where=in_tercile(tercile))
        if r.n == 0:
            continue
        lines.append(
            f"| {tercile} | {r.n} | {r.mean_a:.0%} | {r.mean_b:.0%} | "
            f"{r.diff:+.1%} | [{r.ci_low:+.1%}, {r.ci_high:+.1%}] |"
        )
    return "\n".join(lines)


def csv_rows(metrics: dict[str, RegimeMetrics]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["regime", "probe_tag", "kind", "bucket", "distance", "hit",
         "used_retrieval", "answer"]
    )
    for m in _ordered(metrics):
        for r in m.probe_results:
            writer.writerow(
                [m.name, r.probe.tag, r.probe.kind, r.probe.bucket,
                 r.probe.distance, int(r.hit), int(r.used_retrieval),
                 r.answer[:120]]
            )
    return buffer.getvalue()
