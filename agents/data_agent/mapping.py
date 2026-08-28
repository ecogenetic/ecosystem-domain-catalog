#!/usr/bin/env python3.14
"""Map a generated source ontology onto the catalog graph (no homonym collapse)."""

from __future__ import annotations

import json
from typing import Any

from agents.data_agent.introspect import INFRA
from agents.shared.catalog_index import get_index, local_name
from agents.shared.paths import source_dir

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
    "Interaction": ["cvm:CustomerEvent", "crm:Activity"],
}


def map_to_catalog(
    source_id: str,
    schema: dict[str, Any],
    prefer_domain: str | None = None,
    selections: dict[str, str] | None = None,
) -> dict[str, Any]:
    idx = get_index()
    selections = selections or {}
    mapped: list[dict[str, Any]] = []
    unmapped: list[dict[str, Any]] = []
    homonyms: list[dict[str, Any]] = []
    class_map: dict[str, dict[str, Any]] = {}

    for coll in schema.get("collections") or []:
        if coll.get("infrastructure") or coll["name"] in INFRA:
            continue
        entity = coll["entity"]
        candidates = _unique_candidates(_candidates(idx, entity, prefer_domain))
        chosen, ambiguity = _resolve_candidate(
            candidates,
            selected_iri=selections.get(entity),
            prefer_domain=prefer_domain,
        )
        if ambiguity:
            options = [
                {
                    "iri": c["iri"],
                    "domainId": c.get("domainId"),
                    "prefLabel": c.get("prefLabel") or local_name(c["iri"]),
                }
                for c in candidates
            ]
            homonyms.append(
                {
                    "entity": entity,
                    "collection": coll["name"],
                    "candidates": [c["iri"] for c in candidates],
                    "options": options,
                    "reason": ambiguity,
                }
            )
            unmapped.append(
                {
                    "entity": entity,
                    "collection": coll["name"],
                    "reason": ambiguity,
                    "candidates": [c["iri"] for c in candidates],
                }
            )
            continue
        if not chosen:
            unmapped.append({"entity": entity, "collection": coll["name"], "reason": "no_catalog_class"})
            continue
        entry = _mapped_entry(coll, chosen)
        mapped.append(entry)
        class_map[entity] = entry

    mapped = list(class_map.values())
    _resolve_joins(mapped)

    readiness = _mapping_readiness(mapped, unmapped, homonyms)
    mapping = {
        "sourceId": source_id,
        "mapped": mapped,
        "unmapped": unmapped,
        "homonyms": homonyms,
        "readiness": readiness,
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
        "readiness": readiness,
    }


def load_mapping(source_id: str) -> dict[str, Any]:
    path = source_dir(source_id) / "source.mapping.json"
    if not path.exists():
        return {
            "sourceId": source_id,
            "mapped": [],
            "unmapped": [],
            "homonyms": [],
            "readiness": _mapping_readiness([], [], []),
        }
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
    readiness = mapping.get("readiness") or _mapping_readiness(
        mapped,
        unmapped,
        mapping.get("homonyms") or [],
    )
    return {
        "ok": True,
        "coveragePct": round(pct, 2),
        "gaps": gaps,
        "mappedCount": len(mapped),
        "readiness": readiness,
    }


def heal_mapping(source_id: str, schema: dict[str, Any], collection: str | None = None) -> dict[str, Any]:
    mapping = load_mapping(source_id)
    idx = get_index()
    repaired = []
    still = []
    remaining = []
    collections = {item.get("name"): item for item in schema.get("collections") or []}
    for gap in mapping.get("unmapped") or []:
        if collection and gap.get("collection") != collection:
            remaining.append(gap)
            continue
        entity = gap.get("entity") or ""
        found = _unique_candidates(_candidates(idx, entity, None))
        chosen, ambiguity = _resolve_candidate(found, selected_iri=None, prefer_domain=None)
        if chosen:
            source_collection = collections.get(gap.get("collection"))
            if not source_collection:
                still.append({**gap, "reason": "source_collection_missing"})
                remaining.append({**gap, "reason": "source_collection_missing"})
                continue
            repaired.append({"entity": entity, "catalogIri": chosen["iri"]})
            mapping.setdefault("mapped", []).append(_mapped_entry(source_collection, chosen))
        else:
            if ambiguity:
                gap = {**gap, "reason": ambiguity, "candidates": [c["iri"] for c in found]}
            still.append(gap)
            remaining.append(gap)
    mapping["unmapped"] = remaining
    mapping["homonyms"] = [
        h for h in mapping.get("homonyms") or [] if h.get("entity") in {u.get("entity") for u in remaining}
    ]
    _resolve_joins(mapping.get("mapped") or [])
    mapping["classMap"] = {
        item["entity"]: item["catalogIri"] for item in mapping.get("mapped") or []
    }
    mapping["readiness"] = _mapping_readiness(
        mapping.get("mapped") or [],
        remaining,
        mapping.get("homonyms") or [],
    )
    path = source_dir(source_id) / "source.mapping.json"
    path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    ttl_path = source_dir(source_id) / "source.mapping.ttl"
    ttl_path.write_text(_mapping_ttl(source_id, mapping.get("mapped") or []), encoding="utf-8")
    return {
        "ok": True,
        "repaired": repaired,
        "stillUnmapped": still,
        "readiness": mapping["readiness"],
    }


