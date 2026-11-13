#!/usr/bin/env python3.14
"""Deep ontology & SHACL validator for ecosystem-domain-catalog.

Usage:
  ./tools/validate-ontology.py --catalog
  ./tools/validate-ontology.py path/to/custom.ttl --shapes path/to/shapes.ttl --json
  ./tools/validate-ontology.py --catalog --remote   # use ONTOLOGY_VALIDATION_SERVER

Honors ONTOLOGY_VALIDATION_SERVER when --remote is passed. Offline mode uses
pyoxigraph + rdflib local checks compatible with AGENTS.md SHACL/SKOS rules.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

NODE_SHAPE = re.compile(r":(\w+)\s+a\s+sh:NodeShape\b")
TARGET_CLASS = re.compile(r"sh:targetClass\s+(?:\S*?[:#])?(\w+)")
SH_PATH = re.compile(r"sh:path\s+(?:\S*?[:#])?(\w+)")
OWL_CLASS = re.compile(r":(\w+)\s+a\s+owl:Class\b")
OBJ_PROP = re.compile(r":(\w+)\s+a\s+owl:ObjectProperty\b")
DATA_PROP = re.compile(r":(\w+)\s+a\s+owl:DatatypeProperty\b")
SH_OR = re.compile(r"sh:or\s*\(")
SH_IN = re.compile(r"sh:in\s*\(([^)]*)\)")
VERSION_DIR = re.compile(r"(?i)(?:VERSION|@version)\s+\"([^\"]+)\"")


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def validate_file(ontology_text: str, shapes_text: str = "", source: str = "file") -> dict:
    issues: list[dict] = []
    recommendations: list[dict] = []
    features: list[dict] = []

    if VERSION_DIR.search(ontology_text or ""):
        features.append({"ruleId": "SYN-004", "detail": "VERSION"})
    if "<<" in (ontology_text or ""):
        features.append({"ruleId": "SYN-005", "detail": "triple-term"})
    if re.search(r"@[A-Za-z]{2,8}(?:-[A-Za-z0-9]+)*--(?:ltr|rtl)\b", ontology_text or ""):
        features.append({"ruleId": "SYN-006", "detail": "directional-lang"})

    classes = set(OWL_CLASS.findall(ontology_text or ""))
    obj_props = set(OBJ_PROP.findall(ontology_text or ""))
    data_props = set(DATA_PROP.findall(ontology_text or ""))
    props = obj_props | data_props

    if not ontology_text.strip():
        issues.append(
            {
                "ruleId": "SYN-009",
                "aspect": "syntax",
                "severity": "error",
                "message": f"{source}: empty ontology",
            }
        )
    if "owl:Ontology" not in (ontology_text or ""):
        issues.append(
            {
                "ruleId": "OWL-001",
                "aspect": "owl_skos",
                "severity": "error",
                "message": f"{source}: missing owl:Ontology header",
            }
        )
        recommendations.append(
            {
                "id": "rec-owl-header",
                "ruleId": "OWL-001",
                "category": "owl_skos",
                "severity": "error",
                "title": "Add owl:Ontology header",
                "suggestedTtl": '<https://example.org/ontology#> a owl:Ontology ;\n    rdfs:label "Domain Ontology" .',
                "autoApplicable": True,
            }
        )

    shapes = shapes_text or ""
    if "sh:NodeShape" in (ontology_text or "") and not shapes:
        shapes = ontology_text
    targets = set(TARGET_CLASS.findall(shapes))
    shape_names = set(NODE_SHAPE.findall(shapes))
    paths = set(SH_PATH.findall(shapes))

    if not shape_names and not targets:
        issues.append(
            {
                "ruleId": "SHACL-001",
                "aspect": "shacl",
                "severity": "error",
                "message": f"{source}: no sh:NodeShape declarations",
            }
        )
    for t in targets:
        if t not in classes:
            issues.append(
                {
                    "ruleId": "SHACL-002",
                    "aspect": "shacl",
                    "severity": "error",
                    "message": f"{source}: sh:targetClass :{t} not declared as owl:Class",
                    "subject": t,
                }
            )
    for p in paths:
        if p not in props and f":{p} " not in (ontology_text or ""):
            issues.append(
                {
                    "ruleId": "SHACL-003",
                    "aspect": "shacl",
                    "severity": "error",
                    "message": f"{source}: sh:path :{p} not declared as a property",
                    "subject": p,
                }
            )
    if SH_OR.search(shapes):
        features.append({"ruleId": "SHACL-008", "detail": "sh:or"})
    if SH_IN.search(shapes):
        features.append({"ruleId": "SHACL-005", "detail": "sh:in"})

    # Try parse with oxigraph/rdflib when available
    try:
        from agents.shared.rdf_parse import parse_rdf_graph

        g = parse_rdf_graph(data=ontology_text)
        features.append({"ruleId": "SYN-010", "detail": f"triples={len(g) if g is not None else 0}"})
    except Exception as exc:
        issues.append(
            {
                "ruleId": "SYN-002",
                "aspect": "syntax",
                "severity": "error",
                "message": f"{source}: parse error: {exc}",
            }
        )

    errors = sum(1 for i in issues if i.get("severity") == "error")
    warnings = sum(1 for i in issues if i.get("severity") == "warning")
    return {
        "ok": errors == 0,
        "source": source,
        "format": "ttl",
        "serviceVersion": "catalog-local-1.0.0",
        "issues": issues,
        "recommendations": recommendations,
        "detectedFeatures": features,
        "validationSummary": {
            "classCount": len(classes),
            "objectPropertyCount": len(obj_props),
            "datatypePropertyCount": len(data_props),
            "shaclNodeShapeCount": len(shape_names),
            "conforms": errors == 0,
            "rdfVersion": "1.2" if VERSION_DIR.search(ontology_text or "") else "1.1",
        },
        "summary": {
            "errors": errors,
            "warnings": warnings,
            "suggestions": 0,
            "info": 0,
            "passed": errors == 0,
        },
    }


def validate_overlay_add_only(base_ont: str, overlay: str, source: str) -> list[dict]:
    """Overlays must not redefine base classes/properties (add-only).

    Detects redeclarations that use a non-default prefix of an imported base term
    as ``prefix:Class a owl:Class`` (same local name as a base ``:Class``).
    New overlay-local ``:NewClass`` declarations are allowed.
    """
    issues: list[dict] = []
    if not overlay.strip():
        return issues
    base_classes = set(OWL_CLASS.findall(base_ont))
    # e.g. crm:Account a owl:Class in an overlay = redefinition of base Account
    imported = re.findall(r"(?<!:)(\w+):(\w+)\s+a\s+owl:Class\b", overlay)
    for prefix, cls in imported:
        if prefix in {"owl", "rdfs", "rdf", "xsd", "skos", "sh", "bfo"}:
            continue
        if cls in base_classes:
            issues.append(
                {
                    "ruleId": "OWL-001",
                    "aspect": "owl_skos",
                    "severity": "error",
                    "message": f"{source}: overlay redefines base class {prefix}:{cls} (add-only violation)",
                    "subject": cls,
                }
            )
    return issues


def validate_catalog(root: Path, use_remote: bool = False) -> dict:
    index = json.loads((root / "index.json").read_text(encoding="utf-8"))
    reports = []
    all_ok = True
    for entry in index.get("domains", []):
        did = entry["id"]
        ont = _load(root / "domains" / did / "ontology.ttl")
        shapes = _load(root / "domains" / did / "shapes.ttl")
        if use_remote:
            try:
                from agents.shared.validation_client import validate_ontology as remote_validate

                report = remote_validate(
                    ontology_content=ont,
                    shapes_content=shapes,
                    domain_id=None,
                    include_recommendations=False,
                )
                report["source"] = f"domains/{did}"
            except Exception as exc:
                report = validate_file(ont, shapes, source=f"domains/{did}")
                report["remoteError"] = str(exc)
        else:
            report = validate_file(ont, shapes, source=f"domains/{did}")

        for ind in entry.get("industries") or []:
            overlay = _load(root / "domains" / did / "industries" / ind / "overlay.ttl")
            for issue in validate_overlay_add_only(ont, overlay, f"domains/{did}/industries/{ind}/overlay.ttl"):
                report.setdefault("issues", []).append(issue)
                if issue.get("severity") == "error":
                    report["ok"] = False
                    report.setdefault("summary", {})["errors"] = report["summary"].get("errors", 0) + 1
                    report["summary"]["passed"] = False

        reports.append({"domainId": did, "report": report})
        if not report.get("ok", False):
            all_ok = False

    # core — shared vocabulary has no shapes.ttl; check OWL/syntax only (skip SHACL-001)
    core_ont = _load(root / "core" / "ontology.ttl")
    core_align = _load(root / "core" / "alignments.ttl")
    if core_ont:
        core_report = validate_file(core_ont + "\n" + core_align, "# no shapes", source="core")
        # Filter SHACL-001 noise for core (by design core has no NodeShapes)
        core_report["issues"] = [
            i for i in core_report.get("issues", [])
            if i.get("ruleId") != "SHACL-001"
        ]
        errors = sum(1 for i in core_report["issues"] if i.get("severity") == "error")
        core_report["ok"] = errors == 0
        core_report["summary"] = {
            **core_report.get("summary", {}),
            "errors": errors,
            "passed": errors == 0,
        }
        reports.append({"domainId": "core", "report": core_report})
        if not core_report.get("ok", False):
            all_ok = False

    return {
        "ok": all_ok,
        "validationSource": "remote" if use_remote else "local",
        "validationServer": os.environ.get("ONTOLOGY_VALIDATION_SERVER", "http://localhost:3001"),
        "domains": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate catalog / ontology Turtle for RDF 1.2, OWL, SKOS, SHACL")
    parser.add_argument("path", nargs="?", help="Path to a single .ttl/.owl file")
    parser.add_argument("--shapes", help="Optional shapes.ttl path")
    parser.add_argument("--catalog", action="store_true", help="Validate entire catalog")
    parser.add_argument("--remote", action="store_true", help="Use ONTOLOGY_VALIDATION_SERVER")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument("--root", default=str(ROOT), help="Catalog root")
    args = parser.parse_args()

    root = Path(args.root)

    if args.catalog or (not args.path):
        result = validate_catalog(root, use_remote=args.remote)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            errors = 0
            for row in result.get("domains", []):
                rep = row["report"]
                errs = rep.get("summary", {}).get("errors", 0)
                status = "PASS" if rep.get("ok") else "FAIL"
                print(f"  {status}: {row['domainId']} ({errs} error(s))")
                errors += errs
            print("OK" if result.get("ok") else f"FAILED ({errors} error(s))")
        return 0 if result.get("ok") else 1

    ont = _load(Path(args.path))
    shapes = _load(Path(args.shapes)) if args.shapes else ""
    if args.remote:
        from agents.shared.validation_client import validate_ontology as remote_validate

        result = remote_validate(ontology_content=ont, shapes_content=shapes or None)
    else:
        result = validate_file(ont, shapes, source=args.path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("PASS" if result.get("ok") else "FAIL")
        for issue in result.get("issues", []):
            print(f"  [{issue.get('severity')}] {issue.get('ruleId')}: {issue.get('message')}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
