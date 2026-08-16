#!/usr/bin/env python3.14
"""Map a generated source ontology onto the catalog graph (no homonym collapse)."""

from __future__ import annotations

import json
from typing import Any

from agents.data_agent.introspect import INFRA
from agents.shared.catalog_index import get_index, local_name
from agents.shared.paths import source_dir

PREFERRED_DOMAINS = ("core", "crm", "oms", "ecom", "cvm", "pim")

EXPLICIT = {
    "Customer": ["core:Customer", "cvm:Customer", "crm:Customer"],
    "Order": ["core:Order", "oms:SalesOrder"],
    "OrderLine": ["core:OrderLine"],
    "Product": ["core:Product", "pim:Product", "cvm:Product"],
    "Campaign": ["crm:Campaign", "cvm:Campaign"],
    "Offer": ["cvm:Offer"],
    "Segment": ["cvm:Segment"],
    "Lead": ["crm:Lead"],
    "Consent": ["crm:ConsentRecord"],
    "Channel": ["cvm:Channel"],
    "Event": ["cvm:CustomerEvent"],
}


def map_to_catalog(source_id: str, schema: dict[str, Any], prefer_domain: str | None = None) -> dict[str, Any]:
    idx = get_index()
    mapped: list[dict[str, Any]] = []
    unmapped: list[dict[str, Any]] = []
    homonyms: list[dict[str, Any]] = []
    class_map: dict[str, dict[str, Any]] = {}

    for coll in schema.get("collections") or []:
        if coll.get("infrastructure") or coll["name"] in INFRA:
            continue
        entity = coll["entity"]
        candidates = _candidates(idx, entity, prefer_domain)
        domains = {c.get("domainId") for c in candidates if c.get("domainId")}
        if len(domains) > 1 and not prefer_domain:
            # keep distinct; pick preferred domain if present else first with note
            chosen = _prefer(candidates, prefer_domain)
            homonyms.append({"entity": entity, "candidates": [c["iri"] for c in candidates]})
        else:
            chosen = _prefer(candidates, prefer_domain)
        if not chosen:
            unmapped.append({"entity": entity, "collection": coll["name"], "reason": "no_catalog_class"})
            continue
        properties = []
        joins = []
        enums = coll.get("enumsFromLookups") or {}
        temporal = []
        for field in coll.get("fields") or []:
            fname = field["name"]
            if fname in {"_id", "__v"}:
                continue
            if field.get("ref"):
                joins.append(
                    {
                        "field": fname,
                        "targetEntity": field["ref"],
                    }
                )
            if fname.lower().endswith("at") or "date" in fname.lower() or "time" in fname.lower():
                temporal.append(fname)
            properties.append(
                {
                    "field": fname,
                    "property": fname,
                    "enums": enums.get(fname) or enums.get(fname.lower()),
                }
            )
        for ename, values in enums.items():
            if not any(p["field"] == ename for p in properties):
                properties.append({"field": ename, "property": ename, "enums": values})

        entry = {
            "entity": entity,
            "collection": coll["name"],
            "catalogIri": chosen["iri"],
            "catalogDomain": chosen.get("domainId"),
            "prefLabel": chosen.get("prefLabel"),
            "properties": properties,
            "joins": joins,
            "temporalFields": temporal,
            "enums": enums,
            "count": coll.get("count", 0),
        }
        mapped.append(entry)
        class_map[entity] = entry

    mapped = list(class_map.values())
    for entry in mapped:
        for join in entry["joins"]:
            target = class_map.get(join["targetEntity"])
            if not target:
                # try case-insensitive
                for k, v in class_map.items():
                    if k.lower() == join["targetEntity"].lower():
                        target = v
                        break
            if target:
                join["targetCollection"] = target["collection"]
                join["targetIri"] = target["catalogIri"]

    mapping = {
        "sourceId": source_id,
        "mapped": mapped,
        "unmapped": unmapped,
        "homonyms": homonyms,
        "classMap": {k: v["catalogIri"] for k, v in class_map.items()},
    }
    dest = source_dir(source_id)
    json_path = dest / "source.mapping.json"
    json_path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    ttl_path = dest / "source.mapping.ttl"
    ttl_path.write_text(_mapping_ttl(source_id, mapped), encoding="utf-8")
    return {
        "ok": True,
        "mappingPath": str(json_path),
        "ttlPath": str(ttl_path),
        "mapped": mapped,
        "unmapped": unmapped,
        "homonyms": homonyms,
    }


