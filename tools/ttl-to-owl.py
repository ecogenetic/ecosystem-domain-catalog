#!/usr/bin/env python3.14
"""Regenerate domain ontology.owl (and optional shapes/mappings) from canonical .ttl.

Ensures RDF/XML companions contain owl:Ontology + owl:Class metadata and stay
graph-isomorphic to Turtle. Used when tooling rejects flat/incomplete .owl files.

Usage:
  ./tools/ttl-to-owl.py domains/crm/ontology.ttl
  ./tools/ttl-to-owl.py --domain crm
  ./tools/ttl-to-owl.py --domain crm --domain cvm --all-companions
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD
from rdflib.namespace import SKOS

ROOT = Path(__file__).resolve().parents[1]
SH = Namespace("http://www.w3.org/ns/shacl#")
BFO = Namespace("http://purl.obolibrary.org/obo/BFO_")


def bind_common(g: Graph, domain_id: str | None) -> None:
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("skos", SKOS)
    g.bind("sh", SH)
    g.bind("bfo", BFO)
    if domain_id:
        ns = Namespace(f"https://ecosystemcode.com/ontology/{domain_id}#")
        g.bind("", ns)
        g.bind(domain_id, ns)


def counts(g: Graph) -> dict[str, int]:
    return {
        "triples": len(g),
        "Ontology": len(list(g.subjects(RDF.type, OWL.Ontology))),
        "Class": len(list(g.subjects(RDF.type, OWL.Class))),
        "ObjectProperty": len(list(g.subjects(RDF.type, OWL.ObjectProperty))),
        "DatatypeProperty": len(list(g.subjects(RDF.type, OWL.DatatypeProperty))),
        "domain": len(list(g.triples((None, RDFS.domain, None)))),
        "range": len(list(g.triples((None, RDFS.range, None)))),
    }


def convert_ttl_to_owl(ttl_path: Path, owl_path: Path | None = None, fmt: str = "pretty-xml") -> dict:
    if not ttl_path.exists():
        raise FileNotFoundError(ttl_path)
    owl_path = owl_path or ttl_path.with_suffix(".owl")
    domain_id = None
    parts = ttl_path.parts
    if "domains" in parts:
        i = parts.index("domains")
        if i + 1 < len(parts):
            domain_id = parts[i + 1]

    # shapes with RDF lists must use plain xml to avoid rdflib pretty-xml dropping list nodes
    if ttl_path.name.startswith("shapes") or ttl_path.name == "shapes.ttl":
        fmt = "xml"

    src = Graph()
    src.parse(ttl_path, format="turtle")
    bind_common(src, domain_id)

    src_counts = counts(src)
    if "ontology" in ttl_path.name and src_counts["Ontology"] < 1:
        raise SystemExit(f"{ttl_path}: Turtle is missing owl:Ontology metadata")
    if "ontology" in ttl_path.name and src_counts["Class"] < 1:
        raise SystemExit(f"{ttl_path}: Turtle has no owl:Class declarations")

    data = src.serialize(format=fmt, encoding="utf-8")
    text = data.decode("utf-8") if isinstance(data, bytes) else data
    if not text.lstrip().startswith("<?xml"):
        text = '<?xml version="1.0" encoding="utf-8"?>\n' + text
    if not text.endswith("\n"):
        text += "\n"
    owl_path.write_text(text, encoding="utf-8")

    check = Graph()
    check.parse(owl_path, format="xml")
    if not src.isomorphic(check):
        raise SystemExit(
            f"{owl_path}: regenerated OWL is NOT isomorphic to TTL "
            f"(ttl={src_counts} owl={counts(check)})"
        )

    out_counts = counts(check)
    if "ontology" in ttl_path.name:
        if out_counts["Ontology"] < 1 or out_counts["Class"] < 1:
            raise SystemExit(
                f"{owl_path}: RDF parse error: No ontology metadata or OWL classes found "
                f"in the RDF document. counts={out_counts}"
            )
        if out_counts["ObjectProperty"] != src_counts["ObjectProperty"]:
            raise SystemExit(
                f"{owl_path}: ObjectProperty count mismatch "
                f"ttl={src_counts['ObjectProperty']} owl={out_counts['ObjectProperty']}"
            )
        if out_counts["domain"] != src_counts["domain"] or out_counts["range"] != src_counts["range"]:
            raise SystemExit(
                f"{owl_path}: domain/range relationship mismatch "
                f"ttl=({src_counts['domain']},{src_counts['range']}) "
                f"owl=({out_counts['domain']},{out_counts['range']})"
            )

    print(f"OK {owl_path.relative_to(ROOT)}  {out_counts}")
    return out_counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ttl_files", nargs="*", type=Path, help="Turtle files to convert")
    parser.add_argument("--domain", action="append", default=[], help="Domain id (e.g. crm)")
    parser.add_argument(
        "--all-companions",
        action="store_true",
        help="Also convert shapes.ttl and mappings/*.ttl for selected domains",
    )
    args = parser.parse_args()

    targets: list[Path] = list(args.ttl_files)
    for domain in args.domain:
        base = ROOT / "domains" / domain
        targets.append(base / "ontology.ttl")
        if args.all_companions:
            targets.append(base / "shapes.ttl")
            mappings = base / "mappings"
            if mappings.is_dir():
                targets.extend(sorted(mappings.glob("*.ttl")))

    if not targets:
        parser.error("Provide ttl paths and/or --domain")

    for ttl in targets:
        path = ttl if ttl.is_absolute() else (ROOT / ttl if not ttl.exists() else ttl)
        if not path.exists() and not ttl.is_absolute():
            path = ROOT / ttl
        convert_ttl_to_owl(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
