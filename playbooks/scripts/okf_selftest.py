#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fixture suite for okf_lint.py, run via ``okf_lint.py --selftest``.

Each case is a (label, bundle-relative path, document, expected rule IDs)
tuple; a ``None`` document marks a fixture written by ``run`` itself. One
clean concept proves legal forms parse without findings; every rule ID has
one case that must fire and only that rule. Pure stdlib.
"""

import tempfile
from pathlib import Path

GOOD = (
    "---\n"
    "type: Warehouse Table\n"
    "status: stable\n"
    "generated: { by: catalog-agent/2.3, at: 2026-06-28T14:00:00Z }\n"
    "verified:\n"
    "  - { by: human:iri, at: 2026-06-25T09:00:00Z }\n"
    "stale_after: 2026-12-31T00:00:00Z\n"
    "sources:\n"
    "  - id: spec\n"
    "    resource: https://example.test/s\n"
    "    usage_count: 10\n"
    "usage_window: { from: 2026-06-01T00:00:00Z, to: 2026-06-30T00:00:00Z }\n"
    "---\nClaim.[^spec]\n\n[^spec]: Spec\n"
)

CASES = [
    ("good concept", "good.md", GOOD, []),
    ("extension keys parse", "ext.md", "---\ntype: T\ncom.example/knob: 1\n---\n", []),
    ("no frontmatter", "plain.md", "Plain text.\n", ["K1"]),
    ("empty type", "empty-type.md", "---\ntype:\n---\n", ["K1"]),
    ("bad status", "status.md", "---\ntype: T\nstatus: retired\n---\n", ["K7"]),
    ("bad timestamp", "ts.md", "---\ntype: T\nstale_after: 2026-12-31\n---\n", ["K4"]),
    ("bad last_modified stamp", "lm.md",
     "---\ntype: T\nsources:\n  - resource: r\n    last_modified: yesterday\n---\n",
     ["K4"]),
    ("bad actor", "actor.md",
     "---\ntype: T\ngenerated: { by: iri, at: 2026-01-01T00:00:00Z }\n---\n", ["K5"]),
    ("block verified mapping", "block-verified.md",
     "---\ntype: T\nverified:\n  by: iri\n  at: not-a-timestamp\n---\n",
     ["K4", "K5"]),
    ("dangling footnote", "foot.md",
     "---\ntype: T\nsources:\n  - id: a\n    resource: r\n---\nX.[^b]\n\n[^b]: B\n",
     ["K6"]),
    ("ghost footnote reference", "ghost.md",
     "---\ntype: T\nsources:\n  - id: a\n    resource: r\n---\nRef.[^ghost]\n",
     ["K6"]),
    ("count without window", "count.md",
     "---\ntype: T\nsources:\n  - resource: r\n    usage_count: 3\n---\n", ["K8"]),
    ("entry usage_window override", "entry-window.md",
     "---\ntype: T\nsources:\n  - resource: r\n    usage_count: 3\n"
     "    usage_window: { from: June, to: July }\n---\n", ["K4"]),
    ("nested index frontmatter", "sub/index.md",
     '---\nokf_version: "0.2"\n---\n# L\n', ["K2", "K3"]),
    ("root index extra keys", "root2/index.md", None, ["K2", "K3"]),
    ("unclosed flow mapping", "unclosed.md",
     "---\ntype: T\ngenerated: { by: agent/1, at: 2026-01-01T00:00:00Z\n---\n",
     ["K1"]),
    ("unclosed flow list", "unclosed-list.md",
     "---\ntype: T\ntags: [a, b\n---\n", ["K1"]),
    ("mismatched flow delimiters", "mismatch.md",
     "---\ntype: T\ntags: [a, b}\n---\n", ["K1"]),
    ("unterminated flow quote", "unterm-quote.md",
     '---\ntype: T\ngenerated: { by: "agent, at: 2026-01-01T00:00:00Z }\n---\n',
     ["K1"]),
    ("prose-only index body", "sub3/index.md", "# Just prose\n\nNo list here.\n",
     ["K3"]),
    ("mixed invalid index lines", "sub4/index.md",
     "# Section\n\nArbitrary prose, not a list.\n\n* [Only one](one.md)\n\nMore prose.\n",
     ["K3"]),
    ("log without date headings", "sub3/log.md", "# Log\n\nJust notes.\n", ["K3"]),
    ("non-bulleted log entry", "sub4/log.md",
     "# Log\n\n## 2026-05-02\n\nNot a bulleted entry.\n", ["K3"]),
    ("empty mapping value", "empty-val.md",
     "---\ntype: T\nsources:\n  - resource:\n---\n", []),
    ("scalar generated", "scalar-gen.md",
     "---\ntype: T\ngenerated: agent/1\n---\n", ["K5"]),
    ("scalar verified", "scalar-ver.md",
     "---\ntype: T\nverified: agent/1\n---\n", ["K5"]),
    ("non-mapping verified entry", "ver-item.md",
     "---\ntype: T\nverified:\n  - agent/1\n---\n", ["K5"]),
    ("non-string status", "status-list.md",
     "---\ntype: T\nstatus: [draft]\n---\n", ["K7"]),
    ("non-string actor", "actor-list.md",
     "---\ntype: T\ngenerated: { by: [agent], at: 2026-01-01T00:00:00Z }\n---\n",
     ["K5"]),
    ("non-string window stamp", "win-list.md",
     "---\ntype: T\nusage_window: { from: [x], to: 2026-01-01T00:00:00Z }\n---\n",
     ["K4"]),
    ("verified event without by", "verified-noby.md",
     "---\ntype: T\nverified:\n  - at: 2026-01-01T00:00:00Z\n---\n", ["K5"]),
    ("non-string stale_after", "stale-list.md",
     "---\ntype: T\nstale_after: [x]\n---\n", ["K4"]),
    ("impossible calendar date", "cal.md",
     "---\ntype: T\nstale_after: 2026-99-99T99:59:59Z\n---\n", ["K4"]),
    ("valid leap-day timestamp", "leap.md",
     "---\ntype: T\nstale_after: 2024-02-29T10:00:00Z\n---\n", []),
    ("closing-only flow scalar", "closer.md", "---\ntype: T\ntags: }\n---\n", ["K1"]),
    ("nested block mapping", "nested-map.md",
     "---\ntype: T\nextension:\n  nested:\n    key: 1\n---\n", []),
    ("footnote label in fence", "fence.md",
     "---\ntype: T\nsources:\n  - id: a\n    resource: r\n---\n```\nX.[^ghost]\n```\n",
     []),
    ("log not newest first", "sub/log.md",
     "# Log\n\n## 2026-05-01\n\n## 2026-05-02\n", ["K3"]),
    ("non-ISO log heading", "sub2/log.md", "# Log\n\n## not-a-date\n\n## 2026-05-02\n",
     ["K3"]),
]

ROOT_FILES = {
    "index.md": '---\nokf_version: "0.2"\n# a comment line\n---\n'
                "# Tables\n\n* [Good](good.md) - A good concept.\n",
    "log.md": "# Log\n\n## 2026-05-02\n\n* **Update**: Added Good.\n",
}

def run(scan_bundle):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for _, rel, doc, _ in CASES:
            if doc is None:
                continue
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(doc, encoding="utf-8")
        for name, doc in ROOT_FILES.items():
            (root / name).write_text(doc, encoding="utf-8")
        found = scan_bundle(root)
        root2 = root / "root2"
        root2.mkdir()
        (root2 / "index.md").write_text(
            '---\nokf_version: "0.2"\nextra: 1\n# comment\n---\n', encoding="utf-8")
        found += ["root2/" + f for f in scan_bundle(root2)]
    failures = 0
    for label, rel, _, expected in CASES:
        got = sorted({f.split("[")[1].split("]")[0] for f in found
                      if f.startswith(rel + ":")})
        ok = got == sorted(set(expected))
        failures += 0 if ok else 1
        print("  %-4s %-26s expected %s, got %s"
              % ("PASS" if ok else "FAIL", label, sorted(set(expected)) or "clean",
                 got or "clean"))
    print("")
    print("okf_lint selftest: %d of %d cases passed"
          % (len(CASES) - failures, len(CASES)))
    return 1 if failures else 0
