#!/usr/bin/env python3.14
"""Generate an internal OWL/SKOS ontology from an introspected schema."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.shared.paths import source_dir


def generate_ontology(source_id: str, schema: dict[str, Any]) -> dict[str, Any]:
    ns = f"https://ecosystemcode.com/ontology/source/{source_id}#"
    ont_iri = f"https://ecosystemcode.com/ontology/source/{source_id}"
    lines = [
        f"@prefix : <{ns}> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "",
        f"<{ont_iri}> a owl:Ontology ;",
        f'    rdfs:label "Source ontology for {source_id}" ;',
        f'    rdfs:comment "Generated from database collections, samples, and lookups." .',
        "",
    ]
    classes = []
    for coll in schema.get("collections") or []:
        if coll.get("infrastructure"):
            continue
        entity = coll["entity"]
        classes.append(entity)
        label = _label(entity)
        definition = f"Record type inferred from collection {coll['name']}."
        lines += [
            f":{entity} a owl:Class ;",
            f'    skos:prefLabel "{label}" ;',
            f'    skos:altLabel "{coll["name"]}" ;',
            f'    skos:definition "{definition}" .',
            "",
        ]
        for field in coll.get("fields") or []:
            fname = _safe(field["name"])
            if fname in {"id", "_id"}:
                continue
            if field.get("ref"):
                lines += [
                    f":{entity}_{fname} a owl:ObjectProperty ;",
                    f'    rdfs:label "{_label(fname)}" ;',
                    f"    rdfs:domain :{entity} ;",
                    f"    rdfs:range :{field['ref']} ;",
                    f'    skos:definition "Join field {field["name"]} on {coll["name"]}." .',
                    "",
                ]
            else:
                rtype = "xsd:dateTime" if "date" in "".join(field.get("types") or []).lower() or fname.lower().endswith("at") else "xsd:string"
                if "int" in (field.get("types") or []) or "float" in (field.get("types") or []):
                    rtype = "xsd:decimal"
                lines += [
                    f":{entity}_{fname} a owl:DatatypeProperty ;",
                    f'    rdfs:label "{_label(fname)}" ;',
                    f"    rdfs:domain :{entity} ;",
                    f"    rdfs:range {rtype} ;",
                    f'    skos:prefLabel "{_label(fname)}" ;',
                    f'    skos:definition "Field {field["name"]} on {coll["name"]}." .',
                    "",
                ]
        for enum_field, values in (coll.get("enumsFromLookups") or {}).items():
            fname = _safe(enum_field)
            joined = ", ".join(values[:12])
            lines += [
                f":{entity}_{fname} a owl:DatatypeProperty ;",
                f'    rdfs:label "{_label(fname)}" ;',
                f"    rdfs:domain :{entity} ;",
                f"    rdfs:range xsd:string ;",
                f'    skos:prefLabel "{_label(fname)}" ;',
                f'    skos:definition "Enumerated field {enum_field} with values: {joined}." .',
                "",
            ]
    dest = source_dir(source_id) / "source.ontology.ttl"
    dest.write_text("\n".join(lines), encoding="utf-8")
    return {
        "ok": True,
        "ontologyIri": ont_iri,
        "turtlePath": str(dest),
        "classCount": len(classes),
        "classes": classes,
    }


def validate_source_ontology(source_id: str) -> dict[str, Any]:
    path = source_dir(source_id) / "source.ontology.ttl"
    if not path.exists():
        return {"ok": False, "error": "missing_ontology", "missingLabels": [], "missingDefs": []}
    from rdflib.namespace import OWL, RDF, RDFS, SKOS
    from agents.shared.rdf_parse import parse_rdf_graph

    g = parse_rdf_graph(path=path)
    missing_labels = []
    missing_defs = []
    for cls in g.subjects(RDF.type, OWL.Class):
        if not list(g.objects(cls, SKOS.prefLabel)) and not list(g.objects(cls, RDFS.label)):
            missing_labels.append(str(cls))
        if not list(g.objects(cls, SKOS.definition)):
            missing_defs.append(str(cls))
    return {
        "ok": not missing_labels and not missing_defs,
        "missingLabels": missing_labels,
        "missingDefs": missing_defs,
        "warnings": [],
    }


def _label(name: str) -> str:
    import re

    parts = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    parts = parts.replace("_", " ")
    return parts.strip()[:1].upper() + parts.strip()[1:]


def _safe(name: str) -> str:
    import re

    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if cleaned.startswith("_"):
        cleaned = "id" + cleaned
    return cleaned