def load_mapping(source_id: str) -> dict[str, Any]:
    path = source_dir(source_id) / "source.mapping.json"
    if not path.exists():
        return {"sourceId": source_id, "mapped": [], "unmapped": [], "homonyms": []}
    return json.loads(path.read_text(encoding="utf-8"))


def mapping_coverage(source_id: str) -> dict[str, Any]:
    mapping = load_mapping(source_id)
    mapped = mapping.get("mapped") or []
    unmapped = mapping.get("unmapped") or []
    total = len(mapped) + len(unmapped)
    pct = (len(mapped) / total * 100) if total else 0.0
    gaps = [{"entity": u.get("entity"), "reason": u.get("reason")} for u in unmapped]
    for m in mapped:
        if not m.get("joins") and not m.get("properties"):
            gaps.append({"entity": m["entity"], "reason": "no_properties"})
    return {"ok": True, "coveragePct": round(pct, 2), "gaps": gaps, "mappedCount": len(mapped)}


def heal_mapping(source_id: str, schema: dict[str, Any], collection: str | None = None) -> dict[str, Any]:
    mapping = load_mapping(source_id)
    idx = get_index()
    repaired = []
    still = []
    remaining = []
    for gap in mapping.get("unmapped") or []:
        if collection and gap.get("collection") != collection:
            remaining.append(gap)
            continue
        entity = gap.get("entity") or ""
        found = _candidates(idx, entity, None)
        chosen = _prefer(found, None) or (found[0] if found else None)
        if chosen:
            repaired.append({"entity": entity, "catalogIri": chosen["iri"]})
            mapping.setdefault("mapped", []).append(
                {
                    "entity": entity,
                    "collection": gap.get("collection"),
                    "catalogIri": chosen["iri"],
                    "catalogDomain": chosen.get("domainId"),
                    "properties": [],
                    "joins": [],
                    "temporalFields": [],
                    "enums": {},
                }
            )
        else:
            still.append(gap)
            remaining.append(gap)
    mapping["unmapped"] = remaining
    path = source_dir(source_id) / "source.mapping.json"
    path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    return {"ok": True, "repaired": repaired, "stillUnmapped": still}


def _candidates(idx, entity: str, prefer_domain: str | None) -> list[dict[str, Any]]:
    hints = EXPLICIT.get(entity) or []
    found: list[dict[str, Any]] = []
    for hint in hints:
        prefix, name = hint.split(":")
        iri = f"https://ecosystemcode.com/ontology/{prefix}#{name}"
        doc = idx.get_concept(iri)
        if doc.get("ok"):
            found.append(doc)
    search = idx.search(entity, domain=prefer_domain, limit=8)
    for m in search.get("matches") or []:
        if m.get("kind") not in {"class", "overlay_class"}:
            continue
        if local_name(m.get("iri") or "").lower() != entity.lower() and entity.lower() not in (m.get("prefLabel") or "").lower():
            if entity.lower() not in [a.lower() for a in m.get("altLabels") or []]:
                continue
        if m.get("iri") not in {f.get("iri") for f in found}:
            found.append(m)
    return found


def _prefer(candidates: list[dict[str, Any]], prefer_domain: str | None) -> dict[str, Any] | None:
    if not candidates:
        return None
    order = ([prefer_domain] if prefer_domain else []) + list(PREFERRED_DOMAINS)
    for dom in order:
        for c in candidates:
            if c.get("domainId") == dom:
                return c
    return candidates[0]


def _mapping_ttl(source_id: str, mapped: list[dict[str, Any]]) -> str:
    ns = f"https://ecosystemcode.com/ontology/source/{source_id}#"
    lines = [
        f"@prefix src: <{ns}> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "",
    ]
    for m in mapped:
        iri = m["catalogIri"]
        lines.append(f"src:{m['entity']} owl:equivalentClass <{iri}> .")
        for prop in m.get("properties") or []:
            field = prop["field"]
            if field.startswith("_"):
                continue
            lines.append(f"src:{m['entity']}_{field} rdfs:subPropertyOf src:{field} .")
    return "\n".join(lines) + "\n"
