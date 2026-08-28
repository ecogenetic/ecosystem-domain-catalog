#!/usr/bin/env python3.14
"""Map a generated source ontology onto the catalog graph (no homonym collapse)."""

from __future__ import annotations

import json
import re
from typing import Any

from rdflib import URIRef
from rdflib.namespace import OWL, RDFS

from agents.data_agent.introspect import INFRA
from agents.shared.catalog_index import get_index, local_name
from agents.shared.paths import CATALOG_ROOT, source_dir
from agents.shared.rdf_parse import parse_rdf_graph

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

_GENERIC_CACHE: dict[str, dict[str, Any]] = {}


def map_to_catalog(
    source_id: str,
    schema: dict[str, Any],
    prefer_domain: str | None = None,
    selections: dict[str, str] | None = None,
) -> dict[str, Any]:
    idx = get_index()
    selections = selections or {}
    generic_hints = _load_generic_mapping(prefer_domain) if prefer_domain else {"classes": {}, "properties": {}}
    mapped: list[dict[str, Any]] = []
    unmapped: list[dict[str, Any]] = []
    homonyms: list[dict[str, Any]] = []
    class_map: dict[str, dict[str, Any]] = {}

    for coll in schema.get("collections") or []:
        if coll.get("infrastructure") or coll["name"] in INFRA:
            continue
        entity = coll["entity"]
        candidates = _unique_candidates(
            _candidates(idx, entity, prefer_domain, generic_hints, coll.get("name") or "")
        )
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
        entry = _mapped_entry(coll, chosen, idx, generic_hints)
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
        "genericMappingDomain": prefer_domain,
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
    prop_total = 0
    prop_mapped = 0
    for m in mapped:
        props = m.get("properties") or []
        if not props and not m.get("joins"):
            gaps.append({"entity": m["entity"], "reason": "no_properties"})
        for p in props:
            prop_total += 1
            if p.get("propertyIri") or p.get("mapped"):
                prop_mapped += 1
            else:
                gaps.append({"entity": m["entity"], "field": p.get("field"), "reason": "no_catalog_property"})
    prop_pct = (prop_mapped / prop_total * 100) if prop_total else 0.0
    readiness = mapping.get("readiness") or _mapping_readiness(
        mapped,
        unmapped,
        mapping.get("homonyms") or [],
    )
    return {
        "ok": True,
        "coveragePct": round(pct, 2),
        "propertyCoveragePct": round(prop_pct, 2),
        "gaps": gaps,
        "mappedCount": len(mapped),
        "readiness": readiness,
    }


def heal_mapping(source_id: str, schema: dict[str, Any], collection: str | None = None) -> dict[str, Any]:
    mapping = load_mapping(source_id)
    prefer = mapping.get("genericMappingDomain")
    for m in mapping.get("mapped") or []:
        if m.get("catalogDomain"):
            prefer = prefer or m["catalogDomain"]
            break
    idx = get_index()
    generic_hints = _load_generic_mapping(prefer) if prefer else {"classes": {}, "properties": {}}
    repaired = []
    still = []
    remaining = []
    collections = {item.get("name"): item for item in schema.get("collections") or []}
    for gap in mapping.get("unmapped") or []:
        if collection and gap.get("collection") != collection:
            remaining.append(gap)
            continue
        entity = gap.get("entity") or ""
        found = _unique_candidates(
            _candidates(idx, entity, prefer, generic_hints, gap.get("collection") or "")
        )
        chosen, ambiguity = _resolve_candidate(found, selected_iri=None, prefer_domain=prefer)
        if chosen:
            source_collection = collections.get(gap.get("collection"))
            if not source_collection:
                still.append({**gap, "reason": "source_collection_missing"})
                remaining.append({**gap, "reason": "source_collection_missing"})
                continue
            repaired.append({"entity": entity, "catalogIri": chosen["iri"]})
            mapping.setdefault("mapped", []).append(_mapped_entry(source_collection, chosen, idx, generic_hints))
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