def _mapped_entry(coll: dict[str, Any], chosen: dict[str, Any]) -> dict[str, Any]:
    properties = []
    joins = []
    enums = coll.get("enumsFromLookups") or {}
    temporal = []
    for field in coll.get("fields") or []:
        fname = field["name"]
        if fname in {"_id", "__v"}:
            continue
        if field.get("ref"):
            joins.append({"field": fname, "targetEntity": field["ref"]})
        if fname.lower().endswith("at") or "date" in fname.lower() or "time" in fname.lower():
            temporal.append(fname)
        properties.append(
            {
                "field": fname,
                "property": fname,
                "enums": enums.get(fname) or enums.get(fname.lower()),
            }
        )
    for name, values in enums.items():
        if not any(prop["field"] == name for prop in properties):
            properties.append({"field": name, "property": name, "enums": values})
    return {
        "entity": coll["entity"],
        "collection": coll["name"],
        "catalogIri": chosen["iri"],
        "catalogDomain": chosen.get("domainId"),
        "prefLabel": chosen.get("prefLabel"),
        "alignmentStatus": "catalog_aligned",
        "mappingRelation": "rdfs:subClassOf",
        "properties": properties,
        "joins": joins,
        "temporalFields": temporal,
        "enums": enums,
        "count": coll.get("count", 0),
    }


def _resolve_joins(mapped: list[dict[str, Any]]) -> None:
    class_map = {entry["entity"]: entry for entry in mapped}
    lower_map = {entity.lower(): entry for entity, entry in class_map.items()}
    for entry in mapped:
        for join in entry.get("joins") or []:
            target = class_map.get(join.get("targetEntity")) or lower_map.get(
                str(join.get("targetEntity") or "").lower()
            )
            if target:
                join["targetEntity"] = target["entity"]
                join["targetCollection"] = target["collection"]
                join["targetIri"] = target["catalogIri"]


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
        wanted = entity.strip().lower()
        exact_names = {
            local_name(m.get("iri") or "").strip().lower(),
            str(m.get("prefLabel") or "").strip().lower(),
            *{str(label).strip().lower() for label in m.get("altLabels") or []},
        }
        # Keep real homonyms, but exclude fuzzy neighbors such as
        # CustomerAccount, WorkOrder, and CampaignMember.
        if wanted not in exact_names:
            continue
        if m.get("iri") not in {f.get("iri") for f in found}:
            found.append(m)
    return found


def _unique_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in candidates:
        iri = candidate.get("iri") or ""
        if not iri or iri in seen:
            continue
        seen.add(iri)
        unique.append(candidate)
    return unique


def _resolve_candidate(
    candidates: list[dict[str, Any]],
    *,
    selected_iri: str | None,
    prefer_domain: str | None,
) -> tuple[dict[str, Any] | None, str | None]:
    if not candidates:
        return None, None
    if selected_iri:
        selected = next((c for c in candidates if c.get("iri") == selected_iri), None)
        if selected:
            return selected, None
        return None, "invalid_catalog_selection"
    if len(candidates) == 1:
        return candidates[0], None
    if prefer_domain:
        preferred = [c for c in candidates if c.get("domainId") == prefer_domain]
        if len(preferred) == 1:
            return preferred[0], None
    return None, "ambiguous_catalog_class"


def _mapping_readiness(
    mapped: list[dict[str, Any]],
    unmapped: list[dict[str, Any]],
    homonyms: list[dict[str, Any]],
) -> dict[str, Any]:
    unresolved_homonyms = {h.get("entity") for h in homonyms}
    ready = bool(mapped) and not unmapped and not unresolved_homonyms
    unmatched = [
        item
        for item in unmapped
        if item.get("reason") not in {"ambiguous_catalog_class", "invalid_catalog_selection"}
    ]
    return {
        "status": "ready" if ready else "needs_review",
        "readyForQuery": ready,
        "catalogAligned": len(mapped),
        "unresolved": len(unmatched),
        "ambiguous": len(unresolved_homonyms),
    }


def _mapping_ttl(source_id: str, mapped: list[dict[str, Any]]) -> str:
    ns = f"https://ecosystemcode.com/ontology/source/{source_id}#"
    lines = [
        f"@prefix src: <{ns}> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "",
        "# Generated matches are catalog alignments, not extensional equivalence assertions.",
        "# They become executable only after every ambiguity and mapping gap is resolved.",
        "",
    ]
    for m in mapped:
        iri = m["catalogIri"]
        lines.append(f"src:{m['entity']} rdfs:subClassOf <{iri}> .")
        for prop in m.get("properties") or []:
            field = prop["field"]
            if field.startswith("_"):
                continue
            lines.append(f"src:{m['entity']}_{field} rdfs:subPropertyOf src:{field} .")
    return "\n".join(lines) + "\n"
