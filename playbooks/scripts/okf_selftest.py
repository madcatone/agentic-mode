#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fixture suite for okf_lint.py, run via ``okf_lint.py --selftest``.

Each case is a (label, bundle-relative path, document, expected rule IDs)
tuple. One clean concept proves legal forms parse without findings; every
rule ID has one case that must fire and only that rule. Pure stdlib.
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
    ("no frontmatter", "plain.md", "Plain text.\n", ["K1"]),
    ("empty type", "empty-type.md", "---\ntype:\n---\n", ["K1"]),
    ("bad status", "status.md", "---\ntype: T\nstatus: retired\n---\n", ["K7"]),
    ("bad timestamp", "ts.md", "---\ntype: T\nstale_after: 2026-12-31\n---\n", ["K4"]),
    ("bad actor", "actor.md",
     "---\ntype: T\ngenerated: { by: iri, at: 2026-01-01T00:00:00Z }\n---\n", ["K5"]),
    ("dangling footnote", "foot.md",
     "---\ntype: T\nsources:\n  - id: a\n    resource: r\n---\nX.[^b]\n\n[^b]: B\n",
     ["K6"]),
    ("count without window", "count.md",
     "---\ntype: T\nsources:\n  - resource: r\n    usage_count: 3\n---\n", ["K8"]),
    ("nested index frontmatter", "sub/index.md",
     '---\nokf_version: "0.2"\n---\n# L\n', ["K2"]),
    ("log not newest first", "sub/log.md",
     "# Log\n\n## 2026-05-01\n\n## 2026-05-02\n", ["K3"]),
]

ROOT_FILES = {
    "index.md": '---\nokf_version: "0.2"\n---\n# Tables\n',
    "log.md": "# Log\n\n## 2026-05-02\n",
}

def run(scan_bundle):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for _, rel, doc, _ in CASES:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(doc, encoding="utf-8")
        for name, doc in ROOT_FILES.items():
            (root / name).write_text(doc, encoding="utf-8")
        found = scan_bundle(root)
    failures = 0
    for label, rel, _, expected in CASES:
        got = sorted({f.split("[")[1].split("]")[0] for f in found
                      if f.startswith(rel + ":")})
        ok = got == sorted(set(expected))
        failures += 0 if ok else 1
        print("  %-4s %-24s expected %s, got %s"
              % ("PASS" if ok else "FAIL", label, sorted(set(expected)) or "clean",
                 got or "clean"))
    print("")
    print("okf_lint selftest: %d of %d cases passed"
          % (len(CASES) - failures, len(CASES)))
    return 1 if failures else 0