def _mapped_entry(
    coll: dict[str, Any],
    chosen: dict[str, Any],
    idx: Any,
    generic_hints: dict[str, Any],
) -> dict[str, Any]:
    properties = []
    joins = []
    enums = coll.get("enumsFromLookups") or {}
    temporal = []
    catalog_iri = chosen["iri"]
    for field in coll.get("fields") or []:
        fname = field["name"]
        if fname in {"_id", "__v"}:
            continue
        if field.get("ref"):
            joins.append({"field": fname, "targetEntity": field["ref"]})
        if fname.lower().endswith("at") or "date" in fname.lower() or "time" in fname.lower():
            temporal.append(fname)
        prop_iri = _map_property(idx, catalog_iri, fname, field.get("ref"), generic_hints)
        properties.append(
            {
                "field": fname,
                "property": local_name(prop_iri) if prop_iri else fname,
                "propertyIri": prop_iri,
                "mapped": bool(prop_iri),
                "enums": enums.get(fname) or enums.get(fname.lower()),
            }
        )
    for name, values in enums.items():
        if not any(prop["field"] == name for prop in properties):
            prop_iri = _map_property(idx, catalog_iri, name, None, generic_hints)
            properties.append(
                {
                    "field": name,
                    "property": local_name(prop_iri) if prop_iri else name,
                    "propertyIri": prop_iri,
                    "mapped": bool(prop_iri),
                    "enums": values,
                }
            )
    mapped_props = sum(1 for p in properties if p.get("mapped"))
    return {
        "entity": coll["entity"],
        "collection": coll["name"],
        "catalogIri": catalog_iri,
        "catalogDomain": chosen.get("domainId"),
        "prefLabel": chosen.get("prefLabel"),
        "alignmentStatus": "catalog_aligned",
        "mappingRelation": "rdfs:subClassOf",
        "properties": properties,
        "propertyCoveragePct": round((mapped_props / len(properties) * 100) if properties else 0.0, 2),
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


def _load_generic_mapping(domain_id: str | None, industry: str | None = None) -> dict[str, Any]:
    if not domain_id:
        return {"classes": {}, "properties": {}}
    key = f"{domain_id}:{industry or ''}"
    if key in _GENERIC_CACHE:
        return _GENERIC_CACHE[key]
    paths = [CATALOG_ROOT / "domains" / domain_id / "mappings" / "generic-mapping.ttl"]
    if industry:
        paths.append(
            CATALOG_ROOT / "domains" / domain_id / "industries" / industry / "mappings" / "generic-mapping.ttl"
        )
    classes: dict[str, str] = {}
    properties: dict[str, str] = {}
    for path in paths:
        if not path.exists():
            continue
        g = parse_rdf_graph(path=path)
        for s, o in g.subject_objects(OWL.equivalentClass):
            if not isinstance(s, URIRef) or not isinstance(o, URIRef):
                continue
            src = local_name(str(s))
            classes[src.lower()] = str(o)
            classes[_camel_to_snake(src).lower()] = str(o)
            if src.endswith("_table"):
                stem = src[: -len("_table")]
                classes[stem.lower()] = str(o)
                for form in _entity_search_terms(_snake_to_pascal(stem)):
                    classes[form.lower()] = str(o)
                    classes[_camel_to_snake(form).lower()] = str(o)
        for s, o in g.subject_objects(RDFS.subPropertyOf):
            if not isinstance(s, URIRef) or not isinstance(o, URIRef):
                continue
            src = local_name(str(s))
            properties[src.lower()] = str(o)
            properties[_camel_to_snake(src).lower()] = str(o)
            # strip common table/entity prefixes: account_name, contact_full_name
            parts = src.split("_")
            if len(parts) >= 2:
                properties["_".join(parts[1:]).lower()] = str(o)
    out = {"classes": classes, "properties": properties}
    _GENERIC_CACHE[key] = out
    return out


def _candidates(
    idx,
    entity: str,
    prefer_domain: str | None,
    generic_hints: dict[str, Any] | None = None,
    collection: str = "",
) -> list[dict[str, Any]]:
    hints = EXPLICIT.get(entity) or []
    found: list[dict[str, Any]] = []
    for hint in hints:
        prefix, name = hint.split(":")
        iri = f"https://ecosystemcode.com/ontology/{prefix}#{name}"
        doc = idx.get_concept(iri)
        if doc.get("ok"):
            found.append(doc)
    generic_hints = generic_hints or {}
    for key in (
        collection,
        entity,
        *_entity_search_terms(entity),
        f"{collection}_table",
        f"{_camel_to_snake(entity)}_table",
    ):
        if not key:
            continue
        hint_iri = (generic_hints.get("classes") or {}).get(str(key).lower())
        if hint_iri:
            doc = idx.get_concept(hint_iri)
            if doc.get("ok") and doc.get("iri") not in {f.get("iri") for f in found}:
                found.append(doc)
    for term in _entity_search_terms(entity):
        search = idx.search(term, domain=prefer_domain, limit=8)
        for m in search.get("matches") or []:
            if m.get("kind") not in {"class", "overlay_class"}:
                continue
            wanted = term.strip().lower()
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


def _map_property(
    idx: Any,
    class_iri: str,
    field: str,
    ref_entity: str | None,
    generic_hints: dict[str, Any],
) -> str | None:
    variants = _field_variants(field)
    for v in variants:
        hint = (generic_hints.get("properties") or {}).get(v)
        if hint:
            return hint
    domain_id = (idx.get_concept(class_iri) or {}).get("domainId")
    kind = "object_property" if ref_entity else "datatype_property"
    for v in variants:
        token = v.replace("_id", "").replace("_", "")
        if len(token) < 2:
            continue
        hits = idx.search(v if "_" in v else token, domain=domain_id, limit=8)
        for m in hits.get("matches") or []:
            if m.get("kind") != kind and m.get("kind") not in {"object_property", "datatype_property"}:
                continue
            if kind == "object_property" and m.get("kind") != "object_property":
                continue
            if kind == "datatype_property" and m.get("kind") != "datatype_property":
                continue
            extra = m.get("extra") or {}
            domains = extra.get("domain") or []
            if domains and class_iri not in domains:
                continue
            ln = local_name(m.get("iri") or "").lower()
            if ln in variants or _camel_to_snake(ln) in variants:
                return m["iri"]
            if v.replace("_", "") == ln.replace("_", ""):
                return m["iri"]
    return None


def _field_variants(field: str) -> set[str]:
    variants = {field, field.lower(), _camel_to_snake(field)}
    if field.endswith("_id"):
        variants.add(field[:-3])
        variants.add(field[:-3].replace("_", ""))
    if field.endswith("Id") and len(field) > 2:
        stem = field[:-2]
        variants.add(stem)
        variants.add(_camel_to_snake(stem))
    # account_name <-> accountName
    if "_" in field:
        parts = field.split("_")
        variants.add(parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:]))
    return {v.lower() for v in variants if v}


def _entity_search_terms(entity: str) -> list[str]:
    """Exact labels plus a conservative singular form for plural table names."""
    terms = [entity]
    if entity.endswith("ies") and len(entity) > 3:
        terms.append(entity[:-3] + "y")
    elif entity.endswith("ses") and len(entity) > 3:
        terms.append(entity[:-2])
    elif entity.endswith("s") and len(entity) > 1 and not entity.endswith("ss"):
        terms.append(entity[:-1])
    out: list[str] = []
    seen: set[str] = set()
    for t in terms:
        key = t.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


def _camel_to_snake(name: str) -> str:
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name or "").replace("-", "_").lower()


def _snake_to_pascal(name: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in re.split(r"[_\-]+", name or "") if p)


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
            prop_iri = prop.get("propertyIri")
            if prop_iri:
                lines.append(f"src:{m['entity']}_{field} rdfs:subPropertyOf <{prop_iri}> .")
            else:
                lines.append(f"src:{m['entity']}_{field} rdfs:subPropertyOf src:{field} .")
    return "\n".join(lines) + "\n"
